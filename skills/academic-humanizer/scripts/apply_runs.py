#!/usr/bin/env python3
"""
Academic Humanizer: Phase 4 Splicer (v7.2.0)

Splices rewritten runs back into a draft. Only the text of each run's
ORIGINAL block is replaced. Every other character of the draft is copied
through unchanged, so sentences the detector already passed cannot drift.
When --source is given, the result is checked with check_draft.py.

The runs file comes from `flagged_runs.py DRAFT FLAGGED --emit runs.txt`.

Usage:
  apply_runs.py DRAFT RUNS_FILE -o NEW_DRAFT [--source SOURCE] [--facts FACTS]

Exit codes: 0 ok, 1 checker failure, 2 a run could not be applied.
"""

import argparse
import re
import sys

from check_draft import check, format_report, segment

RUN_HEADER = re.compile(r'^=== RUN (\d+) ===\s*$', re.MULTILINE)


def parse_runs(text):
    """Returns [(run_number, original, rewrite)] from a runs file."""
    runs = []
    headers = list(RUN_HEADER.finditer(text))
    for k, h in enumerate(headers):
        body = text[h.end():headers[k + 1].start() if k + 1 < len(headers) else len(text)]
        original, rewrite, section = [], [], None
        for line in body.splitlines():
            if line.startswith('ORIGINAL:'):
                section = 'original'
                rest = line[len('ORIGINAL:'):].strip()
                if rest:
                    original.append(rest)
            elif line.startswith('REWRITE:'):
                section = 'rewrite'
                rest = line[len('REWRITE:'):].strip()
                if rest:
                    rewrite.append(rest)
            elif line.startswith(('CONTEXT BEFORE:', 'CONTEXT AFTER:')) or line.startswith('#'):
                if section == 'original':
                    section = None
            elif section == 'original':
                original.append(line.strip())
            elif section == 'rewrite':
                rewrite.append(line.strip())
        runs.append((int(h.group(1)), ' '.join(x for x in original if x), ' '.join(x for x in rewrite if x)))
    return runs


def _locate(draft, original):
    """Finds the single span of `original` in the draft, tolerating whitespace differences."""
    tokens = original.split()
    if not tokens:
        return None, 'empty ORIGINAL block'
    pattern = re.compile(r'\s+'.join(re.escape(t) for t in tokens))
    matches = list(pattern.finditer(draft))
    if len(matches) != 1:
        return None, f'ORIGINAL text found {len(matches)} times in the draft (need exactly 1)'
    return matches[0].span(), None


def splice(draft, runs):
    """Returns (new_draft, applied_numbers, errors). Runs with an empty REWRITE are left as they are."""
    spans, errors = [], []
    for number, original, rewrite in runs:
        if not rewrite:
            continue
        span, error = _locate(draft, original)
        if error:
            errors.append(f'Run {number}: {error}')
            continue
        spans.append((span, number, ' '.join(rewrite.split())))
    spans.sort()
    for prev, cur in zip(spans, spans[1:]):
        if cur[0][0] < prev[0][1]:
            errors.append(f'Runs {prev[1]} and {cur[1]} overlap')
    if errors:
        return draft, [], errors
    out, pos = [], 0
    for (a, b), _, rewrite in spans:
        out.append(draft[pos:a])
        out.append(rewrite)
        pos = b
    out.append(draft[pos:])
    return ''.join(out), [n for _, n, _ in spans], []


def _norm(text):
    return ' '.join(text.split())


def review_runs(runs, result):
    """Sorts checker findings into those inside rewritten runs (fix) and those outside (leave),
    and flags highlighted sentences that a rewrite copied unchanged."""
    rewrites = [_norm(r) for _, _, r in runs if r]
    inside, outside, general = [], [], []
    for f in result['findings']:
        if not f['where'] or f['where'].startswith('source'):
            general.append(f)
        elif any(_norm(f['text']) in r for r in rewrites):
            inside.append(f)
        else:
            outside.append(f)
    copied = []
    for number, original, rewrite in runs:
        if not rewrite:
            continue
        for s in segment(original):
            if len(s.text.split()) >= 4 and _norm(s.text) in _norm(rewrite):
                copied.append((number, s.text))
    return inside, outside, general, copied


def format_review(inside, outside, general, copied):
    lines = ['=== PHASE 4 REVIEW ===']
    if copied:
        lines.append('Highlighted sentences copied unchanged into a rewrite (rewrite them; they will be flagged again):')
        lines.extend(f'  Run {n}: "{s}"' for n, s in copied)
    lines.append(f'Warnings inside your rewrites (fix these): {len(inside)}')
    for f in inside:
        lines.append(f'  {f["level"]}  {f["kind"]}: {f["message"]}')
        lines.append(f'        "{f["text"][:110]}"')
    lines.append(f'Whole-document findings (fix failures; check hedge and drop warnings): {len(general)}')
    for f in general:
        where = f'  [{f["where"]}]' if f['where'] else ''
        lines.append(f'  {f["level"]}  {f["kind"]}: {f["message"]}{where}')
    lines.append(f'Warnings in sentences outside the runs: {len(outside)}. Those sentences already passed the '
                 'detector; leave them unchanged.')
    ok = not copied and not inside and not any(f['level'] == 'FAIL' for f in general)
    lines.append('PHASE 4 RESULT: ' + ('READY TO SCAN' if ok else 'REVISE runs.txt AND RUN AGAIN'))
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Academic Humanizer: Phase 4 Splicer (v7.2.0)')
    parser.add_argument('draft', help='The draft that was scanned')
    parser.add_argument('runs', help='Runs file with REWRITE slots filled in')
    parser.add_argument('-o', '--output', required=True, help='Where to write the new draft')
    parser.add_argument('--source', help='Original source text; when given, the new draft is checked against it')
    parser.add_argument('--facts', help='Fact sheet, passed to the checker')
    args = parser.parse_args(argv)

    with open(args.draft, encoding='utf-8') as f:
        draft = f.read()
    with open(args.runs, encoding='utf-8') as f:
        runs = parse_runs(f.read())

    new_draft, applied, errors = splice(draft, runs)
    if errors:
        print('Nothing written. Fix the runs file and try again:', file=sys.stderr)
        for e in errors:
            print(f'  {e}', file=sys.stderr)
        return 2
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(new_draft)
    skipped = [n for n, _, r in runs if not r]
    print(f'Applied runs: {", ".join(map(str, applied)) or "none"}'
          + (f'; left unchanged (empty REWRITE): {", ".join(map(str, skipped))}' if skipped else ''))
    print(f'Everything outside those runs is unchanged. Written to {args.output}')

    if not args.source:
        return 0
    with open(args.source, encoding='utf-8') as f:
        source = f.read()
    facts = ''
    if args.facts:
        with open(args.facts, encoding='utf-8') as f:
            facts = f.read()
    result = check(source, new_draft, facts)
    print()
    print(format_report(result))
    print()
    print(format_review(*review_runs(runs, result)))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
