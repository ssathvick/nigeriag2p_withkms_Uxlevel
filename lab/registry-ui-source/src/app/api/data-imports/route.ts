import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'node:crypto';
import { z } from 'zod';
import { actor, enqueue, ImportError, receipt, requireNativeTransferPermission, storeFile, templates, trackingConfigured, type Actor } from '@/features/data-imports/native';
import { batchById, batches, saveBatch, saveSource, sourceById, sources } from '@/features/data-imports/store';
import { limits, mapRows, transferFilters, type Batch, type Status } from '@/features/data-imports/model';
import { connectorChoices, fetchSourceFile } from '@/features/data-imports/connectors';
import { readImport } from '@/features/data-imports/read-file';

export const runtime = 'nodejs';

const version = z.number().int().positive();
const id = z.uuid();
const sourceSchema = z.object({
    id: id.optional(), version: version.optional(),
    name: z.string().trim().min(1).max(100), templateId: z.string().min(1).max(100), registerId: z.string().min(1).max(100),
    active: z.boolean(), connectorId: z.string().regex(/^[a-z0-9_-]{1,50}$/).optional(), key: z.string().min(1).max(100),
    fields: z.array(z.object({
        name: z.string().trim().regex(/^[A-Za-z0-9][A-Za-z0-9_. -]{0,99}$/),
        column: z.string().trim().min(1).max(100), required: z.boolean(),
        transform: z.enum(['none', 'trim', 'upper', 'lower']),
    })).min(1).max(limits.columns),
});
const batchAction = z.discriminatedUnion('action', [
    z.object({ action: z.literal('edit'), id, version, line: z.number().int().positive(),
        values: z.array(z.string().max(limits.cell).refine(value => !value.includes('\0'))).max(limits.columns), excluded: z.boolean() }),
    z.object({ action: z.enum(['review', 'approve', 'transfer', 'refresh']), id, version }),
    z.object({ action: z.literal('return'), id, version, note: z.string().trim().min(1).max(500) }),
]);

function json(data: unknown, status = 200) {
    return NextResponse.json(data, { status, headers: { 'Cache-Control': 'no-store, private' } });
}

async function handle(req: NextRequest, run: (who: Actor) => Promise<NextResponse>) {
    if (!process.env.DATA_IMPORTS_DB) return json({ error: 'Data Imports is unavailable for this Registry.' }, 503);
    try {
        return await run(await actor(req));
    } catch (error) {
        if (error instanceof ImportError) return json({ error: error.message }, error.status);
        if (error instanceof z.ZodError || error instanceof SyntaxError) return json({ error: 'Check the values you entered and try again.' }, 400);
        return json({ error: 'Data Imports is temporarily unavailable.' }, 502);
    }
}

function visibleBatch(batchId: string, who: Actor) {
    const batch = batchById(id.parse(batchId));
    if (!batch || (who.role === 'field' && batch.owner !== who.id) || (who.role === 'level1' && batch.status === 'draft')) {
        throw new ImportError('This batch was not found.', 404);
    }
    return batch;
}

function record(batch: Batch, who: Actor, status: Status, action: string, note?: string) {
    const { version } = batch;
    const next = { ...batch, status, version: version + 1, events: [...batch.events, {
        at: new Date().toISOString(), actor: who.name, action, note,
    }] };
    if (!saveBatch(next, version)) throw new ImportError('This batch changed. Reload it and try again.', 409);
    return next;
}

function requireRole(condition: boolean) {
    if (!condition) throw new ImportError('Your role cannot perform this action for the current batch.', 403);
}

function reviewable(batch: Batch) {
    const check = mapRows(batch.source, batch.columns, batch.rows);
    if (check.missing.length || !check.included.length || check.included.some(row => row.issues.length)) {
        throw new ImportError('Resolve the validation issues or exclude affected rows before requesting approval.', 422);
    }
}

function uploadLimit(declared: number, max: number) {
    if (!Number.isSafeInteger(declared) || declared <= 0 || declared > max) throw new ImportError('The upload exceeds the allowed size.', 413);
}

