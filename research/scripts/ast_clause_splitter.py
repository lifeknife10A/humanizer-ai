#!/usr/bin/env python3
"""
Academic Humanizer v8.0 — Stage 1: Deterministic AST Clause Splitter (prototype)

Breaks long academic sentences into shorter declarative units using a real
dependency parse (spaCy), NOT regex and NOT an LLM. The point of Stage 1 is to
decompose sentences deterministically, so the transformation adds no
LLM-distribution fingerprint of its own (see
research/V8_DETERMINISTIC_FIRST_ARCHITECTURE.md).

Design principle: PROPOSE via the parse, ACCEPT only if provably faithful.
Every candidate rewrite must pass three gates or the original sentence is kept
unchanged:
  1. Numbers preserved   — extract_numbers() (the repo's canonical, unit-free,
     digit==word number set) is identical before and after.
  2. Content preserved   — the multiset of content-word lemmas (NOUN, PROPN,
     VERB, ADJ, ADV, NUM) is identical before and after. This is what guards
     against the failure that retired humanizer.py: dropped/glued/duplicated
     words. Function words (the dropped "and", the added "This") are not content.
  3. Well-formed         — every output sentence re-parses to a finite ROOT verb
     and an explicit subject, so no fragment is emitted.

Transforms:
  * Coordinate-clause split (default, low risk): "S1 V1 ..., and S2 V2 ..." ->
    "S1 V1 ...." + "S2 V2 ...." Only the coordinating conjunction (and a comma)
    is dropped; every content word stays, in order. Fully meaning-preserving.
  * Participial-tail decoupling (--participial, EXPERIMENTAL): "..., yielding X"
    -> "... This yields X." Generates a present 3rd-person-singular finite verb
    from the participle's lemma. Higher risk (tense can shift); gated by the
    well-formedness and content checks, and off by default.

This is a RESEARCH PROTOTYPE, not wired into the skill. It only splits sentences
longer than --max-words; shorter ones pass through untouched. Run its output
through check_draft.py (or pass --check SOURCE) before trusting it.

Usage:
  ast_clause_splitter.py INPUT.txt [-o OUT.txt] [--max-words 16] [--participial]
                         [--report] [--check SOURCE.txt] [--model en_core_web_sm]

Requires: spacy + a model (python3 -m spacy download en_core_web_sm).
"""

import argparse
import os
import re
import sys
from collections import Counter

# Reuse the repo's canonical number extractor so "fifty" == "50" == "50.0",
# exactly as the Phase 2 checker counts numbers.
_SKILL_SCRIPTS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',
                                              'skills', 'academic-humanizer', 'scripts'))
if _SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, _SKILL_SCRIPTS)
from check_draft import extract_numbers  # noqa: E402

CONTENT_POS = {'NOUN', 'PROPN', 'VERB', 'ADJ', 'ADV', 'NUM'}
SUBJECT_DEPS = {'nsubj', 'nsubjpass', 'csubj', 'csubjpass', 'expl'}
FINITE_POS = {'VERB', 'AUX'}
CLAUSE_HEAD_DEPS = {'ROOT', 'conj'}   # only split top-level independent clauses
COORD_CONJ = {'and', 'but', 'so', 'yet', 'for', 'or', 'nor'}
VOWELS = set('aeiou')

_NLP = None


def load_nlp(model='en_core_web_sm'):
    """Loads and caches the spaCy pipeline (NER disabled; we only need the parser)."""
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load(model, disable=['ner'])
    return _NLP


# ---------- fidelity helpers ----------

def content_lemmas(doc):
    """Multiset of lowercased content-word lemmas in a parsed doc/span."""
    return Counter(t.lemma_.lower() for t in doc if t.pos_ in CONTENT_POS and not t.is_space)


def _word_count(span):
    return sum(1 for t in span if not t.is_punct and not t.is_space)


def well_formed(doc):
    """True if every sentence in the parsed doc has a finite ROOT verb and a subject."""
    sents = list(doc.sents)
    if not sents:
        return False
    for s in sents:
        has_root = any(t.dep_ == 'ROOT' and t.pos_ in FINITE_POS for t in s)
        has_subject = any(t.dep_ in SUBJECT_DEPS for t in s)
        if not (has_root and has_subject):
            return False
    return True


