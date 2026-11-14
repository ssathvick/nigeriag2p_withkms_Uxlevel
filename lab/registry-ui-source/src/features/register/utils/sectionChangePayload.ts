/** A widget editor may return its entire backing record. Only propose fields owned by this section. */
export function sectionChangePayload(schema: unknown, records: Record<string, unknown>[]) {
    const fields = new Map<string, Record<string, any>>();
    const walk = (node: any) => {
        if (!node || typeof node !== 'object') return;
        if (Array.isArray(node)) { node.forEach(walk); return; }
        const paths = node['widget-data-path'];
        for (const path of typeof paths === 'string' ? [paths] : Object.values(paths ?? {})) {
            if (typeof path === 'string' && path.includes('.')) fields.set(path.split('.')[1], node);
        }
        if (typeof node['column-key'] === 'string') fields.set(node['column-key'], node);
        Object.values(node).forEach(walk);
    };
    walk(schema);
    if (!fields.size) throw new Error('Section fields could not be identified. Reload the record before saving.');
    const identities = new Set(['internal_record_id', 'link_internal_record_id', 'edit_action']);
    return records.map(record => Object.fromEntries(Object.entries(record).filter(([key]) => identities.has(key) || fields.has(key)).map(([key, raw]) => {
        const widget = fields.get(key);
        const options = widget?.['widget-data-source']?.options;
        const option = Array.isArray(options) ? options.find(o => String(o.value) === String(raw)) : undefined;
        let value = option ? option.value : raw;
        if (widget?.widget === 'number' && typeof value === 'string' && value.trim() && Number.isFinite(Number(value))) value = Number(value);
        return [key, value];
    })));
}
