"""Check that published guidance can be found and read in the built site."""

from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import json
import subprocess
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree

from build import KNOWLEDGE, TOPIC_SECTIONS


class Page(HTMLParser):
    def __init__(self, contents):
        super().__init__()
        self.ids = set()
        self.links = set()
        self.canonicals = []
        self.in_main = False
        self.main_text = []
        self.instructions = []
        self.in_instruction = False
        self.feed(contents.decode('utf-8'))

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                raise ValueError(f'Duplicate anchor {attrs["id"]}')
            self.ids.add(attrs['id'])
        if tag == 'span' and attrs.get('class') == 'instruction':
            self.in_instruction = True
        if tag == 'source' and 'srcset' in attrs:
            self.links.add(attrs['srcset'])
        if tag == 'main':
            self.in_main = True
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs['href'])
        else:
            self.links.update(attrs[key] for key in ('href', 'src') if key in attrs)

    def handle_endtag(self, tag):
        if tag == 'span':
            self.in_instruction = False
        if tag == 'main':
            self.in_main = False

    def handle_data(self, data):
        if self.in_main:
            self.main_text.append(data)
            if self.in_instruction:
                self.instructions.append(data)


def collapsed(text):
    return ' '.join(text.split())


def verify_build(docs, root):
    files = {}
    for file in root.rglob('*'):
        if file.is_file():
            relative = file.relative_to(root).as_posix()
            path = docs.prefix + '/' + relative.removesuffix('index.html')
            files[path] = file.read_bytes()
    expected = {docs.path(ref) for ref in ('', *docs.chapters, *docs.topics)}
    pages = {path: Page(files[path]) for path in expected}
    if {path for path in files if path.endswith('/')} != expected:
        raise ValueError('The built page set differs from the service and guidance inventory')

    index = json.loads(files[docs.path() + 'search.json'])
    indexed = {entry['url']: entry for entry in index}
    if len(indexed) != len(index) or indexed.keys() != expected - {docs.path()}:
        raise ValueError('The search index does not contain every guide exactly once')
    sitemap = ElementTree.fromstring(files[docs.path() + 'sitemap.xml'])
    urls = [node.text for node in sitemap.findall('.//{*}loc')]
    if len(urls) != len(expected) or set(urls) != {docs.origin + path for path in expected}:
        raise ValueError('The sitemap does not contain every canonical page exactly once')

    host = urlsplit(docs.origin).netloc
    for path, page in pages.items():
        if page.canonicals != [docs.origin + path]:
            raise ValueError(f'Incorrect canonical link for {path}')
        for link in page.links:
            target = urlsplit(urljoin(docs.origin + path, link))
            if target.netloc != host or not target.path.startswith(docs.path()):
                continue
            if target.path not in files:
                raise ValueError(f'Broken link from {path} to {target.path}')
            if target.fragment and unquote(target.fragment) not in pages[target.path].ids:
                raise ValueError(f'Broken anchor from {path} to {link}')

    for ref, topic in docs.topics.items():
        path = docs.path(ref)
        if path not in pages[docs.path(topic['parent'])].links:
            raise ValueError(f'Missing link to {path} from its service chapter')
        if 'id' in topic and f'{KNOWLEDGE}/{topic["id"]}' not in pages[path].links:
            raise ValueError(f'Missing Knowledge Library link on {path}')
        content = collapsed(' '.join(pages[path].main_text))
        if topic.get('provisional') and 'Provisional sandbox guidance' not in content:
            raise ValueError(f'Missing provisional label for {path}')
        search = collapsed(indexed[path]['title'] + ' ' + indexed[path]['body'])
        for field in ('title', *TOPIC_SECTIONS, 'stage'):
            text = collapsed(topic.get(field, ''))
            displayed = collapsed(' '.join(pages[path].instructions)) if field == 'steps' else content
            if text and (text not in search or field != 'stage' and text not in displayed):
                raise ValueError(f'Missing {field} for {path}')
    return files


def fetch_public(url):
    data = subprocess.check_output([
        'curl', '-4', '--fail', '--silent', '--show-error', '--location',
        '--max-time', '12', '--retry', '2', '--write-out', '\n%{url_effective}', url,
    ])
    body, _, destination = data.rpartition(b'\n')
    return body, destination.decode('utf-8')


def verify_published(origin, files):
    def verify(item):
        path, expected = item
        url = origin + path
        body, destination = fetch_public(url)
        if body != expected or destination != url:
            raise RuntimeError(f'The public site served different content at {url}')

    with ThreadPoolExecutor(max_workers=8) as pool:
        for _ in pool.map(verify, files.items()):
            pass