async function boundedBody(req: NextRequest, maximum: number) {
    if (!req.body) throw new ImportError('Request body required.');
    const reader = req.body.getReader();
    const chunks: Uint8Array[] = [];
    let size = 0;
    try {
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            size += value.byteLength;
            if (size > maximum) throw new ImportError('The upload exceeds the allowed size.', 413);
            chunks.push(value);
        }
        uploadLimit(size, maximum);
        return new Response(Buffer.concat(chunks), { headers: { 'content-type': req.headers.get('content-type') || '' } });
    } catch (error) {
        await reader.cancel().catch(() => undefined);
        throw error;
    } finally {
        reader.releaseLock();
    }
}

export async function GET(req: NextRequest) {
    return handle(req, async who => {
        const query = req.nextUrl.searchParams;
        const batchId = query.get('id');
        const registerId = query.get('templates');
        if (batchId) return json(visibleBatch(batchId, who));
        if (registerId) {
            requireRole(who.role === 'admin');
            return json(await templates(req, z.string().min(1).max(100).parse(registerId)));
        }
        const page = z.coerce.number().int().min(0).max(10000).parse(query.get('page') || '0');
        const filter = z.enum(['all', 'review', 'attention', 'sent']).parse(query.get('filter') || 'all');
        const { records, counts } = batches(who.role === 'field' ? who.id : null, who.role === 'level1', transferFilters[filter].statuses, page * 20);
        return json({
            batches: records.slice(0, 20), counts,
            sources: sources().filter(source => source.active || who.role === 'admin'), hasNext: records.length > 20,
            connectors: who.role === 'admin' ? connectorChoices() : [],
            preview: process.env.DATA_IMPORTS_LOCAL_PREVIEW === '1',
        });
    });
}

async function transfer(req: NextRequest, batch: Batch, who: Actor) {
    requireRole((who.role === 'admin' || batch.owner === who.id) && ['approved', 'retry'].includes(batch.status));
    reviewable(batch);
    if (!trackingConfigured()) throw new ImportError('Registry tracking must be configured before transferring records.', 503);
    await requireNativeTransferPermission(req);
    const configured = (await templates(req, batch.source.registerId))
        .find(item => item.import_file_configuration_id === batch.source.templateId && item.register_id === batch.source.registerId);
    if (!configured) throw new ImportError('The approved destination template is no longer available.', 422);
    let sending = record(batch, who, 'sending', 'Transfer started');
    let started = false;
    try {
        if (!sending.documentId) {
            const documentId = await storeFile(req, sending);
            sending = record({ ...sending, documentId }, who, 'sending', 'Document stored at Registry');
        }
        started = true;
        const nativeId = await enqueue(req, sending, configured);
        return record({ ...sending, nativeId }, who, 'queued', 'Registry accepted the queue request');
    } catch (error) {
        if (error instanceof ImportError && error.status === 409) throw error;
        const safe = !started || (error instanceof ImportError && error.status === 403);
        return record(sending, who, safe ? 'retry' : 'unconfirmed', safe ? 'Transfer blocked before queueing' : 'Registry queue receipt could not be confirmed',
            error instanceof ImportError ? error.message : undefined);
    }
}

async function refresh(req: NextRequest, batch: Batch, who: Actor) {
    if (!['sending', 'unconfirmed', 'queued', 'partial', 'failed', 'received'].includes(batch.status)) return batch;
    const elapsed = Date.now() - Date.parse(batch.events.at(-1)!.at);
    if (batch.status === 'sending' && elapsed < 90_000) return batch;
    if (!batch.documentId) {
        return batch.status === 'sending' ? record(batch, who, 'retry', 'Interrupted before queueing') : batch;
    }
    const native = await receipt(req, batch.documentId);
    if (!native) {
        return batch.status === 'sending' ? record(batch, who, 'unconfirmed', 'Interrupted during transfer. Check the Registry receipt before retrying.') : batch;
    }
    const state = String(native.status ?? 'pending').toLowerCase();
    const submitted = mapRows(batch.source, batch.columns, batch.rows).included;
    const nativeRows = (native.records ?? []).map(number => submitted[number - 1]?.line).filter(line => line !== undefined);
    const found = native.found ?? submitted.length;
    const ingested = nativeRows.length || (native.ingested ?? undefined);
    const attempts = native.attempts ?? undefined;
    const status: Status = found === submitted.length && ingested === submitted.length ? 'received'
        : ['success', 'completed', 'processed', 'ingested', 'partial', 'failed', 'error', 'rejected'].includes(state)
            ? (ingested && ingested > 0 ? 'partial' : 'failed') : 'queued';
    if (batch.status === status && batch.nativeStatus === state && batch.ingested === ingested && batch.found === found && batch.attempts === attempts && JSON.stringify(batch.nativeRows) === JSON.stringify(nativeRows)) return batch;
    return record({ ...batch, nativeId: native.id, nativeStatus: state, found, ingested, attempts, nativeRows }, who, status, 'Registry receipt reconciled');
}

