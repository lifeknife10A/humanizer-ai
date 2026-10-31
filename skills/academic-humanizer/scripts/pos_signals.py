#!/usr/bin/env python3
"""
Academic Humanizer: POS Signal Prototype (v7.16.0)

Pure-stdlib, deterministic regex proxies for three part-of-speech signals that
the literature reports separate human from AI academic prose ([P05]; the verified
primary source is indexed in research/LITERATURE_TRACKER.md, with grounding in
research/POS_CERTAINTY_READABILITY.md):

  - pronoun rate         referential pronouns per 100 words. AI starves prose of
                         pronouns ([P05]: the strongest negative predictor of AI).
  - nominalization rate  words ending in -tion/-ment/-ity/... per 100 words. AI
                         stacks abstract noun phrases ("nominal loading").
  - passive share        share of sentences with a passive construction. [P05]
                         reports human academic prose uses far more passive than
                         AI (~34% vs ~11%), but on THIS repo's texts the lowest-
                         ZeroGPT rewrites had the least passive, so this is
                         reported as an informational stat and never warns.

These are PROXIES, not a POS tagger. They are deliberately crude so the checker
stays dependency-free. Expect false positives (a coincidental -ment word, an
adjectival "is based"). For that reason check_draft.py always PRINTS these three
rates as informational stats, but only emits WARNs when run with --pos-checks.
The thresholds below are calibrated against this repo's own benchmark texts, not
against any detector, and are not benchmark-validated. Treat them as a starting
point to tune, never as a pass/fail gate.

This module is standalone (it imports nothing from check_draft) so it can be
tested on its own and reused by other tools.
"""

import re

# ---------- pronouns ----------
# Personal, possessive and demonstrative pronouns. "that" is left out on purpose:
# it is a relative pronoun and complementizer far more often than a demonstrative,
# so counting it would swamp the signal.
PRONOUNS = re.compile(
    r'\b(?:i|we|us|me|my|our|mine|ours|myself|ourselves'
    r'|you|your|yours|yourself|yourselves'
    r'|he|him|his|himself|she|her|hers|herself'
    r'|it|its|itself|they|them|their|theirs|themselves'
    r'|this|these|those)\b',
    re.IGNORECASE)

# ---------- nominalizations ----------
# Suffixes that mark a deverbal/deadjectival noun. Crude: it matches the surface
# form, so it also catches common academic nouns (that is the point — they are
# what "nominal loading" is made of) and a few coincidental words (below).
NOMINALIZATION = re.compile(
    r'\b[a-z]{2,}(?:tions?|sions?|ments?|ness(?:es)?|ities|ity|ances?|ences?|isms?)\b',
    re.IGNORECASE)
# Common words whose suffix is coincidental, not a nominalization. Small on purpose.
NOMINALIZATION_STOPWORDS = {
    'moment', 'moments', 'comment', 'comments', 'cement', 'garment', 'garments',
    'element', 'elements', 'segment', 'segments', 'pigment', 'pigments',
    'fragment', 'fragments', 'ornament', 'ornaments', 'parliament', 'density',
    'entity', 'quantity', 'quantities', 'city', 'cities',
}

# ---------- passive voice ----------
_BE = r'(?:am|is|are|was|were|be|been|being|gets?|got|gotten)'
# Irregular past participles that don't end in -ed, so the proxy catches them too.
_IRREGULAR = (
    'born', 'done', 'made', 'given', 'taken', 'seen', 'known', 'shown', 'found',
    'held', 'built', 'set', 'put', 'written', 'drawn', 'grown', 'kept', 'led',
    'sent', 'told', 'left', 'lost', 'meant', 'read', 'cut', 'hit', 'let', 'met',
    'paid', 'said', 'sold', 'won', 'run', 'begun', 'chosen', 'driven', 'proven',
    'broken', 'spoken', 'frozen', 'stolen', 'risen', 'fallen', 'thrown', 'brought',
    'bought', 'caught', 'taught', 'fought', 'sought',
)
# be (+ up to two -ly adverbs) + a past participle. Noisy around adjectival
# predicates ("is interested"), which is why passive is a WARN only under --pos-checks.
PASSIVE = re.compile(
    r'\b' + _BE + r'\s+(?:\w+ly\s+){0,2}(?:\w+ed|' + '|'.join(_IRREGULAR) + r')\b',
    re.IGNORECASE)

