#!/usr/bin/env python3
"""Repair duplicate Commons resources and schema initialization hooks locally."""
import sys, yaml

def merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        result = dict(a)
        for key, value in b.items():
            result[key] = merge(result[key], value) if key in result else value
        return result
    if isinstance(a, list) and isinstance(b, list):
        result = list(a)
        for value in b:
            identity = next((k for k in ('clientId', 'username', 'name') if isinstance(value, dict) and k in value), None)
            match = next((i for i, old in enumerate(result) if identity and isinstance(old, dict) and old.get(identity) == value[identity]), None)
            if match is not None:
                result[match] = merge(result[match], value)
            elif value not in result:
                result.append(value)
        return result
    return b

resources = {}
for doc in yaml.safe_load_all(sys.stdin):
    if not doc:
        continue
    meta = doc.setdefault('metadata', {})
    key = (doc.get('kind'), meta.get('namespace'), meta.get('name'))
    if doc.get('kind') == 'Job' and ('postgres-init' in meta.get('name', '') or 'schema-init' in meta.get('name', '')):
        annotations = meta.get('annotations', {})
        for annotation in list(annotations):
            if annotation.startswith('helm.sh/hook'):
                del annotations[annotation]
    if key in resources:
        old = resources[key]
        if doc['kind'] == 'ConfigMap':
            for name, value in doc.get('data', {}).items():
                if name.endswith('.yaml') and name in old.get('data', {}):
                    old['data'][name] = yaml.safe_dump(merge(yaml.safe_load(old['data'][name]), yaml.safe_load(value)))
                else:
                    old.setdefault('data', {})[name] = value
        elif doc['kind'] != 'Secret':
            raise RuntimeError(f'Unexpected duplicate: {key}')
    else:
        resources[key] = doc
yaml.safe_dump_all(resources.values(), sys.stdout)
