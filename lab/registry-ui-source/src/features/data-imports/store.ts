import 'server-only';
import { DatabaseSync } from 'node:sqlite';
import { type Batch, type BatchSummary, type Source, type Status } from './model';

let connection: DatabaseSync | undefined;

function db() {
    const file = process.env.DATA_IMPORTS_DB;
    if (!file) throw new Error('Data Imports storage is unavailable.');
    if (!connection) {
        connection = new DatabaseSync(file);
        connection.exec(`
            PRAGMA busy_timeout = 5000;
            PRAGMA journal_mode = WAL;
            CREATE TABLE IF NOT EXISTS import_sources (
                id TEXT PRIMARY KEY, version INTEGER NOT NULL, payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS import_batches (
                id TEXT PRIMARY KEY, owner TEXT NOT NULL, version INTEGER NOT NULL,
                status TEXT NOT NULL, updated TEXT NOT NULL, payload TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS import_batches_owner ON import_batches(owner, updated DESC);
        `);
    }
    return connection;
}

function decode<T>(row: { payload?: unknown } | undefined): T | undefined {
    return row ? JSON.parse(String(row.payload)) as T : undefined;
}

export function sources() {
    return db().prepare('SELECT payload FROM import_sources ORDER BY rowid').all()
        .map(row => decode<Source>(row)!);
}

export function sourceById(id: string) {
    return decode<Source>(db().prepare('SELECT payload FROM import_sources WHERE id = ?').get(id));
}

export function saveSource(source: Source, expected: number) {
    const sql = expected === 0
        ? 'INSERT INTO import_sources (version, payload, id) VALUES (?, ?, ?) ON CONFLICT DO NOTHING'
        : 'UPDATE import_sources SET version = ?, payload = ? WHERE id = ? AND version = ?';
    const values = [source.version, JSON.stringify(source), source.id];
    return db().prepare(sql).run(...(expected ? [...values, expected] : values)).changes === 1;
}

export function batchById(id: string) {
    return decode<Batch>(db().prepare('SELECT payload FROM import_batches WHERE id = ?').get(id));
}

export function batches(owner: string | null, omitDrafts: boolean, statuses: Status[], offset: number) {
    const rules: string[] = [];
    const values: string[] = [];
    if (owner) { rules.push('owner = ?'); values.push(owner); }
    if (omitDrafts) rules.push("status <> 'draft'");
    const visible = rules.length ? `WHERE ${rules.join(' AND ')}` : '';
    const stats = db().prepare(`SELECT status, COUNT(*) AS count FROM import_batches ${visible} GROUP BY status`).all(...values);
    if (statuses.length) {
        rules.push(`status IN (${statuses.map(() => '?').join(', ')})`);
        values.push(...statuses);
    }
    const where = rules.length ? `WHERE ${rules.join(' AND ')}` : '';
    const records = db().prepare(`
        SELECT id, status, updated,
            json_extract(payload, '$.fileName') AS fileName,
            json_extract(payload, '$.ownerName') AS ownerName,
            json_extract(payload, '$.source.name') AS sourceName,
            json_array_length(payload, '$.rows') AS count,
            json_extract(payload, '$.nativeId') AS nativeId,
            json_extract(payload, '$.found') AS found,
            json_extract(payload, '$.ingested') AS ingested,
            json_extract(payload, '$.attempts') AS attempts
        FROM import_batches ${where} ORDER BY updated DESC, id LIMIT 21 OFFSET ?
    `).all(...values, offset) as unknown as BatchSummary[];
    return { records, counts: Object.fromEntries(stats.map(row => [String(row.status), Number(row.count)])) as Partial<Record<Status, number>> };
}

export function saveBatch(batch: Batch, expected: number) {
    const updated = batch.events.at(-1)!.at;
    const values = [batch.version, batch.status, updated, JSON.stringify(batch), batch.id];
    if (expected === 0) {
        return db().prepare('INSERT INTO import_batches (version, status, updated, payload, id, owner) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT DO NOTHING')
            .run(...values, batch.owner).changes === 1;
    }
    return db().prepare('UPDATE import_batches SET version = ?, status = ?, updated = ?, payload = ? WHERE id = ? AND version = ?')
        .run(...values, expected).changes === 1;
}
