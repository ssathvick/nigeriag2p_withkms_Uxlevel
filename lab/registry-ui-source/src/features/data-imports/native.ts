import 'server-only';
import { Pool } from 'pg';
import { stringify } from 'csv-stringify/sync';
import { NextRequest } from 'next/server';
import { GET as getPermissions } from '@/app/api/permissions/route';
import { GET as getIdentity } from '@/app/api/me/route';
import { POST as getTemplates } from '@/app/api/input-mechanism/get-import-file-configuration/route';
import { proxyToBackend } from '@/app/api/_lib/backend-proxy';
import { getBackendConfig } from '@/app/api/_lib/backend-config';
import { createBackendRequest } from '@/app/api/_lib/backend-request';
import { requireAuth } from '@/app/api/_lib/requireAuth';
import { importRoles, mapRows, type Batch, type ImportRole } from './model';

export class ImportError extends Error {
    constructor(message: string, public status = 400) { super(message); }
}

export type Actor = { id: string; name: string; role: ImportRole };

export async function actor(req: NextRequest): Promise<Actor> {
    const response = await getIdentity(req);
    if (!response.ok) throw new ImportError('Sign in with an authorized Registry account.', response.status);
    const profile = await response.json();
    if (!importRoles.includes(profile.registry_scope)) throw new ImportError('Your Registry role does not have access to Data Imports.', 403);
    const token = req.cookies.get('X-Access-Token')!.value;
    const claims = JSON.parse(Buffer.from(token.split('.')[1], 'base64url').toString());
    if (typeof claims.sub !== 'string' || !claims.sub) throw new ImportError('The session has no Registry identity.', 401);
    return { id: claims.sub, name: profile.name || claims.preferred_username || claims.sub, role: profile.registry_scope };
}

export async function requireNativeTransferPermission(req: NextRequest) {
    const response = await getPermissions(req);
    if (!response.ok) throw new ImportError('Registry transfer permissions could not be checked.', 503);
    const applications = await response.json();
    if (!Array.isArray(applications) || !applications.some(app => Array.isArray(app.permissions) && app.permissions.includes('intakeSubmission:edit'))) {
        throw new ImportError('Your Registry role does not have permission to transfer files.', 403);
    }
}

function post(req: NextRequest, body: FormData | Record<string, unknown>) {
    const headers = new Headers(req.headers);
    headers.delete('content-type');
    headers.delete('content-length');
    if (!(body instanceof FormData)) headers.set('content-type', 'application/json');
    return new NextRequest(req.url, { method: 'POST', headers, body: body instanceof FormData ? body : JSON.stringify(body) });
}

type ImportTemplate = {
    import_file_configuration_id: string;
    import_file_template_description: string;
    import_file_template_mnemonic: string;
    data_model_id: string;
    form_id: string;
    register_id: string;
};

export async function templates(req: NextRequest, registerId: string): Promise<ImportTemplate[]> {
    // The deployed catalog API ties template reads to intake writes. Registry
    // administrators can manage mappings with the read-only catalog connection.
    if (process.env.DATA_IMPORTS_DOCUMENT_REFERENCE === 'catalog' && process.env.DATA_IMPORTS_NATIVE_READ_URL) {
        return (await pool().query<ImportTemplate>(`
            SELECT import_file_configuration_id, import_file_template_description,
                   import_file_template_mnemonic, data_model_id, form_id, register_id
            FROM g2p_registry_import_file_configurations WHERE register_id = $1
            ORDER BY import_file_template_mnemonic LIMIT 100
        `, [registerId])).rows;
    }
    const response = await getTemplates(post(req, { register_id: registerId, page_size: 100 }));
    if (!response.ok) throw new ImportError('Registry templates could not be loaded. Check the destination and your access.', 422);
    const data = await response.json();
    return data.import_file_configurations ?? [];
}

export async function storeFile(req: NextRequest, batch: Batch) {
    const { included } = mapRows(batch.source, batch.columns, batch.rows);
    const contents = stringify([batch.source.fields.map(field => field.name), ...included.map(row => row.mapped)]);
    const form = new FormData();
    form.set('document_label', 'import_file');
    form.set('bucket', 'data_import_files');
    form.set('documents', new File([contents], `import-${batch.id}.csv`, { type: 'text/csv' }));
    const result = await proxyToBackend({
        req: post(req, form), targetEndpoint: '/documents/upload_documents',
        transformResponse: body => body?.response_payload?.documents ?? body?.response_payload?.uploaded_documents ?? [],
        caching: { signal: AbortSignal.timeout(15000) },
    });
    if (!result.ok) throw new ImportError('Registry document upload failed. The file was not queued.', 502);
    const [document] = await result.json();
    const reference = process.env.DATA_IMPORTS_DOCUMENT_REFERENCE === 'catalog' ? document?.document_id : document?.document_store_id;
    if (!reference) throw new ImportError('Registry did not return a document reference. The file was not queued.', 502);
    return String(reference);
}

