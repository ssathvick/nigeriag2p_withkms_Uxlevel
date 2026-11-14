"""Repair geography widget parameters in the Nigeria demonstration registry.

Run from the lab host with the labdb module available and backed-up database
access. Changes only mismatched geo-level-values widget parameters. The current
JSON is checked in the same transaction to prevent overwriting concurrent edits.
"""
import json, os, sys, time
from pathlib import Path
from labdb import query

def quote(value): return "'" + value.replace("'", "''") + "'"
def update_widgets(node):
    count = 0
    if isinstance(node, dict):
        source = node.get('widget-data-source')
        if isinstance(source, dict) and source.get('type') == 'api' and source.get('service') == 'master-data' and source.get('endpoint') == 'geo-level-values' and source.get('level_id'):
            params = source.setdefault('params', {})
            if not isinstance(params, dict):
                raise ValueError('Unexpected geo widget params; no changes made')
            expected = {'valueKey': 'level_value_id', 'labelKey': 'level_value_mnemonic'}
            if params.get('level_id') != source['level_id'] or any(source.get(k) != v for k, v in expected.items()):
                params['level_id'] = source['level_id']; source.update(expected); count += 1
        for value in node.values(): count += update_widgets(value)
    elif isinstance(node, list):
        for value in node: count += update_widgets(value)
    return count

def main():
    raw = query('register', "SELECT row_to_json(t) FROM (SELECT register_id, section_id, section_ui_schema FROM g2p_register_sections) t;")
    changes = []
    for line in raw.splitlines():
        row = json.loads(line); before = row['section_ui_schema']
        after = json.loads(json.dumps(before)); n = update_widgets(after)
        if n: changes.append((row, after, n))
    if not changes:
        print('No geography metadata changes required'); return
    backup = Path('/opt/openg2p-lab/backups') / ('geo-widget-metadata-' + time.strftime('%Y%m%d-%H%M%S') + '.json')
    backup.parent.mkdir(parents=True, exist_ok=True)
    with open(backup, 'x', encoding='utf8') as f:
        os.chmod(backup, 0o600)
        json.dump([row for row, _, _ in changes], f, ensure_ascii=False, indent=2)
    sql = ['BEGIN;']
    for row, after, _ in changes:
        where = 'register_id=' + quote(str(row['register_id'])) + ' AND section_id=' + quote(str(row['section_id']))
        old = quote(json.dumps(row['section_ui_schema'], ensure_ascii=False)) + '::jsonb'
        new = quote(json.dumps(after, ensure_ascii=False)) + '::jsonb'
        sql.append('DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM g2p_register_sections WHERE ' + where + ' AND section_ui_schema=' + old + ") THEN RAISE EXCEPTION 'Geography metadata changed during repair'; END IF; END $$;")
        sql.append('UPDATE g2p_register_sections SET section_ui_schema=' + new + ' WHERE ' + where + ' AND section_ui_schema=' + old + ';')
    sql.append('COMMIT;')
    query('register', '\n'.join(sql))
    print('Updated', sum(n for _, _, n in changes), 'widgets in', len(changes), 'sections; metadata backup:', backup)

if __name__ == '__main__': main()