# ---------- thresholds (calibrated on this repo's benchmarks; not validated) ----------
# Calibration finding (see research/POS_CERTAINTY_READABILITY.md): across this repo's own
# AI and humanized texts these proxies overlap heavily and barely separate the two, echoing
# the label study's "local proxies are at chance for ZeroGPT". Two consequences:
#   1. The thresholds below are set to flag only clear extremes, so they stay conservative.
#   2. Passive share is PRINTED but NEVER WARNS. In our data the lowest-ZeroGPT texts had the
#      LEAST passive (breakthrough 2.9% and round3 5.3% at 0-8%, vs 21% for the 100%-AI
#      baseline), the opposite of [P05]. Warning on low passive would penalize our best
#      outputs, so passive stays informational only.
MIN_PRONOUN_RATE = 1.5          # per 100 words; warn below
MAX_NOMINALIZATION_RATE = 11.0  # per 100 words; warn above
MIN_SENTENCES = 10              # don't judge rates on very short text


def _words(text):
    return re.findall(r"[A-Za-z][A-Za-z'-]*", text)


def pronoun_rate(text):
    """Referential pronouns per 100 words."""
    words = _words(text)
    if not words:
        return 0.0
    return round(len(PRONOUNS.findall(text)) / len(words) * 100, 1)


def nominalization_rate(text):
    """Nominalization-suffixed words per 100 words, minus a small coincidental stoplist."""
    words = _words(text)
    if not words:
        return 0.0
    hits = [m.group(0) for m in NOMINALIZATION.finditer(text)
            if m.group(0).lower() not in NOMINALIZATION_STOPWORDS]
    return round(len(hits) / len(words) * 100, 1)


def passive_share(sentence_texts):
    """Percentage of sentences that contain at least one passive construction."""
    if not sentence_texts:
        return 0.0
    passive = sum(1 for s in sentence_texts if PASSIVE.search(s))
    return round(passive / len(sentence_texts) * 100, 1)


def compute(text, sentence_texts):
    """All three rates as a dict."""
    return {
        'pronoun_rate': pronoun_rate(text),
        'nominalization_rate': nominalization_rate(text),
        'passive_share': passive_share(sentence_texts),
    }


def warnings(stats, n_sentences):
    """Opt-in WARNs (kind, message) from the rates. Empty on short text.
    Passive share is informational only (see the threshold note) and never warns."""
    out = []
    if n_sentences < MIN_SENTENCES:
        return out
    if stats['pronoun_rate'] < MIN_PRONOUN_RATE:
        out.append(('pronoun', f'only {stats["pronoun_rate"]} referential pronouns per 100 words '
                    f'(below {MIN_PRONOUN_RATE:g}); AI prose starves itself of "it", "they", "this". '
                    'Where the source refers back to something, use a pronoun instead of repeating the noun'))
    if stats['nominalization_rate'] > MAX_NOMINALIZATION_RATE:
        out.append(('nominalization', f'{stats["nominalization_rate"]} nominalizations per 100 words '
                    f'(above {MAX_NOMINALIZATION_RATE:g}); the prose stacks abstract nouns. Prefer a plain '
                    'verb to an abstract noun ("we measured" over "measurement was performed"), within H3'))
    return out


def _report(text, sentence_texts):
    stats = compute(text, sentence_texts)
    lines = [f'pronoun rate (per 100 words): {stats["pronoun_rate"]}',
             f'nominalization rate (per 100 words): {stats["nominalization_rate"]}',
             f'passive sentence share: {stats["passive_share"]}%']
    for _, message in warnings(stats, len(sentence_texts)):
        lines.append(f'WARN  {message}')
    return '\n'.join(lines)


if __name__ == '__main__':
    import sys
    data = open(sys.argv[1], encoding='utf-8').read() if len(sys.argv) > 1 else sys.stdin.read()
    sentences = re.split(r'(?<=[.?!])\s+', ' '.join(data.split()))
    print(_report(data, [s for s in sentences if s.strip()]))
