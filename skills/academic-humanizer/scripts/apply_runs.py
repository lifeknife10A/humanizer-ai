#!/usr/bin/env python3
"""
Academic Humanizer: Phase 4 Splicer (v7.1.0)

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

from check_draft import check, format_report

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


def main(argv=None):
    parser = argparse.ArgumentParser(description='Academic Humanizer: Phase 4 Splicer (v7.1.0)')
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
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
