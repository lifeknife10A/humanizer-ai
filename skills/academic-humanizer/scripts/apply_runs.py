#!/usr/bin/env python3
"""
Academic Humanizer: Phase 4 Splicer (v7.6.0)

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

from check_draft import (HEDGE_CLASSES, LIST_MARKER_LINE, MUST, _is_formula, _stems, check, format_report,
                         segment)

# Rewrites that cleared ZeroGPT runs kept at most 79% of each highlighted sentence's
# words (typically 42-50%); near-copies at 80% or more were flagged again.
BARELY_CHANGED = 0.8
# The 5.3% round included an 18-word sentence, so slightly long sentences inside a rewrite
# are reported but don't block READY TO SCAN.
LONG_SENTENCE_SLACK = 20

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
                rewrite.append(line.rstrip())
        runs.append((int(h.group(1)), ' '.join(x for x in original if x), _join_rewrite(rewrite)))
    return runs


def _join_rewrite(lines):
    """Joins REWRITE lines into prose, but keeps bullet and formula lines on lines of their own."""
    out = []
    for line in lines:
        if not line.strip():
            continue
        if out and not (LIST_MARKER_LINE.match(line) or _is_formula(line)) and not _is_formula(out[-1]):
            out[-1] += ' ' + line.strip()
        else:
            out.append(line if LIST_MARKER_LINE.match(line) else line.strip())
    return '\n'.join(' '.join(l.split()) if not LIST_MARKER_LINE.match(l)
                     else re.match(r'\s*', l).group(0) + ' '.join(l.split()) for l in out)


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
        spans.append((span, number, rewrite))
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


def _words(text):
    return set(re.findall(r'[a-z0-9]+', text.lower()))


def hedge_changes(before, after):
    """Hedge kinds the splice lost, and whether it added a 'must', comparing the scanned draft to the new one."""
    lost = []
    for kind, pattern in HEDGE_CLASSES.items():
        a = len(re.findall(pattern, before, re.IGNORECASE))
        b = len(re.findall(pattern, after, re.IGNORECASE))
        if b < a:
            lost.append(f'{kind} hedges went from {a} to {b}')
    if len(MUST.findall(after)) > len(MUST.findall(before)):
        lost.append('a "must" was added')
    return lost


ORDINALS = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']


def broken_enumerations(text):
    """Paragraphs where an ordinal appears without the one before it ("Third, ..." with no "second")."""
    broken = []
    for p, para in enumerate([p for p in re.split(r'\n\s*\n', text) if p.strip()], 1):
        present = {o for o in ORDINALS if re.search(rf'\b{o}\b', para, re.IGNORECASE)}
        has_next = bool(re.search(r'\bnext\b', para, re.IGNORECASE))  # "Next come..." stands in for an ordinal
        for k, o in enumerate(ORDINALS[1:], 1):
            if o in present and ORDINALS[k - 1] not in present and not has_next:
                broken.append((p, o, ORDINALS[k - 1]))
    return broken


def enumeration_changes(before, after):
    """Enumeration breaks the splice introduced."""
    old = set(broken_enumerations(before))
    return [f'paragraph {p}: "{o}" is left without "{prev}"' for p, o, prev in broken_enumerations(after)
            if (p, o, prev) not in old]


def run_meaning_changes(runs):
    """Per run: hedges or limiters the rewrite lost (blocking) and content words it dropped (to check)."""
    lost, dropped = [], []
    for number, original, rewrite in runs:
        if not rewrite:
            continue
        for kind, pattern in HEDGE_CLASSES.items():
            before = [m.lower() for m in re.findall(pattern, original, re.IGNORECASE)]
            after = len(re.findall(pattern, rewrite, re.IGNORECASE))
            if after < len(before):
                lost.append(f'Run {number}: {kind} words went from {len(before)} to {after} '
                            f'(original has: {", ".join(before)})')
        gone = sorted(_stems(original) - _stems(rewrite))
        if gone:
            dropped.append(f'Run {number}: {", ".join(gone)}')
    return lost, dropped


def review_runs(runs, result):
    """Sorts checker findings into those inside rewritten runs (fix) and those outside (leave),
    and flags highlighted sentences that a rewrite barely changed."""
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
        new_sentences = [_words(s.text) for s in segment(rewrite)]
        for s in segment(original):
            w = _words(s.text)
            if len(w) < 4 or not new_sentences:
                continue
            overlap = max(len(w & n) / len(w | n) for n in new_sentences)
            if overlap >= BARELY_CHANGED:
                copied.append((number, s.text, overlap))
    return inside, outside, general, copied


def _minor(finding):
    return finding['kind'] == 'long-sentence' and len(finding['text'].split()) <= LONG_SENTENCE_SLACK


def format_review(inside, outside, general, copied, hedges=(), meaning=((), ()), enumerations=()):
    lines = ['=== PHASE 4 REVIEW ===']
    if copied:
        lines.append(f'Highlighted sentences barely changed (rewrite keeps {BARELY_CHANGED:.0%}+ of their words; '
                     'restructure them, or they will be flagged again):')
        lines.extend(f'  Run {n}: {o:.0%} kept: "{s}"' for n, s, o in copied)
    lost, dropped = meaning
    if hedges or lost:
        lines.append('Hedges or limiting words lost in your rewrites (restore them; dropping "some", '
                     '"strongly", "may" or "only" overclaims):')
        lines.extend(f'  {h}' for h in list(lost) + list(hedges))
    if enumerations:
        lines.append('Enumerations broken by your rewrites (a later ordinal remains outside the run; '
                     'keep "first"/"second" in the rewrite):')
        lines.extend(f'  {e}' for e in enumerations)
    if dropped:
        lines.append('Word stems in a run\'s ORIGINAL that its rewrite no longer has. Synonyms are fine; '
                     'make sure no claim, item or qualifier went missing:')
        lines.extend(f'  {d}' for d in dropped)
    blocking = [f for f in inside if not _minor(f)]
    lines.append(f'Warnings inside your rewrites (fix these): {len(blocking)}')
    for f in blocking:
        lines.append(f'  {f["level"]}  {f["kind"]}: {f["message"]}')
        lines.append(f'        "{f["text"][:110]}"')
    for f in inside:
        if _minor(f):
            lines.append(f'  note (not blocking): {f["kind"]}: {f["message"]}')
    lines.append(f'Whole-document findings (fix failures; check hedge and drop warnings): {len(general)}')
    for f in general:
        where = f'  [{f["where"]}]' if f['where'] else ''
        lines.append(f'  {f["level"]}  {f["kind"]}: {f["message"]}{where}')
    lines.append(f'Warnings in sentences outside the runs: {len(outside)}. Those sentences already passed the '
                 'detector; leave them unchanged.')
    ok = (not copied and not hedges and not lost and not enumerations and not blocking
          and not any(f['level'] == 'FAIL' for f in general))
    lines.append('PHASE 4 RESULT: ' + ('READY TO SCAN' if ok else 'REVISE runs.txt AND RUN AGAIN'))
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Academic Humanizer: Phase 4 Splicer (v7.6.0)')
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
    print(format_review(*review_runs(runs, result), hedges=hedge_changes(draft, new_draft),
                        meaning=run_meaning_changes(runs), enumerations=enumeration_changes(draft, new_draft)))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
