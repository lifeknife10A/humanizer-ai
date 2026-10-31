#!/usr/bin/env python3
"""
Academic Humanizer v8.0 — Register-Lowering Lexicon (research prototype)

Empirical Ablation Study 1 (research/EMPIRICAL_ABLATION_STUDY_1.md) showed that
sentence splitting alone does not move Turnitin (75% -> 77%); the lever in the
passing Clever-AI draft was **lexical register lowering** — replacing inflated,
high-probability LLM vocabulary with plain, direct words. This module is a
deterministic, auditable version of that: a conservative inflated -> plain
dictionary applied with word-boundary matching.

What it is NOT: a paper-specific bigram list (that is whack-a-mole). The map holds
only *generic* inflated words/phrases that are meaning-preserving in academic
prose. It is a SEED — extend it, and review every addition by hand.

Fidelity by construction:
  - No number is ever in the map, so numbers can't change (H1).
  - Keys are generic lowercase words; acronyms, formulas, and named/domain terms
    are never map keys, so they are left alone (H2). Word-boundary matching means
    a key never fires inside a longer token.
  - Replacements are plain lowercase words, so no new acronym/formula is created.
  - The original capitalization of each match is preserved.

Caveat: a lexical swap is the one transform that can shift nuance in a way the
number checker cannot catch ("mitigate"->"reduce" is safe; a domain term must
never be mapped). Keep the map conservative and human-reviewed. Run the output
through check_draft.py and re-read it.

Usage:
  register_lexicon.py INPUT.txt [-o OUT.txt] [--report]
"""

import argparse
import re
import sys

# Conservative, meaning-preserving, GENERIC swaps only. Keys are lowercase.
# Grouped by lemma; inflections included where the plain form stays grammatical.
LEXICON = {
    # verbs of using / doing
    'utilize': 'use', 'utilizes': 'uses', 'utilized': 'used', 'utilizing': 'using',
    'utilization': 'use',
    'leverage': 'use', 'leverages': 'uses', 'leveraging': 'using',
    'facilitate': 'help', 'facilitates': 'helps', 'facilitated': 'helped',
    'demonstrate': 'show', 'demonstrates': 'shows', 'demonstrated': 'showed',
    'demonstrating': 'showing',
    'commence': 'begin', 'commences': 'begins', 'commenced': 'began',
    'ascertain': 'find', 'ascertains': 'finds', 'ascertained': 'found',
    'comprise': 'include', 'comprises': 'includes', 'comprised': 'included',
    'encompass': 'cover', 'encompasses': 'covers', 'encompassed': 'covered',
    # verbs of change
    'induce': 'cause', 'induces': 'causes', 'induced': 'caused',
    'amplify': 'increase', 'amplifies': 'increases', 'amplified': 'increased',
    'mitigate': 'reduce', 'mitigates': 'reduces', 'mitigated': 'reduced',
    # quantity / degree
    'numerous': 'many', 'myriad': 'many', 'plethora': 'many',
    'additional': 'more', 'approximately': 'about', 'sufficient': 'enough',
    'individuals': 'people',
    # e-commerce register (from the ASOLO baseline; generic synonyms)
    'apparel': 'clothing', 'storefront': 'website', 'storefronts': 'websites',
    # multi-word connective inflation
    'prior to': 'before', 'subsequent to': 'after', 'in order to': 'to',
    'due to the fact that': 'because', 'in the event that': 'if',
    'the majority of': 'most', 'a number of': 'several', 'with regard to': 'about',
    'a myriad of': 'many',
}

# Longest keys first so multi-word phrases win over any single-word overlap.
_PATTERN = re.compile(
    r'\b(' + '|'.join(re.escape(k) for k in sorted(LEXICON, key=len, reverse=True)) + r')\b',
    re.IGNORECASE)


def _match_case(matched, replacement):
    """Carry the first-letter case of the matched text onto the replacement."""
    if matched[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def lower_register(text):
    """Returns (new_text, n_changes). Deterministic; numbers and acronyms untouched."""
    count = 0

    def sub(m):
        nonlocal count
        count += 1
        return _match_case(m.group(0), LEXICON[m.group(0).lower()])

    return _PATTERN.sub(sub, text), count


def main(argv=None):
    parser = argparse.ArgumentParser(description='Academic Humanizer v8.0 register-lowering lexicon (prototype)')
    parser.add_argument('input', help='Plain-text prose file')
    parser.add_argument('-o', '--output', help='Where to write the result (default: stdout)')
    parser.add_argument('--report', action='store_true', help='Print the number of substitutions to stderr')
    args = parser.parse_args(argv)
    with open(args.input, encoding='utf-8') as f:
        text = f.read()
    new, n = lower_register(text)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(new if new.endswith('\n') else new + '\n')
        print(f'Written: {args.output}')
    else:
        sys.stdout.write(new + ('\n' if not new.endswith('\n') else ''))
    if args.report:
        print(f'register-lowering substitutions: {n}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
