#!/usr/bin/env python3
"""Normalize user-supplied SRT/VTT, Bilibili subtitle JSON or YouTube JSON3.

Does not download, authenticate, transcribe audio, or verify source truth.
"""
import argparse
import html
import json
import math
import re
from pathlib import Path


def seconds(text):
    values = text.replace(',', '.').split(':')
    if len(values) not in (2, 3):
        raise ValueError(f'invalid timestamp: {text}')
    values = [float(v) for v in values]
    total = 0
    for val in values:
        total = total * 60 + val
    return total


def clean(text):
    return html.unescape(re.sub(r'<[^>]+>', '', text)).strip()


def normalize(raw, suffix):
    raw = raw.lstrip('\ufeff')
    rows = []
    if suffix.lower() == '.json':
        obj = json.loads(raw)
        if isinstance(obj, dict) and 'body' in obj:
            rows = [{'start': r['from'], 'end': r['to'], 'text': r['content']} for r in obj['body']]
        elif isinstance(obj, dict) and 'events' in obj:
            for event in obj['events']:
                content = ''.join(s.get('utf8', '') for s in event.get('segs', []))
                if content.strip():
                    start = event['tStartMs'] / 1000
                    end = start + event['dDurationMs'] / 1000 if 'dDurationMs' in event else None
                    rows.append({'start': start, 'end': end, 'text': content})
        else:
            raise ValueError('supported JSON shapes: Bilibili body or YouTube events')
    else:
        # Works for SRT and VTT cue IDs, settings, multiline cues and BOM.
        timing = re.compile(r'(?P<start>(?:\d+:)?\d{2}:\d{2}[.,]\d{3})\s*-->\s*(?P<end>(?:\d+:)?\d{2}:\d{2}[.,]\d{3})[^\n]*\n(?P<text>.*?)(?=\n\s*\n|\Z)', re.S)
        normalized = raw.replace('\r\n', '\n').replace('\r', '\n')
        for m in timing.finditer(normalized):
            rows.append({'start': seconds(m['start']), 'end': seconds(m['end']), 'text': m['text']})
    if not rows:
        raise ValueError('no timed cues found; plain text needs explicit manual locator handling')
    result = []
    for row in rows:
        start = float(row['start'])
        end = float(row['end']) if row['end'] is not None else None
        if not math.isfinite(start) or start < 0 or (end is not None and (not math.isfinite(end) or end < start)):
            raise ValueError('invalid cue interval')
        text = clean(str(row['text']))
        if text:
            result.append({'start': start, 'end': end, 'text': text})
    if not result:
        raise ValueError('no nonempty cues')
    result.sort(key=lambda x: x['start'])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.resolve() == args.input.resolve():
            raise ValueError('output must differ from input')
        if args.output.exists():
            raise ValueError('output exists; select a new path to preserve prior data')
        cues = normalize(args.input.read_text(encoding='utf-8-sig'), args.input.suffix)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({'format_version': 1, 'verification': 'format_only', 'cues': cues}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'Normalized {len(cues)} cues; content accuracy and coverage unverified.')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
