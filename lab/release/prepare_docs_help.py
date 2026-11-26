"""Build a destination-specific NSIPA documentation and Help release."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

from merge_knowledge import read_seed


LAB = Path(__file__).resolve().parents[1]
SERVICES = {
    'register', 'registry', 'beneficiary', 'pbms', 'awe', 'portal-admin', 'odk', 'superset',
    'master-data-ui', 'partner-management', 'consent-manager', 'staff-portal', 'iam-staff-ui', 'keycloak',
}
HOST = re.compile(r'[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+')


def settings(path):
    config = json.loads(path.read_text(encoding='utf-8-sig'))
    services = config['services']
    if services.keys() != SERVICES:
        raise ValueError('Supply one host for every service in docs-help.example.json')
    hosts = [config['platform'], config['docs'], *services.values()]
    if any(not HOST.fullmatch(host) for host in hosts) or len(set(hosts)) != len(hosts):
        raise ValueError('Use distinct lowercase DNS hostnames, without schemes or paths')
    upstream = urlsplit(config['registration_upstream'])
    if (upstream.scheme not in ('http', 'https') or not upstream.hostname
            or not re.fullmatch(r'[a-zA-Z0-9.-]+(?::[0-9]+)?', upstream.netloc)
            or upstream.path or upstream.query or upstream.fragment):
        raise ValueError('Registration upstream must be an HTTP(S) origin without a path')
    return config


def stage(destination, config):
    destination.mkdir(parents=True, exist_ok=False)
    source = destination / 'source'
    help_assets = destination / 'help'
    runtime = destination / 'registration'
    platform, docs = config['platform'], config['docs']
    hosts = {'docs.g2p.wverve.in': docs, 'g2p.wverve.in': platform, 'nigeriag2p.com': platform}
    hosts.update({f'g2p-{service}.wverve.in': host for service, host in config['services'].items()})
    host_pattern = re.compile(r'(?<![\w.-])(?:' + '|'.join(
        re.escape(host) for host in sorted(hosts, key=len, reverse=True)
    ) + r')(?![\w.-])')

    def copy(previous, target):
        target.parent.mkdir(parents=True, exist_ok=True)
        content = (LAB / previous).read_text(encoding='utf-8-sig')
        target.write_text(host_pattern.sub(lambda match: hosts[match[0]], content), encoding='utf-8')

    for name in ('build.py', 'verify.py', 'pages.json', 'site.css', 'site.js',
                 'visual_guides.py', 'diagrams.json', 'screenshots.json'):
        copy('platform-docs/' + name, source / 'platform-docs' / name)
    shutil.copytree(LAB / 'platform-docs/visuals', source / 'platform-docs/visuals')
    for name in ('nsipa-wordmark.svg', 'nsipa-symbol.svg'):
        copy('platform-docs/branding/' + name, source / 'platform-docs' / 'branding' / name)
    copy('knowledge/contextual-catalog.json', source / 'knowledge/contextual-catalog.json')
    copy('knowledge-seed.json', source / 'knowledge-seed.json')
    runtime_seed = runtime / 'knowledge-seed.json'
    runtime.mkdir()
    runtime_seed.write_bytes((source / 'knowledge-seed.json').read_bytes())
    copy('knowledge_management.py', runtime / 'knowledge_management.py')
    copy('knowledge_management.py', source / 'knowledge_management.py')
    copy('km_governance.py', runtime / 'km_governance.py')
    copy('km_governance.py', source / 'km_governance.py')
    copy('local_ai.py', runtime / 'local_ai.py')
    copy('ai/local-ai.js', runtime / 'static/local-ai.js')
    for name in ('knowledge-article.html', 'knowledge-library.html', 'knowledge-editor.html', 'knowledge-revision.html',
                 'knowledge-admin.html', 'knowledge-register.html', 'knowledge-checks.html'):
        copy('registration-ui/' + name, runtime / 'templates' / name)

    help_assets.mkdir()
    web = {'platform': f'https://{platform}', 'docs': f'https://{docs}',
           'services': {platform: 'g2p', **{host: service for service, host in config['services'].items()}}}
    (help_assets / 'knowledge-config.js').write_text(
        'window.NSIPAKnowledgeConfig = ' + json.dumps(web, ensure_ascii=True, sort_keys=True) + ';\n',
        encoding='utf-8',
    )
    (help_assets / 'knowledge-context.js').write_bytes(
        (LAB / 'knowledge/context.js').read_bytes() + b'\n' + (LAB / 'knowledge/contextual.js').read_bytes(),
    )
    (help_assets / 'knowledge-help.js').write_bytes((LAB / 'knowledge/contextual-help.js').read_bytes())
    (help_assets / 'knowledge-help.css').write_bytes((LAB / 'knowledge/help.css').read_bytes())
    version = sha256(b'\0'.join(file.read_bytes() for file in sorted(help_assets.iterdir()))).hexdigest()[:12]
    url = '/iqs-brand/docs-help/'
    tags = [f'<link rel="stylesheet" href="{url}knowledge-help.css?v={version}">']
    for name in ('knowledge-config', 'knowledge-context', 'knowledge-help'):
        tags.append(f'<script defer src="{url}{name}.js?v={version}"></script>')
    (destination / 'help-tags.html').write_text('\n'.join(tags) + '\n')
    (destination / 'nginx-help.conf').write_text(f"""location ^~ /iqs-brand/docs-help/ {{
    alias /srv/nsipa-knowledge/current/help/;
}}
location = /iqs-brand/knowledge {{
    limit_except GET {{ deny all; }}
    proxy_pass {config['registration_upstream']}/registration/api/knowledge?include_roles=1;
    proxy_set_header Host {platform};
    proxy_set_header Cookie "";
    proxy_set_header Authorization "";
    proxy_hide_header Set-Cookie;
    proxy_cache off;
}}
""")
    entries = read_seed(runtime / 'knowledge-seed.json')
    print(json.dumps({'release': str(destination), 'helpAssetVersion': version,
                      'docsOrigin': web['docs'], 'publicGuides': len(entries),
                      'contextualGuides': sum(bool(item.get('context_key')) for item in entries.values())}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path, help='New release directory')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a new release directory')
    stage(args.output, settings(args.config))
