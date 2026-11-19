import { createServer } from 'node:http';
import { randomBytes, randomUUID, timingSafeEqual } from 'node:crypto';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawn } from 'node:child_process';
import { DatabaseSync } from 'node:sqlite';
import { parse } from 'csv-parse/sync';

const app = 'http://127.0.0.1:3100';
const base = 'http://127.0.0.1:3101';
const dir = join(tmpdir(), 'nsipa-data-imports-preview');
mkdirSync(dir, { recursive: true, mode: 0o700 });
const accountPath = join(dir, 'credentials.json');
const nativeRoles = {
    operator: 'Registry Field Agent', approver: 'Registry First Reviewer', administrator: 'Registry Administrator',
};
let passwords;
try {
    passwords = JSON.parse(readFileSync(accountPath, 'utf8'));
} catch (error) {
    if (error.code !== 'ENOENT') throw error;
    passwords = Object.fromEntries(Object.keys(nativeRoles).map(role => [role, randomBytes(15).toString('base64url')]));
    writeFileSync(accountPath, JSON.stringify(passwords, null, 2), { flag: 'wx', mode: 0o600 });
}
const database = join(dir, 'imports.sqlite');
const db = new DatabaseSync(database);
db.exec(`
    PRAGMA journal_mode = WAL;
    CREATE TABLE IF NOT EXISTS import_sources (id TEXT PRIMARY KEY, version INTEGER NOT NULL, payload TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS preview_documents (id TEXT PRIMARY KEY, rows TEXT NOT NULL, owner TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS preview_transient (reference TEXT PRIMARY KEY);
    CREATE TABLE IF NOT EXISTS preview_receipts (document TEXT PRIMARY KEY, payload TEXT NOT NULL, committed INTEGER NOT NULL);
`);
const register = { register_id: 'fixture-individual', register_mnemonic: 'individual', register_subject: 'Individual Registry', register_description: 'Local preview' };
const template = {
    import_file_configuration_id: 'fixture-csv', register_id: register.register_id, form_id: 'fixture-intake', data_model_id: 'fixture-model',
    import_file_template_description: 'Synthetic beneficiary file template', import_file_template_mnemonic: 'fixture-file',
};
const source = {
    id: 'fd178eb0-5827-4afe-86c5-a85a2fe43d54', version: 1, name: 'Sample beneficiary list', registerId: register.register_id,
    templateId: template.import_file_configuration_id, active: true, key: 'reference',
    fields: [
        { name: 'reference', column: 'Referral ID', required: true, transform: 'upper' },
        { name: 'full_name', column: 'Full Name', required: true, transform: 'trim' },
        { name: 'state', column: 'State', required: true, transform: 'trim' },
    ],
};
db.prepare('INSERT OR IGNORE INTO import_sources (id, version, payload) VALUES (?, 1, ?)').run(source.id, JSON.stringify(source));
const connected = { ...source, id: '33e980ca-4e08-4db2-a1a1-218da5218a7b', name: 'Sample connected source', connectorId: 'sample-api' };
db.prepare('INSERT OR IGNORE INTO import_sources (id, version, payload) VALUES (?, 1, ?)').run(connected.id, JSON.stringify(connected));
const sessions = new Map();