def is_faithful(original_text, new_text, nlp):
    """The three gates: numbers preserved, content lemmas preserved, output well-formed."""
    if extract_numbers(original_text) != extract_numbers(new_text):
        return False
    new_doc = nlp(new_text)
    if content_lemmas(nlp(original_text)) != content_lemmas(new_doc):
        return False
    return well_formed(new_doc)


# ---------- transforms ----------

def _capitalize(text):
    text = text.strip()
    return text[:1].upper() + text[1:] if text else text


def _ensure_period(text):
    text = text.strip()
    return text if re.search(r'[.?!]["”\')\]]?$', text) else text + '.'


def _coordinate_cuts(sent):
    """Char offsets (relative to the sentence) where a top-level clause coordination can be cut.
    Returns a sorted list of (drop_start, right_start): drop the cc (and a preceding comma) between
    them, and start a new sentence at right_start."""
    base = sent.start_char
    cuts = []
    for tok in sent:
        if tok.dep_ != 'cc' or tok.lower_ not in COORD_CONJ:
            continue
        head = tok.head
        if head.pos_ not in FINITE_POS or head.dep_ not in CLAUSE_HEAD_DEPS:
            continue
        # The conjunct clause that this cc introduces: a finite verb conj of head, after the cc,
        # carrying its own subject (so the right side can stand alone).
        conj = next((c for c in head.children
                     if c.dep_ == 'conj' and c.i > tok.i and c.pos_ in FINITE_POS
                     and any(ch.dep_ in SUBJECT_DEPS for ch in c.children)), None)
        if conj is None:
            continue
        subj = min((ch.left_edge.i for ch in conj.children if ch.dep_ in SUBJECT_DEPS),
                   default=conj.i)
        right_start = sent[subj].idx - base
        drop_start = tok.idx - base
        # Pull a comma (and spaces) sitting just before the cc into the dropped region.
        j = drop_start - 1
        while j >= 0 and sent.text[j] in ' \t':
            j -= 1
        if j >= 0 and sent.text[j] == ',':
            drop_start = j
        cuts.append((drop_start, right_start))
    return sorted(cuts)


def coordinate_split(sent):
    """"S1 V1 ..., and S2 V2 ..." -> ["S1 V1 ....", "S2 V2 ...."] or None if not applicable."""
    cuts = _coordinate_cuts(sent)
    if not cuts:
        return None
    text = sent.text
    pieces, pos = [], 0
    for drop_start, right_start in cuts:
        pieces.append(text[pos:drop_start])
        pos = right_start
    pieces.append(text[pos:])
    out = [_ensure_period(_capitalize(p)) for p in pieces if p.strip()]
    return ' '.join(out) if len(out) > 1 else None


def _third_person_singular(lemma):
    """Present 3sg of a verb lemma (regular rules + be/have)."""
    irregular = {'be': 'is', 'have': 'has', 'do': 'does', 'go': 'goes'}
    if lemma in irregular:
        return irregular[lemma]
    if lemma.endswith(('s', 'sh', 'ch', 'x', 'z', 'o')):
        return lemma + 'es'
    if lemma.endswith('y') and len(lemma) > 1 and lemma[-2] not in VOWELS:
        return lemma[:-1] + 'ies'
    return lemma + 's'


def participial_split(sent):
    """EXPERIMENTAL: "..., yielding X" -> "... This yields X." or None if not applicable."""
    base = sent.start_char
    for tok in sent:
        if tok.tag_ != 'VBG' or tok.dep_ not in {'advcl', 'acl'}:
            continue
        if tok.head.pos_ not in FINITE_POS:
            continue
        sub = list(tok.subtree)
        if any(c.dep_ in SUBJECT_DEPS for c in sub):     # has its own subject -> not a bare tail
            continue
        left_edge = min(t.i for t in sub)
        # The tail must be set off by a comma immediately before the participial subtree.
        start_char = sent[left_edge].idx - base
        j = start_char - 1
        while j >= 0 and sent.text[j] in ' \t':
            j -= 1
        if j < 0 or sent.text[j] != ',':
            continue
        left = sent.text[:j]
        verb = _third_person_singular(tok.lemma_.lower())
        after = sent.text[(tok.idx - base) + len(tok.text):]   # text after the participle
        right = f'This {verb}{after}'
        return f'{_ensure_period(left)} {_ensure_period(_capitalize(right))}'
    return None


