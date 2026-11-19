export const importRoles = ['field', 'level1', 'admin'] as const;
export type ImportRole = typeof importRoles[number];

export const statuses = {
    draft: 'Draft',
    review: 'Awaiting approval',
    returned: 'Returned for correction',
    approved: 'Approved',
    sending: 'Submitting to Registry',
    retry: 'Ready to retry',
    unconfirmed: 'Submission unconfirmed',
    queued: 'Queued at Registry',
    received: 'Ingested by Registry',
    partial: 'Partially ingested',
    failed: 'Ingestion needs attention',
} as const;

export type Status = keyof typeof statuses;
export const attentionStatuses: Status[] = ['returned', 'retry', 'unconfirmed', 'partial', 'failed'];
export const receiptStatuses: Status[] = ['sending', 'unconfirmed', 'queued', 'received', 'partial', 'failed'];
export const transferFilters = {
    all: { label: 'All batches', statuses: [] as Status[] },
    review: { label: 'Awaiting approval', statuses: ['review'] as Status[] },
    attention: { label: 'Needs attention', statuses: attentionStatuses },
    sent: { label: 'Sent to Registry', statuses: receiptStatuses.filter(status => status !== 'sending') },
};
export type Field = { name: string; column: string; required: boolean; transform: 'none' | 'trim' | 'upper' | 'lower' };
export type Source = {
    id: string; name: string; registerId: string; templateId: string;
    fields: Field[]; key: string; active: boolean; version: number; connectorId?: string;
};
export type Connector = { id: string; label: string };
export type ImportRow = { line: number; values: string[]; excluded: boolean };
export type Event = { at: string; actor: string; action: string; note?: string };
export type Batch = {
    id: string; version: number; owner: string; ownerName: string; fileName: string; source: Source;
    columns: string[]; rows: ImportRow[]; status: Status; events: Event[];
    documentId?: string; nativeId?: string; nativeStatus?: string;
    found?: number; ingested?: number; attempts?: number; nativeRows?: number[];
};
export type BatchSummary = Pick<Batch, 'id' | 'ownerName' | 'fileName' | 'status' | 'nativeId' | 'found' | 'ingested' | 'attempts'> & {
    sourceName: string; updated: string; count: number;
};

export const limits = { file: 2 * 1024 * 1024, rows: 1000, columns: 40, cell: 500 };

export function transformValue(value: string, transform: Field['transform']) {
    switch (transform) {
        case 'trim': return value.trim();
        case 'upper': return value.trim().toUpperCase();
        case 'lower': return value.trim().toLowerCase();
        default: return value;
    }
}

export function mapRows(source: Source, columns: string[], rows: ImportRow[]) {
    const indices = source.fields.map(field => columns.indexOf(field.column));
    const missing = source.fields.filter((field, i) => field.required && indices[i] < 0).map(field => field.column);
    const keyIndex = source.fields.findIndex(field => field.name === source.key);
    const seen = new Map<string, number>();
    const result = rows.map(row => {
        const issues: string[] = [];
        const mapped = source.fields.map((field, i) => {
            const original = row.values[indices[i]] ?? '';
            const value = transformValue(original, field.transform);
            if (field.required && !value.trim()) issues.push(`${field.name} is required`);
            return value;
        });
        const key = mapped[keyIndex]?.trim().toLowerCase();
        if (!row.excluded && key) {
            const previous = seen.get(key);
            if (previous !== undefined) issues.push(`Duplicate ${source.key} from row ${previous}`);
            else seen.set(key, row.line);
        }
        return { ...row, mapped, issues };
    });
    return { missing, rows: result, included: result.filter(row => !row.excluded) };
}
