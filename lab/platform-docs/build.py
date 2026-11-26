"""Build the service guides and the public NSIPA Knowledge Library."""

import argparse
import html
import json
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlencode, urlsplit
from urllib.request import urlopen
from xml.sax.saxutils import escape as xml_escape

from visual_guides import GuideVisuals


SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parent
sys.path.insert(0, str(ROOT))
from knowledge_management import reader_content
PLATFORM = 'https://g2p.wverve.in'
KNOWLEDGE = PLATFORM + '/registration/knowledge'
KNOWLEDGE_FEED = 'http://127.0.0.1:18081/registration/api/knowledge?include_roles=1'
TOPIC_SECTIONS = ('purpose', 'steps', 'requirements', 'next_step', 'issues')
AUDIENCES = {
    'all': 'All roles', 'citizen': 'Citizen', 'officer': 'Registration Officer',
    'verifier': 'Verification Officer', 'supervisor': 'Programme Supervisor',
}
PLATFORM_ARTICLES = {
    'platform-find-your-service': 'services',
    'nigeria-guide-platform-1': 'lifecycle',
    'nsipa-screen-platform-programme-analytics': 'analytics',
    'nsipa-screen-platform-partner-simulation': 'partners',
    'nsipa-screen-platform-mobile-collection-setup': 'offline-collection',
    'nsipa-screen-platform-territorial-intelligence': 'territorial-atlas',
    'nsipa-screen-platform-jos-pilot-demonstration': 'jos-family-support',
}
PBMS_APPROVALS = {
    'verification', 'approvals', 'finance', 'audit', 'ceo', 'decision-visible', 'flow-open',
    'flow-submit', 'flow-history', 'flow-returned', 'approval-comment', 'submission-comment',
    'supporting-doc', 'correction-reason',
}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def published_knowledge():
    # This is the anonymous feed. Its role filter includes all public audiences.
    with urlopen(KNOWLEDGE_FEED, timeout=15) as response:
        return json.load(response)


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def topic_chapter(topic, defaults):
    group, key = topic['group'], topic['key']
    if group == 'pbms':
        if 'reversal' in key or key.startswith(('corrective-payment', 'escalation-', 'reopened-case')):
            return 'reversals-and-exceptions'
        if key.startswith(('payment', 'flow-payment', 'partial-payment')) or key in {'flow-routing', 'sponsor-routing'}:
            return 'payment-and-reconciliation'
        if key in PBMS_APPROVALS or key.startswith(('flow-correct', 'flow-resubmit')):
            return 'pbms-approvals'
        if any(word in key for word in ('enrollment', 'disbursement', 'entitlement', 'cycle', 'lists')) or key == 'flow-export':
            return 'cycles-and-lists'
        if key == 'analytics':
            return 'analytics'
    if group == 'register':
        if key.startswith(('review-', 'duplicates')) or key in {'intake-queue', 'returned-intake', 'decision-note'}:
            return 'registry-review'
        if key == 'offline' or key.startswith('offline-'):
            return 'offline-collection'
    return defaults[group]


def article_chapter(article, defaults):
    module = article['module']
    stage = article['stage'].casefold()
    if module == 'pbms':
        if any(term in stage for term in ('bank', 'reconciliation', 'payments', 'disbursement')):
            return 'payment-and-reconciliation'
        if any(term in stage for term in ('approval', 'verification', 'list correction')):
            return 'pbms-approvals'
        if any(term in stage for term in ('eligibility', 'enrol', 'cycle', 'entitlement', 'benefit calculation')):
            return 'cycles-and-lists'
    if module == 'register' and any(term in stage for term in ('duplicate', 'audit', 'submit for approval')):
        return 'registry-review'
    if module == 'platform':
        if article['slug'].startswith('nsipa-screen-platform-sandbox-'):
            return 'phase-one'
        return PLATFORM_ARTICLES.get(article['slug'], defaults[module])
    return defaults[module]


