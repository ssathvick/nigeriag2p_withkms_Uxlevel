"""Render the diagrams and screenshot callouts shared by the static guides."""
import html
import json


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


class GuideVisuals:
    def __init__(self, source, asset_url):
        self.url = asset_url + 'visuals/'
        self.images = read(source / 'screenshots.json')
        self.maps = read(source / 'diagrams.json')

    def screenshots(self, keys):
        figures = []
        for key in keys:
            photo = self.images['screens'][key]
            caption = html.escape(photo['caption'])
            url = self.url + key
            phone = ''
            if 'phone' in photo:
                w, h = photo['phone']
                phone = (f'<source media="(max-width: 600px)" srcset="{url}-phone.webp" '
                         f'width="{w}" height="{h}">')
            figures.append(
                f'<figure class="screen-example"><a class="screen-link" href="{url}.webp" '
                f'aria-label="Enlarge screenshot. {caption}"><picture>{phone}'
                f'<img src="{url}.webp" width="{photo["width"]}" height="{photo["height"]}" '
                f'loading="lazy" decoding="async" alt="{caption}"></picture>'
                '<span class="zoom-label" aria-hidden="true">Enlarge screenshot</span></a>'
                f'<figcaption>{caption}</figcaption></figure>')
        if len(figures) > 2:
            return (figures[0] + '<details class="more-examples"><summary>'
                    + f'Show {len(figures) - 1} more screenshots</summary>'
                    + ''.join(figures[1:]) + '</details>')
        return ''.join(figures)

    def diagram(self, key):
        diagram = self.maps[key]
        parallel = diagram.get('parallel', False)
        tag = 'ul' if parallel else 'ol'
        items = ''.join(f'<li><strong>{html.escape(label)}</strong><span>{html.escape(text)}</span></li>'
                        for label, text in diagram['nodes'])
        return (f'<figure class="process-map{" choices" if parallel else ""}">'
                f'<figcaption>{html.escape(diagram["title"])}</figcaption>'
                f'<{tag} role="list">{items}</{tag}></figure>')

    def illustration(self, key, alt):
        url = self.url + key
        return (f'<picture class="guide-art"><source media="(max-width: 600px)" srcset="{url}-phone.webp">'
                f'<img src="{url}.webp" width="920" height="518" alt="{html.escape(alt)}" decoding="async"></picture>')

    def topic_diagram(self, topic):
        key = topic['slug']
        if key.startswith('context-register-duplicates'):
            return 'duplicate-check'
        if key.startswith('context-pbms-payment-report-reversal-mismatch'):
            return 'reversal-count-check'
        if key in ('context-pbms-flow-routing', 'context-pbms-sponsor-routing'):
            return 'sponsor-route'
        if key == 'context-pbms-escalation-case-closure-workflow':
            return 'case-closure'
        if key == 'knowledge-review-and-publication':
            return 'publish-guidance'
        if key.startswith('context-imports-'):
            if 'receipt-log-' in key:
                return 'missing-log'
            if key.endswith(('shared-fetch', 'choose-fetch')):
                return 'separate-import'
        if key.startswith('context-pbms-'):
            if 'partial' in key:
                return 'partial-payment'
            if any(word in key for word in ('correction', 'resubmit', 'flow-returned', 'flow-correct')):
                return 'returned-list'
        return topic['parent']
