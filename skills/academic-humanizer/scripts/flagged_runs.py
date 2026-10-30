#!/usr/bin/env python3
"""
Academic Humanizer: Phase 4 Detector-Feedback Helper (v7.12.0)

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

from check_draft import PLACEHOLDER, segment, strip_placeholders

MIN_PREFIX_CHARS = 12
# A LaTeX placeholder can stand for up to this many words of the compiled PDF ("[3]", "s t", "Fig. 2").
MAX_WILD_WORDS = 8
WILD = None
# Section numbers the compiled PDF adds to headings: "I.", "IV.", "2.", "2.1", "A."
ENUMERATOR = re.compile(r'^\s*(?:(?:[IVXLC]+|[A-Z])\.|\d+(?:\.\d+)*\.?)\s+(?=[A-Za-z])')


def _norm(text):
    return re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()


def _tokens(text):
    """Normalized words, with each kept-LaTeX placeholder as a wildcard. Pair markers stand for nothing."""
    closed = {m.group()[2:-1] for m in PLACEHOLDER.finditer(text) if m.group()[1] == '/'}
    out = []
    for part in re.split(r'(\u27e6/?\d+\u27e7)', text):
        if PLACEHOLDER.fullmatch(part):
            if part[1] != '/' and part[1:-1] not in closed:
                out.append(WILD)
        else:
            out.extend(_norm(part).split())
    return out


def _wild_match(key, sent, sentence_may_end):
    """True if the key's words start the sentence's words, a wildcard standing for a few words.
    With sentence_may_end, the sentence may also run out first (the key covers it and more).
    At least half of the key's words must match real words, not wildcards."""
    need = (len(key) + 1) // 2
    memo = {}

    def go(i, j, lit):
        lit = min(lit, need)
        if (i, j, lit) in memo:
            return memo[(i, j, lit)]
        if i == len(key):
            result = lit >= need
        elif j == len(sent):
            result = sentence_may_end and lit >= need
        elif sent[j] is WILD:
            result = any(go(i + k, j + 1, lit) for k in range(min(MAX_WILD_WORDS, len(key) - i) + 1))
        elif key[i] == sent[j]:
            result = go(i + 1, j + 1, lit + 1)
        else:   # the key's last word may be cut off
            result = i == len(key) - 1 and sent[j].startswith(key[i]) and lit + 1 >= need
        memo[(i, j, lit)] = result
        return result
    return go(0, 0, 0)


def match_flags(sentences, flagged_lines):
    """Returns one boolean per sentence, plus the flagged lines that matched no sentence."""
    keys = [_norm(ENUMERATOR.sub('', line)) for line in flagged_lines]
    keys = [k for k in keys if len(k) >= MIN_PREFIX_CHARS]
    texts = [ENUMERATOR.sub('', s.text) for s in sentences]
    norm_sentences = [_norm(strip_placeholders(t)) for t in texts]
    wild = [_tokens(t) if PLACEHOLDER.search(t) else None for t in texts]
    flags = [False] * len(sentences)
    unmatched = []
    for key in keys:
        words = key.split()

        def starts(i, s):
            if wild[i] is not None:
                return _wild_match(words, wild[i], len(s) >= MIN_PREFIX_CHARS)
            return s.startswith(key) or key.startswith(s) and len(s) >= MIN_PREFIX_CHARS

        def contains(i, s):
            if wild[i] is not None:
                return any(_wild_match(words, wild[i][j:], False) for j in range(len(wild[i])))
            return key in s

        hits = [i for i, s in enumerate(norm_sentences) if starts(i, s)]
        if not hits:
            hits = [i for i, s in enumerate(norm_sentences) if contains(i, s)]
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
# Markers like ⟦12⟧ hold LaTeX code: keep each one exactly once, in place. Reword the text
# between a pair ⟦12⟧...⟦/12⟧ and keep both markers.
"""


def rewritable_units(draft):
    """Every unit Phase 4 may rewrite: prose sentences, formula lines and section headings.
    Only the paper's title (a heading in the first paragraph) is left out."""
    return [s for s in segment(draft) if not (s.heading and s.para == 1)]


def runs_file(draft, flagged_lines, gap=1):
    """Builds the fill-in runs file for apply_runs.py."""
    sentences = rewritable_units(draft)
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
    sentences = rewritable_units(draft)
    flags, unmatched = match_flags(sentences, flagged_lines)
    runs = find_runs(sentences, flags, gap)
    words = [len(strip_placeholders(s.text).split()) for s in sentences]
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
    parser = argparse.ArgumentParser(description='Academic Humanizer: Phase 4 Detector-Feedback Helper (v7.12.0)')
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