class Documentation:
    def __init__(self, prefix, origin, knowledge=None):
        self.prefix = prefix
        self.origin = origin
        self.visuals = GuideVisuals(SOURCE, self.path() + 'assets/')
        self.groups = read_json(SOURCE / 'pages.json')
        self.chapters = {}
        self.topics = {}
        self.section = {}
        owners = {}
        for group in self.groups:
            for chapter in group['pages']:
                ref = chapter['id']
                if not re.fullmatch(r'[a-z0-9-]+', ref) or ref in self.chapters:
                    raise ValueError(f'Invalid or duplicate chapter {ref}')
                self.chapters[ref] = chapter
                self.section[ref] = group['name']
                for key in chapter.get('guides', []):
                    if key in owners:
                        raise ValueError(f'Duplicate topic owner {key}')
                    owners[key] = ref
                if 'app' in chapter:
                    parsed = urlsplit(chapter['app'])
                    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                        raise ValueError(f'Unexpected workspace for {ref}')

        if knowledge is None:
            knowledge = read_json(ROOT / 'knowledge-seed.json')
        self.modules = {item['id']: item['name'] for item in knowledge['modules']}
        self.load_topics(knowledge['articles'], owners)

        for chapter in self.chapters.values():
            if set(chapter.get('related', [])) - self.chapters.keys():
                raise ValueError(f"Invalid related chapter for {chapter['id']}")

    def load_topics(self, articles, owners):
        catalog = {}
        for topic in read_json(ROOT / 'knowledge' / 'contextual-catalog.json'):
            group, key = topic['group'], topic['key']
            context_key = f'context-{group}-{key}'
            if context_key in catalog:
                raise ValueError(f'Duplicate contextual guide {context_key}')
            catalog[context_key] = (f'topics/{group}/{key}', topic_chapter(topic, owners), topic['help_level'])

        public_slugs = set()
        contexts = set()
        for entry in articles:
            if entry.get('visibility', 'public') != 'public':
                continue
            module, article_slug = entry['module'], entry['slug']
            if module not in self.modules or module not in owners:
                raise ValueError(f'Unmapped knowledge service {module}')
            if article_slug in public_slugs or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', article_slug):
                raise ValueError(f'Invalid or duplicate article {article_slug}')
            public_slugs.add(article_slug)
            if entry['audience'] not in AUDIENCES or not entry['title'].strip() or not entry['purpose'].strip():
                raise ValueError(f'Incomplete guidance for {article_slug}')

            context_key = entry.get('context_key')
            if context_key in catalog:
                ref, parent, level = catalog[context_key]
                if entry.get('help_level') != level or entry.get('scope') != 'local_workflow':
                    raise ValueError(f'Mismatched contextual guidance for {context_key}')
                contexts.add(context_key)
            else:
                ref = f'library/{module}/{article_slug}'
                parent = article_chapter(entry, owners)
                level = 'upstream' if entry.get('scope') == 'upstream_reference' else 'library'

            if ref in self.topics or parent not in self.chapters:
                raise ValueError(f'Invalid documentation route for {article_slug}')
            self.topics[ref] = {**reader_content(entry), 'parent': parent, 'level': level}

        if missing := catalog.keys() - contexts:
            raise ValueError(f"Published contextual guidance is missing {', '.join(sorted(missing))}")

    def path(self, ref=''):
        return self.prefix + ('/' + ref if ref else '') + '/'

    def href(self, ref, label=None):
        return self.link(self.path(ref), label or self.chapters[ref]['title'])

    @staticmethod
    def link(url, label, attributes=''):
        return f'<a href="{html.escape(url)}"{attributes}>{html.escape(label)}</a>'

    def nav(self, page):
        rows = []
        for group in self.groups:
            links = []
            for chapter in group['pages']:
                ref = chapter['id']
                attr = ' aria-current="page"' if ref == page else ''
                links.append('<li>' + self.link(self.path(ref), chapter['title'], attr) + '</li>')
            rows.append(f'<div class="nav-group"><p>{html.escape(group["name"])}</p><ul>{"".join(links)}</ul></div>')
        home_attr = ' aria-current="page"' if page == '' else ''
        return '<nav id="doc-nav" class="sidebar" aria-label="Documentation">' + self.link(self.path(), 'Overview', home_attr) + ''.join(rows) + '</nav>'

    def shell(self, ref, title, description, content, headings=(), parent=None):
        home = ref == ''
        canonical = self.origin + self.path(ref)
        crumb = ''
        if not home:
            category = self.section.get(parent or ref, '')
            crumb = f'<nav class="crumb" aria-label="Breadcrumb">{self.href("", "Documentation")} <span aria-hidden="true">/</span> '
            crumb += self.href(parent) if parent else html.escape(category)
            crumb += '</nav>'
        toc = ''.join(f'<li>{self.link("#" + slug(h), h)}</li>' for h in headings)
        aside = f'<aside class="toc"><nav aria-label="On this page"><p>On this page</p><ul>{toc}</ul></nav></aside>' if toc else ''
        page = parent or ref
        return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · NSIPA Documentation</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{html.escape(canonical)}">