async function createBatch(source: NonNullable<ReturnType<typeof sourceById>>, file: File, who: Actor, origin: string) {
    let input;
    try { input = await readImport(file); } catch (error) {
        throw new ImportError(error instanceof Error ? error.message : 'The spreadsheet could not be read.', 422);
    }
    const batch: Batch = {
        ...input, id: randomUUID(), version: 1, owner: who.id, ownerName: who.name,
        fileName: file.name.slice(0, 180), source, status: 'draft',
        events: [{ at: new Date().toISOString(), actor: who.name, action: origin }],
    };
    saveBatch(batch, 0);
    return json(batch, 201);
}

export async function POST(req: NextRequest) {
    return handle(req, async who => {
        if (req.headers.get('content-type')?.startsWith('multipart/form-data')) {
            requireRole(who.role === 'field' || who.role === 'admin');
            const form = await (await boundedBody(req, limits.file + 8192)).formData();
            const source = sourceById(id.parse(form.get('source')));
            const file = form.get('file');
            if (!source?.active || !(file instanceof File)) throw new ImportError('Choose an active source and a file.');
            return createBatch(source, file, who, 'File uploaded and validated');
        }
        const body = await (await boundedBody(req, 160000)).json();
        if (body?.action === 'fetch-source') {
            requireRole(who.role === 'field' || who.role === 'admin');
            const source = sourceById(id.parse(body.sourceId));
            if (!source?.active || !source.connectorId) throw new ImportError('Choose an active connected source.');
            return createBatch(source, await fetchSourceFile(source.connectorId), who, 'Source API file received and validated');
        }
        if (body?.action === 'source') {
            requireRole(who.role === 'admin');
            const value = sourceSchema.parse(body);
            if (!!value.id !== !!value.version) throw new ImportError('Reload this source and try again.', 409);
            const { version: previous = 0, id: sourceId = randomUUID(), ...config } = value;
            if (new Set(config.fields.map(field => field.name.toLowerCase())).size !== config.fields.length
                || !config.fields.some(field => field.name === config.key && field.required)) {
                throw new ImportError('Use unique destination fields and select a required duplicate-check key.', 422);
            }
            if (config.connectorId && !connectorChoices().some(item => item.id === config.connectorId)) {
                throw new ImportError('Choose an available source connection.', 422);
            }
            const valid = (await templates(req, config.registerId)).some(template => template.import_file_configuration_id === config.templateId && template.register_id === config.registerId);
            if (!valid) throw new ImportError('Choose an available Registry template.', 422);
            const source = { id: sourceId, version: previous + 1, ...config };
            if (!saveSource(source, previous)) throw new ImportError('This source changed. Reload it and try again.', 409);
            return json(source);
        }
        const action = batchAction.parse(body);
        const batch = visibleBatch(action.id, who);
        if (action.version !== batch.version) throw new ImportError('This batch changed. Reload it and try again.', 409);
        const canEdit = batch.owner === who.id && ['draft', 'returned'].includes(batch.status);
        switch (action.action) {
            case 'edit': {
                requireRole(canEdit);
                const row = batch.rows.find(item => item.line === action.line);
                if (!row || action.values.length !== batch.columns.length) throw new ImportError('The record does not match this batch.');
                Object.assign(row, { values: action.values, excluded: action.excluded });
                return json(record(batch, who, batch.status, action.excluded ? `Row ${row.line} excluded` : `Row ${row.line} saved`));
            }
            case 'review':
                requireRole(canEdit);
                reviewable(batch);
                return json(record(batch, who, 'review', 'Submitted for independent approval'));
            case 'approve':
            case 'return':
                requireRole(who.role === 'level1' && batch.owner !== who.id && batch.status === 'review');
                if (!('note' in action)) {
                    reviewable(batch);
                    return json(record(batch, who, 'approved', 'Batch approved'));
                }
                return json(record(batch, who, 'returned', 'Batch returned for correction', action.note));
            case 'transfer': return json(await transfer(req, batch, who));
            case 'refresh': return json(await refresh(req, batch, who));
        }
    });
}
