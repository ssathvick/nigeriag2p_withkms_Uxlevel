"""Preview or apply a published NSIPA guidance release to an existing Knowledge Library."""

import argparse
from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3


FIELDS = {
    'module', 'stage', 'audience', 'title', 'purpose', 'steps', 'requirements', 'next_step', 'issues',
}
METADATA = {'sources', 'sources_checked_on', 'scope', 'help_level', 'context_key', 'source_note', 'provisional'}
ACTOR = 'system:nsipa-docs-help-release'


def read_seed(path):
    seed = json.loads(path.read_text(encoding='utf-8-sig'))
    entries = {}
    contexts = set()
    for article in seed['articles']:
        if article.get('visibility', 'public') != 'public':
            raise ValueError('The release seed must contain only public guidance')
        slug = article['slug']
        context_key = article.get('context_key')
        if slug in entries or context_key in contexts or not FIELDS <= article.keys():
            raise ValueError(f'Duplicate or incomplete release article {slug}')
        if context_key:
            contexts.add(context_key)
        entries[slug] = {'visibility': 'public', **{key: val for key, val in article.items() if key in FIELDS | METADATA}}
    return entries


def merge(connection, entries):
    connection.row_factory = sqlite3.Row
    existing = {row['slug']: row for row in connection.execute('SELECT * FROM km_articles')}
    context_owners = {}
    for slug, row in existing.items():
        for raw in (row['published'], row['draft']):
            if raw and (key := json.loads(raw).get('context_key')):
                context_owners.setdefault(key, set()).add(slug)
    for slug, item in entries.items():
        if item.get('context_key') and context_owners.get(item['context_key'], {slug}) != {slug}:
            raise ValueError(f'Context key for {slug} belongs to another local article. Reconcile the slugs first.')

    counts = Counter({'inserted': 0, 'updated': 0, 'unchanged': 0, 'preserved': 0})
    now = datetime.now(timezone.utc).isoformat(timespec='seconds')
    for slug, content in entries.items():
        attributes = (content['module'], content['stage'], content['audience'])
        row = existing.get(slug)
        if row:
            previous = json.loads(row['published']) if row['published'] else {}
            if (row['status'] != 'published' or not row['published'] or row['draft'] != row['published']
                    or previous.get('visibility', 'public') != 'public' or not row['author'].startswith('system:')
                    or (row['reviewer'] and not row['reviewer'].startswith('system:'))):
                counts['preserved'] += 1
                continue
            content = {**previous, **content}
            if previous == content:
                counts['unchanged'] += 1
                continue
            payload = json.dumps(content, ensure_ascii=False, sort_keys=True)
            article, version = row['id'], row['version'] + 1
            connection.execute(
                'UPDATE km_articles SET module=?,stage=?,audience=?,draft=?,published=?,version=?,'
                'published_version=?,author=?,reviewer=NULL,updated=? WHERE id=?',
                (*attributes, payload, payload, version, version, ACTOR, now, article),
            )
            action = 'docs_help_refreshed'
            counts['updated'] += 1
        else:
            payload = json.dumps(content, ensure_ascii=False, sort_keys=True)
            article = connection.execute(
                "INSERT INTO km_articles(slug,module,stage,audience,draft,version,status,author,published,published_version,updated)"
                " VALUES(?,?,?,?,?,1,'published',?,?,1,?)", (slug, *attributes, payload, ACTOR, payload, now),
            ).lastrowid
            version = 1
            action = 'docs_help_added'
            counts['inserted'] += 1
        connection.execute(
            'INSERT INTO km_history(article,version,action,actor,at,content,note) VALUES(?,?,?,?,?,?,?)',
            (article, version, action, ACTOR, now, payload, 'Published sandbox guidance release'),
        )
    return dict(counts)


def run(database, seed, backup=None):
    entries = read_seed(seed)
    mode = 'rw' if backup else 'ro'
    with closing(sqlite3.connect(database.resolve().as_uri() + '?mode=' + mode, uri=True)) as source:
        if not source.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='km_articles'").fetchone():
            raise ValueError('Initialize the Knowledge Library schema with the registration service first')
        if backup is None:
            with closing(sqlite3.connect(':memory:')) as target, target:
                source.backup(target)
                return merge(target, entries)
        with os.fdopen(os.open(backup, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), 'wb'):
            pass
        with closing(sqlite3.connect(backup)) as target:
            source.backup(target)
        with source:
            source.execute('BEGIN IMMEDIATE')
            return merge(source, entries)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', required=True, type=Path)
    parser.add_argument('--seed', required=True, type=Path)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--backup', type=Path, help='New private SQLite backup path')
    args = parser.parse_args()
    if args.apply != bool(args.backup):
        parser.error('--apply and --backup must be used together')
    print(json.dumps({'applied': args.apply, **run(args.database, args.seed, args.backup)}, indent=2))