<link rel="icon" href="{self.path()}assets/symbol.svg">
<link rel="stylesheet" href="{self.path()}assets/site.css">
<script defer src="{self.path()}assets/site.js"></script>
</head><body data-search="{self.path()}search.json">
<a class="skip" href="#content">Skip to content</a>
<header class="header"><div class="header-content">
  <button class="mobile-menu" type="button" aria-expanded="false" aria-controls="doc-nav">Menu</button>
  <a class="brand" href="{self.path()}"><img src="{self.path()}assets/wordmark.svg" width="112" height="30" alt="NSIPA"><span>Documentation</span></a>
  <div class="header-actions">
    <button type="button" class="search-launch" aria-haspopup="dialog">Search <kbd>Ctrl K</kbd></button>
    <a class="platform" href="{PLATFORM}/">Open platform <span aria-hidden="true">↗</span></a>
  </div>
</div></header>
<div class="frame">{self.nav(page)}
<main id="content" tabindex="-1" class="article{' home' if home else ''}">
  {crumb}<h1>{html.escape(title)}</h1><p class="lead">{html.escape(description)}</p>{content}
  <footer class="foot"><a href="{KNOWLEDGE}">Knowledge Library</a><span>NSIPA G2P sandbox</span></footer>
</main>{aside}</div>
<dialog id="search-dialog" aria-labelledby="search-title">
  <div class="search-bar"><label for="search-input" id="search-title">Search documentation</label>
  <button type="button" class="close-search">Close</button></div>
  <input id="search-input" type="search" autocomplete="off" placeholder="Search by topic, role or task">
  <p id="search-status" role="status"></p><ul id="search-results"></ul>
