#!/usr/bin/env python3
"""Validate the published source/method graph and portable local references."""
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / 'skills' / 'kaogong-coach' / 'references'
LEVELS = {'transcript', 'video_sample', 'article_body', 'description_only', 'search_only', 'unavailable'}


def check(sources, methods, root=ROOT):
    errors = []
    ids = [x.get('id') for x in sources]
    if len(ids) != len(set(ids)):
        errors.append('duplicate source IDs')
    urls = [x.get('url') for x in sources]
    if len(urls) != len(set(urls)):
        errors.append('duplicate source URLs')
    by_id = {x.get('id'): x for x in sources}
    for s in sources:
        for key in ['id', 'platform', 'url', 'title', 'uploader', 'identity_status', 'evidence_level', 'read_scope', 'accessed_at', 'limitations']:
            if key not in s or not s[key]:
                errors.append(f'{s.get("id")}: missing {key}')
        if s.get('evidence_level') not in LEVELS:
            errors.append(f'{s.get("id")}: invalid evidence level')
        url = urlparse(s.get('url', ''))
        if url.scheme != 'https' or not url.netloc:
            errors.append(f'{s.get("id")}: invalid https URL')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', s.get('accessed_at', '')):
            errors.append(f'{s.get("id")}: invalid accessed_at')
        if s.get('evidence_level') == 'video_sample' and not s.get('observations'):
            errors.append(f'{s.get("id")}: sample lacks observations')
    mids = [m.get('id') for m in methods]
    if len(mids) != len(set(mids)):
        errors.append('duplicate method IDs')
    for m in methods:
        for key in ['id', 'name', 'module', 'status', 'attribution', 'triggers', 'limits']:
            if not m.get(key):
                errors.append(f'{m.get("id")}: missing {key}')
        if m.get('status') not in {'source_verified', 'original_design', 'candidate'}:
            errors.append(f'{m.get("id")}: invalid status')
        if m.get('status') != 'candidate' and (not m.get('steps') or not m.get('example', {}).get('answer')):
            errors.append(f'{m.get("id")}: executable method lacks steps/example')
        if m.get('status') == 'source_verified' and not m.get('evidence'):
            errors.append(f'{m.get("id")}: verified method lacks evidence')
        if m.get('status') == 'original_design' and m.get('attribution') != '本项目原创教学设计':
            errors.append(f'{m.get("id")}: original method attribution mismatch')
        for e in m.get('evidence', []):
            s = by_id.get(e.get('source_id'))
            if s is None:
                errors.append(f'{m.get("id")}: unknown source {e.get("source_id")}')
            if not e.get('locator') or not e.get('support'):
                errors.append(f'{m.get("id")}: incomplete evidence locator/support')
            if m.get('status') == 'source_verified' and s and s.get('evidence_level') in {'search_only', 'unavailable'}:
                errors.append(f'{m.get("id")}: unsupported promotion of discovery to method')
    for file in root.rglob('*.md'):
        if '.git' in file.parts:
            continue
        for target in re.findall(r'\]\(([^)]+)\)', file.read_text(encoding='utf-8')):
            target = target.strip('<>')
            if '://' in target or target.startswith('#'):
                continue
            dest = unquote(target.split('#')[0])
            if dest and not (file.parent / dest).exists():
                errors.append(f'{file.relative_to(root)}: broken local link {target}')
    return errors


def main():
    sources = json.loads((REFS / 'sources.json').read_text(encoding='utf-8'))['sources']
    methods = json.loads((REFS / 'methods.json').read_text(encoding='utf-8'))['methods']
    errors = check(sources, methods)
    print(json.dumps({'sources': len(sources), 'methods': len(methods),
                      'evidence_levels': dict(Counter(s['evidence_level'] for s in sources)),
                      'method_statuses': dict(Counter(m['status'] for m in methods)),
                      'errors': errors}, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