export async function enqueue(req: NextRequest, batch: Batch, template: Awaited<ReturnType<typeof templates>>[number]) {
    const auth = requireAuth(req);
    if (!('backendHeaders' in auth)) throw new ImportError('Your session expired.', 401);
    const payload = createBackendRequest({
        pagination_request: { current_page: 1, page_size: 20, sort_by: '', search_text: '' },
        request_payload: {
            [process.env.DATA_IMPORTS_DOCUMENT_REFERENCE === 'catalog' ? 'document_id' : 'document_store_id']: batch.documentId,
            data_model_id: template.data_model_id,
            register_id: batch.source.registerId, intake_form_id: template.form_id,
        },
    }, process.env.APP_ORIGIN || req.nextUrl.origin);
    const response = await fetch(`${getBackendConfig().backendApiUrl}/input-mechanism-data/enqueue_import_file`, {
        method: 'POST', headers: auth.backendHeaders, body: JSON.stringify(payload),
        cache: 'no-store', signal: AbortSignal.timeout(15000),
    });
    const result = await response.json();
    if (response.status === 401 || response.status === 403 || ['G2P-AUT-401', 'G2P-AUT-403'].includes(result.response_header?.response_error_code)) {
        throw new ImportError('The Registry denied permission to queue the file.', 403);
    }
    if (!response.ok || result.response_header?.response_status !== 'SUCCESS') {
        throw new ImportError('The Registry did not confirm the queue request.', 502);
    }
    const data = result.response_body?.response_payload;
    return typeof data?.import_file_id === 'string' ? data.import_file_id : undefined;
}

type Receipt = { id: string; status: string; found: number | null; ingested: number | null; attempts: number | null; records: number[] };
let nativePool: Pool | undefined;
let documentColumn: 'document_id' | 'document_store_id' | undefined;

function pool() {
    nativePool ??= new Pool({
        connectionString: process.env.DATA_IMPORTS_NATIVE_READ_URL, max: 3,
        connectionTimeoutMillis: 3000, statement_timeout: 4000,
    });
    return nativePool;
}

export function trackingConfigured() {
    return Boolean(process.env.DATA_IMPORTS_NATIVE_READ_URL || (process.env.DATA_IMPORTS_LOCAL_PREVIEW === '1'
        && getBackendConfig().backendApiUrl === 'http://127.0.0.1:3101'));
}

export async function receipt(req: NextRequest, documentId: string): Promise<Receipt | undefined> {
    if (process.env.DATA_IMPORTS_NATIVE_READ_URL) {
        const nativePool = pool();
        if (!documentColumn) {
            const columns = await nativePool.query<{ attname: string }>(`
                SELECT attname FROM pg_attribute
                WHERE attrelid = 'import_file_process_queue'::regclass AND NOT attisdropped
            `);
            documentColumn = columns.rows.some(column => column.attname === 'document_store_id') ? 'document_store_id' : 'document_id';
        }
        const result = await nativePool.query<Receipt>(`
            SELECT import_file_id::text AS id, intake_form_ingestion_status::text AS status,
                   number_of_records_present AS found, number_of_records_ingested AS ingested,
                   intake_form_ingestion_attempts AS attempts,
                   ARRAY(SELECT DISTINCT l.record_number::int FROM import_file_process_log l
                         WHERE l.import_file_id = q.import_file_id ORDER BY 1) AS records
            FROM import_file_process_queue q WHERE q.${documentColumn} = $1
            ORDER BY queued_at DESC LIMIT 1
        `, [documentId]);
        return result.rows[0];
    }
    // The loopback fixture supplies synthetic receipts through the mocked Registry API.
    if (process.env.DATA_IMPORTS_LOCAL_PREVIEW === '1' && getBackendConfig().backendApiUrl === 'http://127.0.0.1:3101') {
        const auth = requireAuth(req);
        if (!('backendHeaders' in auth)) throw new ImportError('Your session expired.', 401);
        const response = await fetch(`http://127.0.0.1:3101/preview/receipt/${encodeURIComponent(documentId)}`, {
            headers: auth.backendHeaders, cache: 'no-store', signal: AbortSignal.timeout(4000),
        });
        if (!response.ok) throw new ImportError('The preview receipt is unavailable.', 502);
        return (await response.json()) ?? undefined;
    }
    throw new ImportError('Registry tracking is not configured.', 503);
}