</dialog></body></html>'''

    def cards(self, refs):
        cards = []
        for ref in refs:
            chapter = self.chapters[ref]
            label = html.escape(chapter['title'])
            text = html.escape(chapter['description'])
            cards.append(f'<a class="card" href="{self.path(ref)}"><strong>{label}<span aria-hidden="true">↗</span></strong><span>{text}</span></a>')
        return '<div class="cards">' + ''.join(cards) + '</div>'

    def page_section(self, label, body):
        return f'<section><h2 id="{slug(label)}">{html.escape(label)}</h2>{body}</section>'

    def topic_groups(self, guides, levels):
        groups = []
        for level, label in levels:
            entries = sorted((item for item in guides if item[1]['level'] == level),
                             key=lambda item: (item[1]['title'].casefold(), item[1]['audience'] != 'all', item[1]['audience']))
            if not entries:
                continue
            items = []
            for ref, topic in entries:
                role = '' if topic['audience'] == 'all' else f' <small>· {AUDIENCES[topic["audience"]]}</small>'
                items.append(f'<li>{self.link(self.path(ref), topic["title"])}{role}</li>')
            groups.append(f'<details class="topic-group"><summary>{label} <span>{len(entries)}</span></summary>'
                          f'<ul>{"".join(items)}</ul></details>')
        return ''.join(groups)

    def overview(self):
        names = ('Get started', 'Explore the documentation')
        notice = '<p class="notice">Sandbox documentation. Use synthetic records and follow approved agency procedures for operational decisions.</p>'
        journey = self.cards(['start', 'lifecycle'])
        featured = self.cards(['master-registry', 'data-imports', 'programme-setup', 'payment-and-reconciliation',
                               'beneficiary-portal', 'services'])
        art = self.visuals.illustration('household-interview', 'A resident and a registration officer review household details together.')
        body = art + self.visuals.diagram('lifecycle') + notice + self.page_section(names[0], journey) + self.page_section(names[1], featured)
        return self.shell('', 'Platform documentation',
                          'Find the steps for registration, Registry review, programme delivery and payment reconciliation.',
                          body, names)

    def chapter_page(self, chapter):
        ref = chapter['id']
        sections = {}
        if chapter.get('directory'):
            for group in self.groups:
                refs = [page['id'] for page in group['pages'] if page['id'] != ref]
                sections[group['name']] = self.cards(refs)
        else:
            for name, paragraphs in chapter.get('sections', {}).items():
                pictures = self.visuals.images['chapters'].get(ref, {})
                sections[name] = ''.join(f'<p>{html.escape(p)}</p>' + self.visuals.screenshots(pictures.get(p, ()))
                                         for p in paragraphs)
        if chapter.get('related'):
            sections['Related guides'] = '<ul>' + ''.join(f'<li>{self.href(rel)}</li>' for rel in chapter['related']) + '</ul>'
        guides = [(key, topic) for key, topic in self.topics.items() if topic['parent'] == ref]
        if contextual := self.topic_groups(guides, (('workflow', 'Workflow guides'), ('screen', 'Screen guides'),
                                                    ('field', 'Field reference'))):
            sections['Task and field reference'] = contextual
        if library := self.topic_groups(guides, (('library', 'Task and role articles'), ('upstream', 'Upstream references'))):
            sections['Knowledge Library articles'] = library
        open_link = self.link(chapter['app'], 'Open workspace ↗', ' class="workspace-link"') if chapter.get('app') else ''
        illustration = ''
        if ref in ('registration-review', 'registry-review'):
            illustration = self.visuals.illustration('independent-review', 'A reviewer compares the submitted household details with the supporting record.')
        elif ref == 'household-registration':
            illustration = self.visuals.illustration('household-interview', 'A resident answers the registration officer’s questions about her household.')
        body = open_link + illustration + self.visuals.diagram(ref)
        body += ''.join(self.page_section(k, v) for k, v in sections.items())
        order = list(self.chapters)
        index = order.index(ref)
        links = []
        for offset, label in ((-1, 'Previous'), (1, 'Next')):
            if 0 <= index + offset < len(order):
                adjacent = order[index + offset]
                links.append(f'<a href="{self.path(adjacent)}"><small>{label}</small>{html.escape(self.chapters[adjacent]["title"])}</a>')
        body += f'<nav class="page-order" aria-label="Read in order">{"".join(links)}</nav>'
        return self.shell(ref, chapter['title'], chapter['description'], body, sections)

    def topic_page(self, ref, topic):
        labels = {'steps':'Steps','requirements':'Before you start','next_step':'What happens next','issues':'Common issues'}
        sections = {}
        pictures = self.visuals.images['topics'].get(topic['slug'], {})
        for field, label in labels.items():
            text = topic.get(field, '').strip()
            if not text:
                continue
            if field == 'steps':
                steps = []
                for line in text.splitlines():
                    if line.strip():
                        photo = self.visuals.screenshots(pictures.get(line, ()))
                        steps.append(f'<li><span class="instruction">{html.escape(line)}</span>{photo}</li>')
                sections[label] = '<ol class="walkthrough" role="list">' + ''.join(steps) + '</ol>'
            else:
                sections[label] = '<p>' + html.escape(text) + '</p>'
        sources = []
        for source in topic.get('sources', []):
            url = urlsplit(source['url'])
            if url.scheme == 'https' and (url.hostname in ('docs.openg2p.org', 'g2p.wverve.in')
                                          or url.hostname == 'github.com' and url.path.startswith('/OpenG2P/openg2p-documentation/')):
                sources.append(f'<li>{self.link(source["url"], source["title"])}</li>')
        if sources:
            sections['References'] = f'<ul>{"".join(sources)}</ul>'
        if 'id' in topic:
            article = f'{KNOWLEDGE}/{topic["id"]}'
        else:
            article = KNOWLEDGE + '?' + urlencode({'q': topic['title'], 'module': topic['module'],
                                                     'audience': topic['audience']})
        body = ''
        if topic['level'] == 'upstream':
            body = '<p class="notice">Upstream reference. Confirm feature availability in the installed NSIPA release.</p>'
        if topic.get('provisional') or topic.get('context_key'):
            body += '<p class="notice">Provisional sandbox guidance · Business validation pending</p>'
        if topic['audience'] != 'all':
            body += f'<p>Guidance for {AUDIENCES[topic["audience"]]}s.</p>'
        body += self.visuals.screenshots(pictures.get('@purpose', ()))
        body += ''.join(self.page_section(k, v) for k, v in sections.items())
        if topic['level'] != 'upstream':
            diagram = self.visuals.topic_diagram(topic)
            if topic['level'] == 'workflow' or diagram != topic['parent']:
                body = self.visuals.diagram(diagram) + body
            elif not pictures:
                body += self.visuals.diagram(diagram)
            else:
                body += ('<details class="process-context"><summary>See how this fits into '
                         + html.escape(self.chapters[topic['parent']]['title'])
                         + '</summary>' + self.visuals.diagram(diagram) + '</details>')
        body += '<p class="source-links">' + self.href(topic['parent'], 'Back to service guide') + self.link(article, 'Open in Knowledge Library ↗') + '</p>'
        return self.shell(ref, topic['title'], topic['purpose'], body, sections, topic['parent'])

    def build(self, out):
        write(out / 'index.html', self.overview())
        search = []
        for key, chapter in self.chapters.items():
            write(out / key / 'index.html', self.chapter_page(chapter))
            search.append({'url':self.path(key),'title':chapter['title'],'description':chapter['description'],
                           'section':self.section[key],'body':' '.join(p for lines in chapter.get('sections',{}).values() for p in lines)})
        for ref, topic in self.topics.items():
            write(out / ref / 'index.html', self.topic_page(ref, topic))
            section = self.chapters[topic['parent']]['title']
            if topic['audience'] != 'all':
                section += ' · ' + AUDIENCES[topic['audience']]
            if topic['level'] == 'upstream':
                section += ' · Upstream reference'
            search.append({'url':self.path(ref),'title':topic['title'],'description':topic['purpose'],
                           'section':section,
                           'body':' '.join(topic.get(field, '') for field in (*TOPIC_SECTIONS, 'stage'))})
        write(out / 'search.json', json.dumps(search, ensure_ascii=False, separators=(',', ':')))
        urls = [self.origin + self.path()] + [self.origin + row['url'] for row in search]
        write(out / 'sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
              ''.join('<url><loc>' + xml_escape(url) + '</loc></url>' for url in urls) + '</urlset>')
        (out / 'assets').mkdir(exist_ok=True)
        shutil.copytree(SOURCE / 'visuals', out / 'assets' / 'visuals', dirs_exist_ok=True)
        for name in ('site.css','site.js'):
            shutil.copy2(SOURCE / name, out / 'assets' / name)
        for name in ('wordmark','symbol'):
            shutil.copy2(SOURCE / 'branding' / f'nsipa-{name}.svg', out / 'assets' / f'{name}.svg')
        contextual = sum(ref.startswith('topics/') for ref in self.topics)
        print(json.dumps({'chapters':len(self.chapters), 'contextual_topics':contextual,
                          'library_topics':len(self.topics)-contextual, 'pages':len(urls)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('--prefix', default='/docs')
    parser.add_argument('--origin', default=PLATFORM)
    parser.add_argument('--published', action='store_true', help='Build from the live public Knowledge Library')
    parser.add_argument('--knowledge-file', type=Path, help='Anonymous published Knowledge Library JSON export')
    args = parser.parse_args()
    if not re.fullmatch(r'(?:/[a-z0-9-]+)?', args.prefix):
        parser.error('Use an empty prefix or one lowercase directory')
    if args.published and args.knowledge_file:
        parser.error('Use one published Knowledge Library source')
    knowledge = published_knowledge() if args.published else read_json(args.knowledge_file) if args.knowledge_file else None
    docs = Documentation(args.prefix, args.origin.rstrip('/'), knowledge)
    docs.build(args.output)
    from verify import verify_build
    verify_build(docs, args.output)
