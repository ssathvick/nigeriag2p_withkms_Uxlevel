'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { ArrowRight, CheckCircle2, CloudUpload, FileSpreadsheet, History, Settings2, ShieldCheck, TriangleAlert } from 'lucide-react';
import { useRegistryScope } from '@/components/shared/RegistryScope';
import { Link } from '@/i18n/navigation';
import { useRbac } from '@/context/RbacContext';
import { useAuth } from '@/context/Authcontext';
import { attentionStatuses, importRoles, mapRows, receiptStatuses, statuses, transferFilters, type Batch, type BatchSummary, type Connector, type ImportRow, type Source, type Status } from './model';
import SourceEditor from './SourceEditor';
import styles from './data-imports.module.css';

const endpoint = '/api/data-imports';

async function importRequest<T>(query = '', body?: FormData | object): Promise<T> {
    const response = await fetch(endpoint + query, {
        method: body ? 'POST' : 'GET', cache: 'no-store',
        headers: body && !(body instanceof FormData) ? { 'Content-Type': 'application/json' } : undefined,
        body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The request could not be completed.');
    return data as T;
}

type Overview = { batches: BatchSummary[]; sources: Source[]; connectors: Connector[]; counts: Partial<Record<Status, number>>; hasNext: boolean; preview: boolean };
const formatDate = (value: string) => new Intl.DateTimeFormat('en-NG', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));

function Badge({ status }: { status: Status }) {
    return <span className={styles.badge} data-tone={attentionStatuses.includes(status) ? 'warning' : status === 'received' || status === 'approved' ? 'success' : 'neutral'}>{statuses[status]}</span>;
}

function Button({ children, onClick, disabled, primary, type = 'button' }: {
    children: React.ReactNode; onClick?: () => void; disabled?: boolean; primary?: boolean; type?: 'button' | 'submit';
}) {
    return <button type={type} onClick={onClick} disabled={disabled} className={`workspace-button ${primary ? 'workspace-primary' : ''}`}>{children}</button>;
}

function Upload({ sources, busy, submit }: { sources: Source[]; busy: boolean; submit: (input: FormData | object) => void }) {
    const [source, setSource] = useState('');
    const selected = sources.find(item => item.id === source);
    return <section className={styles.panel}>
        <ol className={styles.steps} aria-label="Import steps">
            <li aria-current="step">1. Upload file</li><li>2. Validate records</li><li>3. Approve and transfer</li>
        </ol>
        <h2>Start an import</h2>
        <p>Choose the source supplying the records. Its mapping determines which columns the Registry receives.</p>
        {sources.length ? <form className={styles.stack} onSubmit={event => { event.preventDefault(); submit(selected?.connectorId ? { action: 'fetch-source', sourceId: selected.id } : new FormData(event.currentTarget)); }}>
            <label>Data source<select name="source" value={source} onChange={event => setSource(event.target.value)} required>
                <option value="">Select a source</option>
                {sources.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select></label>
            {selected && <details><summary>Expected columns</summary><ul className={styles.columns}>{selected.fields.map(field => <li key={field.name}>{field.column} {field.required && <strong>· Required</strong>}</li>)}</ul></details>}
            {selected?.connectorId ? <div className={styles.notice}>Get the latest file from this source connection. You can verify and correct the data before approval.</div> : <><label className={styles.upload}><CloudUpload size={26} aria-hidden="true" /><span>Choose a beneficiary data file</span>
                <input name="file" type="file" accept=".csv,.xlsx" required aria-describedby="import-formats" />
                <small id="import-formats">CSV or XLSX · up to 2 MB and 1,000 rows · first worksheet only</small>
            </label>
            <div className={styles.notice}><FileSpreadsheet size={19} aria-hidden="true" />For PDFs and images, extract the data and verify the fields before uploading a spreadsheet. Format identifiers as text in Excel to preserve leading zeros.</div></>}
            <div className={styles.actions}><Button type="submit" primary disabled={!selected || busy}>{selected?.connectorId ? 'Fetch and validate' : 'Validate file'} <ArrowRight size={16} /></Button></div>
        </form> : <div className={styles.empty}>No active sources are configured. A Registry administrator can add a source and map its fields.</div>}
    </section>;
}

function RowEditor({ row, columns, busy, save }: {
    row: ImportRow; columns: string[]; busy: boolean; save: (values: string[], excluded: boolean) => void;
}) {
    const [values, setValues] = useState(row.values);
    const [excluded, setExcluded] = useState(row.excluded);
    return <form className={styles.stack} onSubmit={event => { event.preventDefault(); save(values, excluded); }}>
        <div className={styles.fields}>{columns.map((column, index) => <label key={column}>{column}
            <input value={values[index]} maxLength={500} onChange={event => setValues(old => old.map((value, i) => i === index ? event.target.value : value))} />
        </label>)}</div>
        <label className={styles.check}><input type="checkbox" checked={excluded} onChange={event => setExcluded(event.target.checked)} /> Exclude this row from the transfer</label>
        <div className={styles.actions}><Button type="submit" disabled={busy}>Save row</Button></div>
    </form>;
}

function BatchDetail({ batch, role, canEdit, canTransfer, busy, apply, back }: {
    batch: Batch; role?: string; canEdit: boolean; canTransfer: boolean; busy: boolean;
    apply: (action: string, payload?: object) => void; back: () => void;
}) {
    const [onlyIssues, setOnlyIssues] = useState(false);
    const [show, setShow] = useState(12);
    const [note, setNote] = useState('');
    const validation = mapRows(batch.source, batch.columns, batch.rows);
    const issues = validation.included.filter(row => row.issues.length).length;
    const excluded = validation.rows.length - validation.included.length;
    const nativeIssues = batch.status === 'failed' || batch.status === 'partial';
    const received = new Set(batch.nativeRows);
    const rows = validation.rows.filter(row => !onlyIssues || row.excluded || row.issues.length || (nativeIssues && !received.has(row.line)));
    const lastReturn = batch.events.findLast(event => event.note && event.action === 'Batch returned for correction');
    const downloadAudit = () => {
        const report = { batch: batch.id, source: batch.source.name, sourceVersion: batch.source.version, status: statuses[batch.status],
            nativeId: batch.nativeId, found: batch.found, ingested: batch.ingested, attempts: batch.attempts,
            events: batch.events.map(({ at, actor, action }) => ({ at, actor, action })) };
        const url = URL.createObjectURL(new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }));
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = `import-audit-${batch.id}.json`;
        anchor.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    };

    return <div className={styles.stack}>
        <section className={styles.panel}>
            <div className={styles.heading}>
                <div><Button onClick={back}>← Back to imports</Button><h2 className={styles.fileName}>{batch.fileName}</h2>
                    <p>{batch.source.name} · Mapping version {batch.source.version} · {batch.ownerName}</p></div>
                <Badge status={batch.status} />
            </div>
            <div className={styles.metrics}>
                <div><strong>{validation.rows.length}</strong><span>Rows uploaded</span></div>
                <div><strong>{validation.included.length - issues}</strong><span>Passed import checks</span></div>
                <div><strong>{issues}</strong><span>Rows with issues</span></div>
                <div><strong>{excluded}</strong><span>Excluded</span></div>
            </div>
            {validation.missing.length > 0 && <p role="alert" className={styles.warning}>Missing columns: {validation.missing.join(', ')}. Add these to the spreadsheet and start a new import.</p>}
            {batch.status === 'returned' && lastReturn && <p className={styles.warning}>{lastReturn.note}</p>}
            {['queued', 'received', 'partial', 'failed', 'unconfirmed', 'sending'].includes(batch.status) && <div className={styles.notice}>
                <div><strong>Registry receipt</strong><p>{batch.nativeId || 'Awaiting the Registry reference.'}</p>
                    {batch.nativeStatus && <p>Native status: {batch.nativeStatus} · Ingested {batch.ingested ?? '—'} of {batch.found ?? '—'} · Attempts {batch.attempts ?? '—'}</p>}
                    {batch.status === 'unconfirmed' && <p>Refresh the Registry receipt before taking further action. Resubmission is blocked while delivery is uncertain.</p>}
                    {['partial', 'failed'].includes(batch.status) && <p>Check the native ingestion job before submitting corrections. This batch won’t be sent again automatically.</p>}
                    {batch.status === 'received' && <p>The Registry ingested these rows. Follow registration decisions in Registration review.</p>}
                </div>
            </div>}
            <div className={styles.actions}>
                {canEdit && <Button primary disabled={busy || !!issues || !!validation.missing.length || !validation.included.length} onClick={() => apply('review')}>Send for approval</Button>}
                {canTransfer && ['approved', 'retry'].includes(batch.status) && <Button primary disabled={busy} onClick={() => apply('transfer')}>{batch.status === 'retry' ? 'Retry transfer' : 'Transfer to Registry'}</Button>}
                {receiptStatuses.includes(batch.status) && <Button primary disabled={busy} onClick={() => apply('refresh')}>Refresh Registry receipt</Button>}
                <Button onClick={downloadAudit}>Download audit report</Button>
            </div>
            {role === 'level1' && batch.status === 'review' && <form className={styles.review} onSubmit={(event: FormEvent) => { event.preventDefault(); apply('return', { note }); }}>
                <h3>Review decision</h3>
                <label>Reason for returning this batch<textarea value={note} onChange={event => setNote(event.target.value)} maxLength={500} rows={3} /></label>
                <div className={styles.actions}><Button primary disabled={busy} onClick={() => apply('approve')}>Approve batch</Button><Button type="submit" disabled={busy || !note.trim()}>Return for correction</Button></div>
            </form>}
        </section>
        <section className={styles.panel}>
            <div className={styles.heading}><div><h2>Reconcile records</h2><p>Open a row to see its source values and the fields mapped to the Registry.</p></div>
                <label className={styles.check}><input type="checkbox" checked={onlyIssues} onChange={event => setOnlyIssues(event.target.checked)} /> Issues and exclusions only</label></div>
            <div className={styles.stack}>
                {rows.slice(0, show).map(row => <details className={styles.row} key={row.line}>
                    <summary><span>Row {row.line}</span><span className={styles.rowState}>{row.excluded ? 'Excluded' : row.issues.length ? `${row.issues.length} to fix` : received.has(row.line) ? 'Registry logged' : nativeIssues ? 'No Registry row receipt' : 'Passed'}</span></summary>
                    <div className={styles.rowBody}>
                        {row.issues.length > 0 && <ul className={styles.warning}>{row.issues.map(issue => <li key={issue}>{issue}</li>)}</ul>}
                        {canEdit && <RowEditor key={`${batch.version}:${row.line}`} row={row} columns={batch.columns} busy={busy}
                            save={(values, isExcluded) => apply('edit', { line: row.line, values, excluded: isExcluded })} />}
                        {!canEdit && <><h3>Source values</h3><dl className={styles.fields}>{batch.columns.map((column, i) =>
                            <div key={column}><dt>{column}</dt><dd>{row.values[i] || '—'}</dd></div>)}</dl></>}
                        <h3>Mapped Registry values</h3>
                        <dl className={styles.fields}>{batch.source.fields.map((field, i) => <div key={field.name}><dt>{field.name}</dt><dd>{row.mapped[i] || '—'}</dd></div>)}</dl>
                    </div>
                </details>)}
                {rows.length === 0 && <div className={styles.empty}>No rows match this filter.</div>}
                {rows.length > show && <div className={styles.actions}><Button onClick={() => setShow(value => value + 12)}>Show more rows</Button></div>}
            </div>
        </section>
        <section className={styles.panel}>
            <h2>Activity</h2>
            <ol className={styles.timeline}>{[...batch.events].reverse().map((event, index) => <li key={index}>
                <strong>{event.action}</strong><span>{formatDate(event.at)} · {event.actor}</span>{event.note && <p>{event.note}</p>}
            </li>)}</ol>
        </section>
    </div>;
}

