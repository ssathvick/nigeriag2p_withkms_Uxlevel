'use client';

import { useEffect, useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { useRegister } from '@/context/RegisterContext';
import { transformValue, type Connector, type Field, type Source } from './model';
import styles from './data-imports.module.css';

type Template = { import_file_configuration_id: string; import_file_template_description: string; import_file_template_mnemonic: string };
type Draft = Omit<Source, 'id' | 'version'> & { id?: string; version?: number };
const newField = (): Field => ({ name: '', column: '', required: true, transform: 'trim' });

function MappingForm({ source, connectors, busy, save }: { source?: Source; connectors: Connector[]; busy: boolean; save: (value: Draft) => Promise<void> }) {
    const { registers } = useRegister();
    const [draft, setDraft] = useState<Draft>(source ?? {
        name: '', registerId: '', templateId: '', active: true, key: '', fields: [newField()],
    });
    const [templates, setTemplates] = useState<Template[]>([]);
    const [templateError, setTemplateError] = useState('');
    const [loadingTemplates, setLoadingTemplates] = useState(false);
    const [sample, setSample] = useState<string[]>([]);
    const patch = (value: Partial<Draft>) => setDraft(old => ({ ...old, ...value }));
    const patchField = (index: number, value: Partial<Field>) => setDraft(old => ({
        ...old, fields: old.fields.map((field, i) => i === index ? { ...field, ...value } : field),
        key: value.name !== undefined && old.key === old.fields[index].name ? value.name : old.key,
    }));

    useEffect(() => {
        if (!draft.registerId) return;
        const controller = new AbortController();
        fetch('/api/data-imports?templates=' + encodeURIComponent(draft.registerId), { cache: 'no-store', signal: controller.signal })
            .then(async response => {
                const data = await response.json();
                if (!response.ok) throw new Error(data.error);
                setTemplates(data);
                setTemplateError(data.length ? '' : 'This register has no configured import templates.');
            })
            .catch(error => { if (!controller.signal.aborted) setTemplateError(error.message); })
            .finally(() => { if (!controller.signal.aborted) setLoadingTemplates(false); });
        return () => controller.abort();
    }, [draft.registerId]);

    return <form className={styles.stack} onSubmit={event => { event.preventDefault(); void save(draft); }}>
        <div className={styles.fields}>
            <label>Source name<input value={draft.name} maxLength={100} required onChange={event => patch({ name: event.target.value })} /></label>
            <label>Destination register<select required value={draft.registerId} onChange={event => {
                setTemplates([]); setTemplateError(''); setLoadingTemplates(!!event.target.value);
                patch({ registerId: event.target.value, templateId: '' });
            }}><option value="">Select a register</option>
                {registers.map(register => <option key={register.register_id} value={register.register_id}>{register.register_subject || register.register_mnemonic}</option>)}
            </select></label>
            <label>Native import template<select required value={draft.templateId} disabled={!draft.registerId || loadingTemplates} onChange={event => patch({ templateId: event.target.value })}>
                <option value="">{loadingTemplates ? 'Loading templates…' : 'Select a template'}</option>
                {templates.map(template => <option key={template.import_file_configuration_id} value={template.import_file_configuration_id}>
                    {template.import_file_template_description || template.import_file_template_mnemonic}
                </option>)}
            </select></label>
        </div>
        {templateError && <p className={styles.warning} role="status">{templateError}</p>}
        <label>How to receive records<select value={draft.connectorId || ''} onChange={event => patch({ connectorId: event.target.value || undefined })}>
            <option value="">Upload a file</option>
            {connectors.map(connector => <option key={connector.id} value={connector.id}>{connector.label}</option>)}
        </select></label>
        <label className={styles.check}><input type="checkbox" checked={draft.active} onChange={event => patch({ active: event.target.checked })} /> Available for new imports</label>
        <h3>Map incoming fields</h3>
        <p>Enter each spreadsheet column and the corresponding column required by the destination template. Changes apply to new batches.</p>
        {draft.fields.map((field, index) => <fieldset key={index} className={styles.mapping}>
            <legend>Field {index + 1}</legend>
            <div className={styles.fields}>
                <label>Spreadsheet column<input value={field.column} maxLength={100} required onChange={event => patchField(index, { column: event.target.value })} /></label>
                <label>Registry column<input value={field.name} maxLength={100} required onChange={event => patchField(index, { name: event.target.value })} /></label>
                <label>Transform<select value={field.transform} onChange={event => patchField(index, { transform: event.target.value as Field['transform'] })}>
                    <option value="none">Keep as entered</option><option value="trim">Trim spaces</option><option value="upper">Trim and uppercase</option><option value="lower">Trim and lowercase</option>
                </select></label>
            </div>
            <div className={styles.actions}>
                <label className={styles.check}><input type="checkbox" checked={field.required} onChange={event => patchField(index, { required: event.target.checked })} /> Required value</label>
                <button type="button" className="workspace-button" disabled={draft.fields.length === 1} onClick={() => {
                    patch({ fields: draft.fields.filter((_, i) => i !== index), key: draft.key === field.name ? '' : draft.key });
                    setSample([]);
                }}><Trash2 size={15} /> Remove field</button>
            </div>
        </fieldset>)}
        <div className={styles.actions}><button type="button" className="workspace-button" disabled={draft.fields.length >= 40} onClick={() => patch({ fields: [...draft.fields, newField()] })}><Plus size={15} /> Add field</button></div>
        <label>Field for duplicate checks<select value={draft.key} onChange={event => patch({ key: event.target.value })} required>
            <option value="">Select a required Registry field</option>
            {draft.fields.filter(field => field.name && field.required).map((field, i) => <option key={i} value={field.name}>{field.name}</option>)}
        </select></label>
        <details className={styles.row}><summary>Test mapping with sample values</summary>
            <div className={styles.rowBody}><p>Use sample values to see how the mapping transforms them.</p>
                <div className={styles.fields}>{draft.fields.map((field, index) => {
                    const input = sample[index] || '';
                    const mapped = transformValue(input, field.transform);
                    return <label key={index}>{field.column || `Column ${index + 1}`}
                        <input value={input} maxLength={500} onChange={event => setSample(old => Object.assign([...old], { [index]: event.target.value }))} />
                        <small>{field.name || 'Registry value'} · {mapped || (field.required ? 'Required' : '—')}</small>
                    </label>;
                })}</div>
            </div>
        </details>
        <div className={styles.actions}><button type="submit" className="workspace-button workspace-primary" disabled={busy || !templates.some(template => template.import_file_configuration_id === draft.templateId)}>Save source mapping</button></div>
    </form>;
}

export default function SourceEditor({ sources, connectors, busy, save }: { sources: Source[]; connectors: Connector[]; busy: boolean; save: (value: Draft) => Promise<void> }) {
    const [selected, setSelected] = useState('');
    const source = sources.find(item => item.id === selected);
    return <section className={styles.panel}>
        <div className={styles.heading}><div><h2>Sources and mappings</h2><p>Manage file and connected sources and the fields used to import into each Registry template.</p></div></div>
        <label>Source to configure<select value={selected} disabled={busy} onChange={event => setSelected(event.target.value)}>
            <option value="">Create a source</option>{sources.map(item => <option key={item.id} value={item.id}>{item.name}{item.active ? '' : ' (inactive)'}</option>)}
        </select></label>
        <MappingForm key={source ? `${source.id}:${source.version}` : 'new'} source={source} connectors={connectors} busy={busy} save={async value => { await save(value); }} />
    </section>;
}