function respond(res, status, body) {
    res.writeHead(status, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
    res.end(JSON.stringify(body));
}

function backend(res, payload) {
    respond(res, 200, { response_header: { response_status: 'SUCCESS' }, response_body: { response_payload: payload } });
}

async function request(req) {
    return new Request(base + req.url, { method: req.method, headers: req.headers, body: req, duplex: 'half' });
}

function same(a, b) {
    const left = Buffer.from(a || '');
    const right = Buffer.from(b || '');
    return left.length === right.length && timingSafeEqual(left, right);
}

const sample = 'Referral ID,Full Name,State\r\nDEMO-001,Synthetic Person One,Lagos\r\nDEMO-001,Synthetic Person Two,Oyo\r\nDEMO-003,,Kano\r\nFAIL-004,Synthetic Person Four,FCT\r\n';
const server = createServer(async (req, res) => {
    try {
        const url = new URL(req.url, base);
        const path = url.pathname;
        if (path === '/preview/logout') {
            res.writeHead(303, { Location: base + '/preview/sign-in', 'Set-Cookie': 'X-Access-Token=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax' }).end();
            return;
        }
        if (path === '/preview/source.csv') {
            if (req.headers.authorization !== 'Bearer local-fixture-only') return respond(res, 403, {});
            res.writeHead(200, { 'Content-Type': 'text/csv' }).end('Referral ID,Full Name,State\r\nAPI-100,Synthetic Connected Person,Lagos\r\n');
            return;
        }
        if (path === '/preview/sample.csv') {
            res.writeHead(200, { 'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename="synthetic-beneficiary-list.csv"' }).end(sample);
            return;
        }
        if (path === '/preview/sign-in') {
            let wrong = false;
            if (req.method === 'POST') {
                if (req.headers.origin !== base) return respond(res, 403, { error: 'Use the preview sign-in form.' });
                const fields = new URLSearchParams(await (await request(req)).text());
                const role = fields.get('username');
                if (Object.hasOwn(nativeRoles, role) && same(fields.get('password'), passwords[role])) {
                    const claims = Buffer.from(JSON.stringify({
                        sub: 'preview-' + role, preferred_username: role,
                        resource_access: { 'register-staff-portal': { roles: [nativeRoles[role]] } },
                    })).toString('base64url');
                    const token = 'preview.' + claims + '.' + randomBytes(32).toString('base64url');
                    sessions.set(token, { role, expires: Date.now() + 8 * 3600 * 1000 });
                    res.writeHead(303, { Location: app + '/en/data-imports', 'Set-Cookie': `X-Access-Token=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=28800` }).end();
                    return;
                }
                wrong = true;
            }
            res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
            res.end(`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Data Imports preview sign-in</title><style>
            *{box-sizing:border-box}body{margin:0;background:#edf3e8;color:#193f36;font:16px system-ui}main{max-width:455px;margin:10vh auto;background:white;border:1px solid #dce6dd;padding:30px;border-radius:18px}h1{margin:8px 0}p{line-height:1.5}label{display:grid;gap:5px;font-weight:600;margin:14px 0}input,button{font:inherit;padding:12px;border-radius:9px;border:1px solid #bfd4c6}button{background:#155d4d;color:white;width:100%;cursor:pointer}a{color:#155d4d}@media(max-width:520px){main{margin:24px 14px}}</style>
            <main><small>MASTER BENEFICIARY REGISTRY</small><h1>Data Imports</h1><p>Sign in to the local test environment. Use synthetic data only.</p>
            ${wrong ? '<p role="alert">Check the username and password.</p>' : ''}
            <form method="post"><label>Username<input name="username" autocomplete="username" required></label><label>Password<input name="password" type="password" autocomplete="current-password" required></label><button>Sign in</button></form>
            <p><a href="/preview/sample.csv">Download a sample CSV with reconciliation cases</a></p></main></html>`);
            return;
        }
        if (path === '/auth/start_authentication_transaction') return respond(res, 200, { redirectUrl: base + '/preview/sign-in' });
        const token = req.headers.authorization?.replace(/^Bearer /, '');
        const session = sessions.get(token);
        if (!session || session.expires < Date.now()) return respond(res, 401, { error: 'Sign in first.' });
        const { role } = session;
        if (path === '/auth/get_logged_in_user') return respond(res, 200, { name: 'Test ' + role });
        if (path === '/auth/logout') { sessions.delete(token); return respond(res, 200, true); }
        if (path === '/user-access/get_application_permissions_for_user') {
            const permissions = role === 'approver' ? ['verificationIntakeForm:create', 'intakeSubmission:view']
                : ['intakeSubmission:edit', 'intakeSubmission:view'];
            return respond(res, 200, [{ permissions: role === 'administrator' ? [...permissions, 'register:view'] : permissions }]);
        }
        if (path === '/register-metadata/get_dashboard_registers') return backend(res, [register]);
        if (path === '/input-mechanism-metadata/get_import_file_configuration_for_register') return backend(res, [template]);
        if (path === '/documents/upload_documents') {
            if (role === 'approver') return respond(res, 403, {});
            const form = await (await request(req)).formData();
            const file = form.get('documents');
            const rows = parse(await file.text(), { columns: true });
            const retry = rows.map(row => row.reference).find(value => String(value).startsWith('RETRY-'));
            if (retry && db.prepare('INSERT OR IGNORE INTO preview_transient VALUES (?)').run(retry).changes) {
                return respond(res, 503, {});
            }
            const id = randomUUID();
            db.prepare('INSERT INTO preview_documents VALUES (?, ?, ?)').run(id, JSON.stringify(rows), role);
            return backend(res, { uploaded_documents: [{ document_store_id: id, document_label: 'import_file' }] });
        }
        if (path === '/input-mechanism-data/enqueue_import_file') {
            if (role === 'approver') return respond(res, 403, {});
            const body = await (await request(req)).json();
            const document = body.request_body.request_payload.document_store_id;
            const contents = db.prepare('SELECT * FROM preview_documents WHERE id = ?').get(document);
            if (!contents || contents.owner !== role) return respond(res, 403, {});
            const rows = JSON.parse(contents.rows);
            const records = rows.map((row, index) => String(row.reference).startsWith('FAIL-') ? 0 : index + 1).filter(Boolean);
            const receipt = { id: randomUUID(), status: records.length === rows.length ? 'processed' : 'failed',
                found: rows.length, ingested: records.length, attempts: records.length === rows.length ? 1 : 3, records };
            db.prepare('INSERT OR IGNORE INTO preview_receipts VALUES (?, ?, ?)').run(document, JSON.stringify(receipt), Date.now());
            const saved = JSON.parse(db.prepare('SELECT payload FROM preview_receipts WHERE document = ?').get(document).payload);
            if (rows.some(row => String(row.reference).startsWith('UNCONFIRMED-'))) return respond(res, 503, {});
            return backend(res, { import_file_id: saved.id });
        }
        if (path.startsWith('/preview/receipt/')) {
            const record = db.prepare('SELECT * FROM preview_receipts WHERE document = ?').get(path.slice('/preview/receipt/'.length));
            if (!record) return respond(res, 200, null);
            const receipt = JSON.parse(record.payload);
            if (Date.now() - record.committed < 1200) return respond(res, 200, { id: receipt.id, status: 'pending', found: null, ingested: null, attempts: 0, records: [] });
            return respond(res, 200, receipt);
        }
        if (path === '/registry-config/get_registry_configuration') return backend(res, {});
        return backend(res, []);
    } catch {
        if (!res.headersSent) respond(res, 500, { error: 'Preview fixture request failed.' });
        else res.end();
    }
});

server.listen(3101, '127.0.0.1', () => {
    console.log(`Sign in at ${base}/preview/sign-in`);
    console.log(`Preview credentials are in ${accountPath}`);
    const standalone = process.env.PREVIEW_STANDALONE === '1';
    const command = standalone ? ['.next/standalone/server.js'] : ['node_modules/next/dist/bin/next', 'dev', '--webpack', '-H', '127.0.0.1', '-p', '3100'];
    const child = spawn(process.execPath, command, {
        stdio: 'inherit', env: {
            ...process.env, APP_ORIGIN: app, IAM_URL: base, BACKEND_API_URL: base, MASTERDATA_BACKEND_API_URL: base,
            KEYCLOAK_LOGOUT_URL: base + '/preview/logout', REDIRECT_URL: app, DATA_IMPORTS_DB: database,
            DATA_IMPORTS_LOCAL_PREVIEW: '1',
            DATA_IMPORTS_CONNECTORS: JSON.stringify({ 'sample-api': { label: 'Sample Registry API', url: base + '/preview/source.csv', tokenEnv: 'DATA_IMPORTS_CONNECTOR_SAMPLE_TOKEN' } }),
            DATA_IMPORTS_CONNECTOR_SAMPLE_TOKEN: 'local-fixture-only', NEXT_TELEMETRY_DISABLED: '1', NOTIFICATION_DISABLED: 'true',
            HOSTNAME: '127.0.0.1', PORT: '3100', DATA_IMPORTS_NATIVE_READ_URL: '',
        },
    });
    child.on('exit', code => { server.close(); process.exitCode = code ?? 1; });
    process.on('SIGINT', () => child.kill());
    process.on('SIGTERM', () => child.kill());
});