export default function DataImports() {
    const role = useRegistryScope();
    const { user } = useAuth();
    const { can } = useRbac();
    const canUpload = role === 'field' || role === 'admin';
    const [tab, setTab] = useState('transfers');
    const [overview, setOverview] = useState<Overview>();
    const [batch, setBatch] = useState<Batch>();
    const [busy, setBusy] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [status, setStatus] = useState('');
    const [page, setPage] = useState(0);
    const [filter, setFilter] = useState<keyof typeof transferFilters>('all');

    useEffect(() => {
        let active = true;
        importRequest<Overview>(`?page=${page}&filter=${filter}`).then(data => { if (active) setOverview(data); })
            .catch(cause => { if (active) setError(cause.message); })
            .finally(() => { if (active) setLoading(false); });
        return () => { active = false; };
    }, [page, filter]);

    async function run(operation: () => Promise<void>) {
        setBusy(true);
        setError('');
        setStatus('');
        try { await operation(); } catch (cause) { setError(cause instanceof Error ? cause.message : 'The request could not be completed.'); }
        finally { setBusy(false); }
    }

    function reload() {
        return importRequest<Overview>(`?page=${page}&filter=${filter}`).then(setOverview);
    }

    function open(id: string) {
        void run(async () => { setBatch(await importRequest<Batch>(`?id=${encodeURIComponent(id)}`)); });
    }

    function select(next: string) {
        setBatch(undefined);
        setError('');
        setStatus('');
        setTab(next);
    }

    const owner = !!user && batch?.owner === user.registry_actor_id;
    const items = overview?.batches ?? [];
    const numberOf = (value: keyof typeof transferFilters) => {
        const counts = overview?.counts ?? {};
        const group = transferFilters[value].statuses;
        return (group.length ? group.map(status => counts[status] ?? 0) : Object.values(counts)).reduce((sum, count) => sum + count, 0);
    };

    if (!importRoles.some(item => item === role)) return <section className={styles.panel}><h2>Access to Data Imports</h2><p>Your Registry role does not have access to this workspace.</p></section>;
    return <main className={styles.root} aria-busy={busy || loading}>
        {overview?.preview && <div className={styles.notice}>Local test environment. Use synthetic beneficiary data only.</div>}
        <nav className={styles.tabs} aria-label="Data Imports">
            <button type="button" disabled={busy} aria-current={tab === 'transfers' ? 'page' : undefined} onClick={() => select('transfers')}><History size={18} /> Transfers</button>
            {canUpload && <button type="button" disabled={busy} aria-current={tab === 'upload' ? 'page' : undefined} onClick={() => select('upload')}><CloudUpload size={18} /> New import</button>}
            {role === 'admin' && <button type="button" disabled={busy} aria-current={tab === 'sources' ? 'page' : undefined} onClick={() => select('sources')}><Settings2 size={18} /> Sources and mappings</button>}
            {role === 'admin' && <button type="button" disabled={busy} aria-current={tab === 'access' ? 'page' : undefined} onClick={() => select('access')}><ShieldCheck size={18} /> Access</button>}
        </nav>
        {error && <p className={styles.warning} role="alert"><TriangleAlert size={17} /> {error} {batch && <Button disabled={busy} onClick={() => open(batch.id)}>Reload batch</Button>}</p>}
        {status && <p className={styles.notice} role="status"><CheckCircle2 size={17} /> {status}</p>}
        {loading && <p role="status" className={styles.empty}>Loading imports…</p>}
        {!loading && !overview && <Button onClick={() => void run(reload)} disabled={busy}>Retry loading imports</Button>}
        {batch && <BatchDetail key={batch.id} batch={batch} role={role} canEdit={owner && ['draft', 'returned'].includes(batch.status)} canTransfer={can('intakeSubmission:edit') && (role === 'admin' || owner)}
            busy={busy} back={() => { select('transfers'); void run(reload); }}
            apply={(action, payload) => void run(async () => {
                const updated = await importRequest<Batch>('', { ...payload, action, id: batch.id, version: batch.version });
                setBatch(updated);
                setStatus(action === 'edit' ? 'Row saved.' : action === 'refresh' && updated.version === batch.version ? 'No new Registry status.' : statuses[updated.status]);
            })} />}
        {!batch && overview && tab === 'upload' && <Upload sources={overview.sources.filter(source => source.active)} busy={busy}
            submit={form => void run(async () => { setBatch(await importRequest<Batch>('', form)); setStatus('File validated. Review the rows before requesting approval.'); })} />}
        {!batch && overview && tab === 'sources' && role === 'admin' && <SourceEditor sources={overview.sources} connectors={overview.connectors} busy={busy}
            save={source => run(async () => { await importRequest('', { ...source, action: 'source' }); await reload(); setStatus('Source mapping saved.'); })} />}
        {!batch && overview && tab === 'access' && role === 'admin' && <section className={styles.panel}>
            <div><h2>Data Imports access</h2><p>Access follows each staff member’s assigned Registry role.</p></div>
            <dl className={styles.access}>
                <div><dt>Operator · Registry Field Agent</dt><dd>Create and correct their own batches, request approval and transfer approved files.</dd></div>
                <div><dt>Approver · Registry First Reviewer</dt><dd>Review submitted batches, approve them or return them to the operator with a reason.</dd></div>
                <div><dt>Administrator · Registry Administrator</dt><dd>Manage sources and mappings and monitor batches. Transfer also requires native intake-edit access.</dd></div>
            </dl>
            {can('registryConfiguration:edit') && <div className={styles.actions}><Link href="/configuration/registry/users" className="workspace-button">Manage Registry staff</Link></div>}
        </section>}
        {!batch && overview && tab === 'transfers' && <section className={styles.panel}>
            <div className={styles.heading}><div><h2>Transfer history</h2><p>Follow submissions from upload through Registry ingestion.</p></div>
                <div className={styles.actions}><Button disabled={busy} onClick={() => void run(reload)}>Refresh history</Button>
                    {canUpload && <Button primary onClick={() => select('upload')}>New import</Button>}</div></div>
            <div className={styles.filters} aria-label="Transfer filters">
                {(Object.keys(transferFilters) as (keyof typeof transferFilters)[]).map(value =>
                    <button type="button" key={value} disabled={loading} aria-pressed={filter === value}
                        onClick={() => { if (value !== filter) { setLoading(true); setPage(0); setFilter(value); } }}>
                        {transferFilters[value].label} <span className={styles.filterCount}>{numberOf(value)}</span>
                    </button>)}
            </div>
            <ul className={styles.transfers}>{items.map(item => <li key={item.id}>
                <button type="button" onClick={() => open(item.id)} disabled={busy} className={styles.transfer}>
                    <span className={styles.transferIcon}><FileSpreadsheet size={20} /></span>
                    <span className={styles.transferName}><strong>{item.fileName}</strong><small>{item.sourceName} · {item.count} rows · {formatDate(item.updated)}</small></span>
                    <Badge status={item.status} /><ArrowRight size={18} aria-hidden="true" />
                </button>
            </li>)}</ul>
            {items.length === 0 && <div className={styles.empty}>{filter === 'all' && page === 0 ? 'No imports yet.' : 'No batches match this filter.'}</div>}
            {(page > 0 || overview.hasNext) && <div className={styles.actions}>
                <Button disabled={!page || loading} onClick={() => { setLoading(true); setPage(page - 1); }}>Previous page</Button>
                <span>Page {page + 1}</span>
                <Button disabled={!overview.hasNext || loading} onClick={() => { setLoading(true); setPage(page + 1); }}>Next page</Button>
            </div>}
        </section>}
    </main>;
}
