#!/usr/bin/env python3
"""
Academic Humanizer: Phase 4 Detector-Feedback Helper (v7.5.0)

Groups the sentences a detector highlighted (e.g. ZeroGPT's yellow spans)
into runs, so they can be rewritten as units. Detectors such as ZeroGPT
appear to score windows of text: in our labelled data a sentence right after
a flagged one was flagged 69% of the time, against 14% otherwise. Fixing one
sentence inside a run rarely clears it.

FLAGGED is a text file with one highlighted sentence per line. A line may be
the whole sentence or just its opening words; matching is by prefix, ignoring
case, spacing and punctuation.

Usage:
  flagged_runs.py DRAFT FLAGGED [--gap 1] [--emit runs.txt]

With --emit, it also writes a runs file: one block per run with the run's
ORIGINAL text and an empty REWRITE slot. Fill in the REWRITE slots and splice
them back with apply_runs.py, which leaves every other sentence untouched.
"""

import argparse
import re
import sys

from check_draft import segment

MIN_PREFIX_CHARS = 12


def _norm(text):
    return re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()


def match_flags(sentences, flagged_lines):
    """Returns one boolean per sentence, plus the flagged lines that matched no sentence."""
    keys = [_norm(line) for line in flagged_lines if len(_norm(line)) >= MIN_PREFIX_CHARS]
    norm_sentences = [_norm(s.text) for s in sentences]
    flags = [False] * len(sentences)
    unmatched = []
    for key in keys:
        hits = [i for i, s in enumerate(norm_sentences) if s.startswith(key) or key.startswith(s) and len(s) >= MIN_PREFIX_CHARS]
        if not hits:
            hits = [i for i, s in enumerate(norm_sentences) if key in s]
        if hits:
            for i in hits:
                flags[i] = True
        else:
            unmatched.append(key)
    return flags, unmatched


def find_runs(sentences, flags, gap=1):
    """Groups flagged sentences into runs, bridging up to `gap` unflagged sentences in one paragraph."""
    runs, current, last = [], [], None
    for i, (s, flagged) in enumerate(zip(sentences, flags)):
        if not flagged:
            continue
        if current and last is not None and s.para == sentences[last].para and i - last - 1 <= gap:
            current.extend(range(last + 1, i + 1))
        else:
            if current:
                runs.append(current)
            current = [i]
        last = i
    if current:
        runs.append(current)
    return runs


RUNS_FILE_HEADER = """# Phase 4 runs file.
# Write each run's rewrite on the lines under its REWRITE: line.
# Leave a REWRITE empty to keep that run as it is.
# Do not edit ORIGINAL blocks: apply_runs.py uses them to find each run in the draft.
# CONTEXT lines are for reading only; those sentences are not changed.
"""


def runs_file(draft, flagged_lines, gap=1):
    """Builds the fill-in runs file for apply_runs.py."""
    sentences = [s for s in segment(draft) if not s.heading]
    flags, _ = match_flags(sentences, flagged_lines)
    blocks = [RUNS_FILE_HEADER]
    for n, run in enumerate(find_runs(sentences, flags, gap), 1):
        first, last = run[0], run[-1]
        para = sentences[first].para
        blocks.append(f'=== RUN {n} ===')
        if first > 0 and sentences[first - 1].para == para:
            blocks.append(f'CONTEXT BEFORE: {sentences[first - 1].text}')
        blocks.append('ORIGINAL:')
        blocks.append(' '.join(sentences[i].text for i in run))
        if last + 1 < len(sentences) and sentences[last + 1].para == para:
            blocks.append(f'CONTEXT AFTER: {sentences[last + 1].text}')
        blocks.append('REWRITE:')
        blocks.append('')
    return '\n'.join(blocks) + '\n'


def report(draft, flagged_lines, gap=1):
    sentences = [s for s in segment(draft) if not s.heading]
    flags, unmatched = match_flags(sentences, flagged_lines)
    runs = find_runs(sentences, flags, gap)
    words = [len(s.text.split()) for s in sentences]
    total = sum(words) or 1
    flagged_words = sum(w for w, f in zip(words, flags) if f)

    lines = ['=== DETECTOR FEEDBACK ===',
             f'Flagged sentences: {sum(flags)} of {len(sentences)}',
             f'Flagged share of words: {flagged_words / total * 100:.1f}% '
             '(ZeroGPT\'s score tracks this closely)',
             f'Runs to rewrite: {len(runs)}', '']
    for n, run in enumerate(runs, 1):
        first, last = run[0], run[-1]
        para = sentences[first].para
        lines.append(f'--- Run {n} (paragraph {para}, sentences {sentences[first].index}-{sentences[last].index}, '
                     f'{sum(words[i] for i in run)} words) ---')
        if first > 0 and sentences[first - 1].para == para:
            lines.append(f'  before (keep): {sentences[first - 1].text}')
        for i in run:
            tag = 'FLAGGED' if flags[i] else 'between'
            lines.append(f'  {tag}: {sentences[i].text}')
        if last + 1 < len(sentences) and sentences[last + 1].para == para:
            lines.append(f'  after (keep): {sentences[last + 1].text}')
        lines.append('')
    if unmatched:
        lines.append('Flagged lines that matched no sentence (check for typos):')
        lines.extend(f'  {u}' for u in unmatched)
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Academic Humanizer: Phase 4 Detector-Feedback Helper (v7.5.0)')
    parser.add_argument('draft', help='The draft that was scanned')
    parser.add_argument('flagged', help='File with one highlighted sentence (or its opening words) per line')
    parser.add_argument('--gap', type=int, default=1, help='Unflagged sentences to bridge inside a run (default 1)')
    parser.add_argument('--emit', metavar='RUNS_FILE', help='Also write a fill-in runs file for apply_runs.py')
    args = parser.parse_args(argv)
    with open(args.draft, encoding='utf-8') as f:
        draft = f.read()
    with open(args.flagged, encoding='utf-8') as f:
        flagged = [line.strip() for line in f if line.strip()]
    print(report(draft, flagged, args.gap))
    if args.emit:
        with open(args.emit, 'w', encoding='utf-8') as f:
            f.write(runs_file(draft, flagged, args.gap))
        print(f'Runs file written to {args.emit}. Fill in each REWRITE, then run apply_runs.py.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