# ---------- document driver ----------

def split_paragraph(text, nlp, max_words=16, participial=False):
    """Returns (new_text, events). Only sentences longer than max_words are considered,
    and a rewrite is applied only if it passes is_faithful()."""
    doc = nlp(text)
    out, events = [], []
    for sent in doc.sents:
        original = sent.text.strip()
        if not original:
            continue
        if _word_count(sent) <= max_words:
            out.append(original)
            continue
        candidate = coordinate_split(sent)
        kind = 'coordinate'
        if candidate is None and participial:
            candidate = participial_split(sent)
            kind = 'participial'
        if candidate is None:
            out.append(original)
            events.append(('kept-no-split', original, ''))
        elif is_faithful(original, candidate, nlp):
            out.append(candidate)
            events.append(('split-' + kind, original, candidate))
        else:
            out.append(original)
            events.append(('rejected-unfaithful', original, candidate))
    return ' '.join(out), events


def split_text(text, nlp, max_words=16, participial=False):
    """Processes each blank-line-separated paragraph, preserving paragraph breaks."""
    paras = re.split(r'(\n\s*\n)', text)
    out, events = [], []
    for chunk in paras:
        if chunk.strip() == '':
            out.append(chunk)
            continue
        new, ev = split_paragraph(chunk, nlp, max_words, participial)
        out.append(new)
        events.extend(ev)
    return ''.join(out), events


def _format_report(events):
    counts = Counter(kind for kind, _, _ in events)
    lines = ['=== AST CLAUSE SPLITTER REPORT ===',
             f'Sentences split (coordinate): {counts.get("split-coordinate", 0)}',
             f'Sentences split (participial): {counts.get("split-participial", 0)}',
             f'Candidates rejected as unfaithful: {counts.get("rejected-unfaithful", 0)}',
             f'Long sentences with no safe split: {counts.get("kept-no-split", 0)}', '']
    for kind, original, new in events:
        if kind.startswith('split'):
            lines.append(f'[{kind}]')
            lines.append(f'  - {original}')
            lines.append(f'  + {new}')
        elif kind == 'rejected-unfaithful':
            lines.append('[rejected: would change numbers/content or make a fragment]')
            lines.append(f'  - {original}')
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Academic Humanizer v8.0 Stage 1: AST clause splitter (prototype)')
    parser.add_argument('input', help='Plain-text prose file to split')
    parser.add_argument('-o', '--output', help='Where to write the result (default: stdout)')
    parser.add_argument('--max-words', type=int, default=16, help='Only split sentences longer than this (default 16)')
    parser.add_argument('--participial', action='store_true', help='Also try experimental participial-tail decoupling')
    parser.add_argument('--report', action='store_true', help='Print a report of what was split and what was rejected')
    parser.add_argument('--check', metavar='SOURCE', help='Run check_draft.py comparing the result against SOURCE')
    parser.add_argument('--model', default='en_core_web_sm', help='spaCy model (default en_core_web_sm)')
    args = parser.parse_args(argv)

    with open(args.input, encoding='utf-8') as f:
        text = f.read()
    try:
        nlp = load_nlp(args.model)
    except OSError:
        print(f"Cannot load spaCy model '{args.model}'. Install it: python3 -m spacy download {args.model}",
              file=sys.stderr)
        return 3
    new_text, events = split_text(text, nlp, args.max_words, args.participial)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(new_text if new_text.endswith('\n') else new_text + '\n')
        print(f'Written: {args.output}')
    else:
        sys.stdout.write(new_text + ('\n' if not new_text.endswith('\n') else ''))
    if args.report:
        print('\n' + _format_report(events), file=sys.stderr)
    if args.check:
        from check_draft import check, format_report
        with open(args.check, encoding='utf-8') as f:
            source = f.read()
        print('\n' + format_report(check(source, new_text)), file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
