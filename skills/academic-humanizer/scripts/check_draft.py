#!/usr/bin/env python3
"""
Academic Humanizer: Phase 2 Draft Checker (v6.4.0)

Compares a rewritten draft against its source text and an optional
author-supplied fact sheet. It reports problems; it never rewrites text.

Fact checks (FAIL, exit code 1):
  - a number in the draft that is in neither the source nor the fact sheet
  - a number in the source that is missing from the draft
  - word retention below --min-retention

Fact checks (WARN):
  - acronyms or formulas in the draft that are in neither the source nor the
    fact sheet, unless defined in the draft as "full term (ACRONYM)"
  - word retention above --max-retention
  - fewer hedges of a kind (possibility, frequency, evidential) than the source
  - more "must" than the source
  - source sentences whose content words are largely missing (possible drops)

Style checks (WARN): sentences over --max-words, semicolons, reveal colons, em dashes,
stock AI phrases, mid-sentence ", however,", participial tails, three-item
lists, duplicate sentences, runs of sentences opening with the same word,
restatement padding, three sentences in a row sharing an opening frame,
too few short sentences (below --min-short), and overused add-ons
("C too.", "C as well.", "also", "alongside", "along with", "together with").

Usage:
  check_draft.py SOURCE [--facts FACTS]          print the fact ledger
  check_draft.py SOURCE DRAFT [--facts FACTS]    check a draft
"""

import argparse
import re
import statistics
import sys
from collections import namedtuple
from decimal import Decimal

SMALL_NUMBERS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10, 'eleven': 11,
    'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
    'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
}
TENS = {
    'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
    'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
}
SCALES = {'hundred': 100, 'thousand': 1000, 'million': 1000000}
NUMBER_WORDS = {**SMALL_NUMBERS, **TENS, **SCALES}

# Digits glued to a letter, digit or formula marker are skipped, so "Li6.4",
# "O12", "cm-2" and "m^{1/2}" yield nothing. Sub/superscripts never match [0-9].
DIGIT_NUMBER = re.compile(
    r'(?<![A-Za-z0-9_^{/.])(?<![A-Za-z]-)([0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(\.[0-9]+)?'
)
# Hyphens and whitespace don't break a run of number words ("three hundred",
# "twenty-five"); any other punctuation does.
WORD_TOKEN = re.compile(r'[A-Za-z]+|[^\sA-Za-z-]')

TERM_TOKEN = re.compile(r'[A-Za-z][A-Za-z0-9²³¹⁰-₟.]*')
SUPERSCRIPTS = '²³¹⁰ⁱ⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ'
# Units that look like acronyms; rewriting "megapascals" as "MPa" is not a new term.
UNIT_TERMS = {
    'MPa', 'GPa', 'TPa', 'MeV', 'GeV', 'TeV', 'MHz', 'GHz', 'THz',
    'MW', 'GW', 'TW', 'MWh', 'GWh', 'TWh', 'MJ', 'GJ', 'TB', 'GB', 'MB',
}

ABBREVIATIONS = {
    'al.', 'e.g.', 'i.e.', 'Fig.', 'Figs.', 'Eq.', 'Eqs.', 'Ref.', 'Refs.',
    'vs.', 'approx.', 'ca.', 'cf.', 'No.', 'Dr.', 'Prof.',
}

STOCK_PHRASES = [
    'furthermore', 'moreover', 'additionally', 'notably', 'ultimately',
    'in conclusion', 'in summary', 'in short', 'to summarize',
    r'it is (?:important|crucial) to note', 'pivotal', 'vital role',
    'integral role', 'tapestry', r'delves? into', 'testament', 'paramount',
    'transformative potential', 'the landscape of', 'cornerstone', 'synergy',
    'holistic', r'to (?:address|resolve|overcome|mitigate) these',
    r'this study (?:highlights|outlines)', 'reveals exactly', 'must deploy',
    'must integrate', 'must establish', 'hinges on', r'as the demand for',
]
STOCK_PATTERN = re.compile(r'\b(' + '|'.join(STOCK_PHRASES) + r')\b', re.IGNORECASE)

PARTICIPIAL_TAIL = re.compile(r',\s+([a-z]{3,}ing)\b')
NOT_PARTICIPLES = {
    'during', 'including', 'according', 'regarding', 'concerning',
    'notwithstanding', 'nothing', 'something', 'anything', 'everything',
    'string', 'spring', 'bring', 'thing', 'morning', 'evening', 'ceiling',
}
TRIAD = re.compile(r',\s[^,;:.]{1,50},\s(?:and|or)\s')
MID_HOWEVER = re.compile(r',\s*however\s*,', re.IGNORECASE)
# Hedges grouped by kind. A draft with fewer of a kind than the source has
# probably turned a tentative finding into a firm one.
HEDGE_CLASSES = {
    'possibility': r'\b(?:may|might|could|possibly|potentially|perhaps)\b',
    'frequency': r'\b(?:often|frequently|occasional(?:ly)?|sometimes|typically|usually|generally|commonly|rarely)\b',
    'evidential': (r'\b(?:suggest(?:s|ed|ing)?|indicat(?:e|es|ed|ing)|appear(?:s|ed)?|seem(?:s|ed)?'
                   r'|likely|unlikely|impl(?:y|ies|ied|ying)|points? to)\b'),
}
MUST = re.compile(r'\bmust\b', re.IGNORECASE)
DROP_STOPWORDS = set(
    'that this these those with from into have been their there which while where when what about across '
    'through under over than then they them also such some more most only very will would should could '
    'being were does upon onto each other both well much many'.split())
MIN_DROP_WORDS = 3
MIN_DROP_SHARE = 0.3
NEAR_DUPLICATE = 0.75
# A short sentence whose content words all appear within two sentences of it adds nothing.
RESTATEMENT_MAX_WORDS = 6
RESTATEMENT_WINDOW = 2
# Three sentences in a row sharing a content word in their first three words read as a template.
FRAME_WORDS = 3
FRAME_STOPWORDS = DROP_STOPWORDS | set('the a an of in on to and or for is are was were it its our we this by as at be'.split())
REVEAL_COLON = re.compile(r':\s')
EM_DASH = re.compile(r'\u2014|\s--\s')
# "(1)", "(b)", "(iv)" mark list items; they aren't facts.
LIST_MARKER = re.compile(r'\(\s*(?:\d{1,2}|[a-z]|[ivx]{1,4})\s*\)')
# "A and B. C too." is what splitting a three-item list tends to produce.
ADD_ON_ENDING = re.compile(r'\b(?:too|as well|alongside (?:it|them)|the same (?:effect|treatment))[.!?]$', re.IGNORECASE)
ADD_ON_CONNECTOR = re.compile(r'\b(?:also|alongside|along with|together with)\b', re.IGNORECASE)
MAX_ADD_ON_ENDINGS = 2
MAX_CONNECTOR_SHARE = 0.06
ACRONYM_DEFINITION = re.compile(r'\(([A-Za-z][A-Za-z-]{1,15})\)')
ACRONYM_STOPWORDS = {'of', 'and', 'the', 'for', 'in', 'on', 'to', 'a', 'an', 'by', 'with'}

Sentence = namedtuple('Sentence', 'para index text heading')


def _canonical(digits, fraction=''):
    value = Decimal(digits.replace(',', '') + (fraction or ''))
    return format(value.normalize(), 'f')


def _parse_number_words(words):
    words = [w for w in words if w != 'and']
    if words == ['one']:
        return None  # "one of", "no one": too ambiguous to count as a quantity
    total = current = 0
    for w in words:
        if w == 'hundred':
            current = (current or 1) * 100
        elif w in SCALES:
            total += (current or 1) * SCALES[w]
            current = 0
        else:
            current += NUMBER_WORDS[w]
    return str(total + current)


def _word_numbers(text):
    found, run = [], []
    for token in WORD_TOKEN.findall(text) + ['.']:
        word = token.lower()
        if word in NUMBER_WORDS or (word == 'and' and run and run[-1] in SCALES):
            run.append(word)
            continue
        if run:
            value = _parse_number_words(run)
            if value is not None:
                found.append(value)
            run = []
    return found


def extract_numbers(text):
    """Returns the set of numbers in text, normalized so '3,860' == '3860' and 'fifty' == '50'."""
    text = LIST_MARKER.sub(' ', text)
    numbers = {_canonical(m.group(1), m.group(2)) for m in DIGIT_NUMBER.finditer(text)}
    numbers.update(_word_numbers(text))
    return numbers


def extract_terms(text):
    """Returns acronyms and formulas: tokens with 2+ capitals, or a capital plus a digit."""
    terms = set()
    for token in TERM_TOKEN.findall(text):
        token = token.rstrip('.').rstrip(SUPERSCRIPTS)
        uppers = sum(c.isupper() for c in token)
        has_digit = any(c.isdigit() for c in token)
        if (uppers >= 2 or (uppers and has_digit)) and token not in UNIT_TERMS:
            terms.add(token)
    return terms


def defined_acronyms(text):
    """Returns acronyms defined in text as "full term (ACRONYM)", where the capitals match the term's initials."""
    defined = set()
    for m in ACRONYM_DEFINITION.finditer(text):
        acronym = m.group(1)
        letters = [c.lower() for c in acronym if c.isupper()]
        if len(letters) < 2:
            continue
        # Whole words only, so the element symbols inside a formula never spell out an acronym.
        words = [w for w in re.findall(r'\b[A-Za-z]+\b', text[:m.start()])[-15:]
                 if w.lower() not in ACRONYM_STOPWORDS]
        if len(words) >= len(letters) and [w[0].lower() for w in words[-len(letters):]] == letters:
            defined |= extract_terms(acronym)
    return defined


def read_fact_sheet(text):
    """Drops HTML comments and markdown headings so template guidance never counts as a fact."""
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return '\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('#'))


def segment(text):
    """Splits text into sentences, tagging single-line unpunctuated paragraphs as headings."""
    sentences = []
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    for p_idx, para in enumerate(paragraphs, 1):
        flat = ' '.join(para.split())
        if '\n' not in para and len(flat.split()) <= 30 and not re.search(r'[.?!]["”)\]]?$', flat):
            sentences.append(Sentence(p_idx, 1, flat, True))
            continue
        pieces = []
        for piece in re.split(r'(?<=[.?!])\s+|(?<=[.?!]["\u201d\u2019\')\]])\s+', flat):
            if pieces and (pieces[-1].split()[-1].lstrip('([') in ABBREVIATIONS or piece[:1].islower()):
                pieces[-1] += ' ' + piece
            else:
                pieces.append(piece)
        sentences.extend(Sentence(p_idx, s_idx, s, False) for s_idx, s in enumerate(pieces, 1))
    return sentences


def _text_numbers(text):
    """Numbers per sentence, so a run of number words never spans a sentence or paragraph break."""
    return set().union(*(extract_numbers(s.text) for s in segment(text)))


def _stems(text):
    """Crude stems (first five letters of content words), enough to tell reworded from removed."""
    return {w[:5] for w in re.findall(r'[a-z]+', text.lower()) if len(w) >= 4 and w not in DROP_STOPWORDS}


def _word_set(text):
    return set(re.findall(r'[a-z0-9]+', text.lower()))


def _sort_numbers(numbers):
    return sorted(numbers, key=float)


def check(source, draft, facts='', min_retention=95.0, max_retention=110.0, max_words=16, min_short=15.0):
    """Checks a draft against its source and fact sheet. Returns findings and stats."""
    facts = read_fact_sheet(facts)
    source_numbers = _text_numbers(source)
    fact_numbers = _text_numbers(facts)
    allowed_numbers = source_numbers | fact_numbers
    allowed_terms = extract_terms(source) | extract_terms(facts) | defined_acronyms(draft)

    findings = []

    def add(level, kind, message, sentence=None, origin='draft'):
        where = f'{origin} ¶{sentence.para} s{sentence.index}' if sentence else ''
        text = sentence.text if sentence else ''
        findings.append({'level': level, 'kind': kind, 'message': message, 'where': where, 'text': text})

    draft_sentences = segment(draft)
    draft_numbers = set()
    for s in draft_sentences:
        numbers = extract_numbers(s.text)
        draft_numbers |= numbers
        for n in _sort_numbers(numbers - allowed_numbers):
            add('FAIL', 'new-number', f'"{n}" is not in the source or fact sheet', s)
        for t in sorted(extract_terms(s.text) - allowed_terms):
            add('WARN', 'new-term', f'"{t}" is not in the source or fact sheet', s)

    source_sentences = segment(source)
    for n in _sort_numbers(source_numbers - draft_numbers):
        origin = next((s for s in source_sentences if n in extract_numbers(s.text)), None)
        add('FAIL', 'missing-number', f'"{n}" from the source is missing from the draft', origin, 'source')

    source_words = len(source.split())
    draft_words = len(draft.split())
    retention = draft_words / source_words * 100 if source_words else 0.0
    if retention < min_retention:
        add('FAIL', 'retention', f'draft keeps {retention:.1f}% of source words (minimum {min_retention:g}%)')
    elif retention > max_retention:
        from_facts = bool((draft_numbers & fact_numbers) - source_numbers)
        note = ('; fact-sheet details were added, so leave it and tell the author in case of a word limit'
                if from_facts else '; cut filler words and merge over-split fragments')
        add('WARN', 'retention', f'draft is {retention:.1f}% of source length (maximum {max_retention:g}%){note}')

    for kind, pattern in HEDGE_CLASSES.items():
        in_source = len(re.findall(pattern, source, re.IGNORECASE))
        in_draft = len(re.findall(pattern, draft, re.IGNORECASE))
        if in_draft < in_source:
            for s in source_sentences:
                m = re.search(pattern, s.text, re.IGNORECASE)
                if m:
                    add('WARN', 'hedge', f'{kind} hedges: source {in_source}, draft {in_draft}; '
                        f'make sure the draft keeps "{m.group(0)}" here', s, 'source')
    if len(MUST.findall(draft)) > len(MUST.findall(source)):
        for s in draft_sentences:
            if MUST.search(s.text):
                add('WARN', 'modal', '"must" is stronger than the source; keep the source\'s modal', s)

    draft_stems = _stems(draft)
    for s in source_sentences:
        if s.heading:
            continue
        stems = _stems(s.text)
        missing = sorted(stems - draft_stems)
        if len(missing) >= MIN_DROP_WORDS and len(missing) / len(stems) >= MIN_DROP_SHARE:
            add('WARN', 'possible-drop', f'words from this source sentence are missing from the draft '
                f'({", ".join(missing)}); check it was not dropped', s, 'source')

    prose = [s for s in draft_sentences if not s.heading]
    seen = []
    run_word, run_length = None, 0
    for s in prose:
        words = s.text.split()
        if len(words) > max_words:
            add('WARN', 'long-sentence', f'{len(words)} words (maximum {max_words})', s)
        if ';' in s.text:
            add('WARN', 'semicolon', 'split into separate sentences', s)
        if REVEAL_COLON.search(s.text):
            add('WARN', 'colon', 'end the sentence instead of using a reveal colon', s)
        if EM_DASH.search(s.text):
            add('WARN', 'em-dash', 'make the aside its own sentence or part of the main clause', s)
        for m in STOCK_PATTERN.finditer(s.text):
            add('WARN', 'stock-phrase', f'"{m.group(1)}"', s)
        if MID_HOWEVER.search(s.text):
            add('WARN', 'however', 'rewrite ", however," as "Yet ..." or two sentences', s)
        for m in PARTICIPIAL_TAIL.finditer(s.text):
            if m.group(1) not in NOT_PARTICIPLES and len(s.text[:m.start()].split()) >= 4:
                add('WARN', 'participial-tail', f'", {m.group(1)}" tail: make it its own sentence', s)
        if TRIAD.search(s.text):
            add('WARN', 'triad', 'three-item list: restructure without dropping an item', s)

        word_set = _word_set(s.text)
        if any(word_set == w or (len(words) >= 5 and len(word_set & w) / len(word_set | w) >= NEAR_DUPLICATE)
               for w in seen):
            add('WARN', 'duplicate', 'repeats an earlier sentence', s)
        seen.append(word_set)

        first = re.sub(r'[^a-z]', '', words[0].lower()) if words else ''
        run_length = run_length + 1 if first == run_word else 1
        run_word = first
        if run_length == 3:
            add('WARN', 'openings', f'third sentence in a row starting with "{words[0]}"', s)

    add_on_endings = [s for s in prose if ADD_ON_ENDING.search(s.text)]
    if len(add_on_endings) > MAX_ADD_ON_ENDINGS:
        for s in add_on_endings:
            add('WARN', 'add-on', f'{len(add_on_endings)} sentences end in "too"/"as well"-style add-ons '
                f'(maximum {MAX_ADD_ON_ENDINGS}); integrate the item instead', s)
    connector_sentences = [s for s in prose if ADD_ON_CONNECTOR.search(s.text)]
    if len(connector_sentences) > max(3, MAX_CONNECTOR_SHARE * len(prose)):
        add('WARN', 'add-on', f'"also"/"alongside"/"along with"/"together with" appear in '
            f'{len(connector_sentences)} of {len(prose)} sentences; vary how items are connected')

    prose_stems = [_stems(s.text) for s in prose]
    for i, s in enumerate(prose):
        if len(s.text.split()) <= RESTATEMENT_MAX_WORDS and len(prose_stems[i]) >= 2:
            nearby = set().union(*(prose_stems[j] for j in range(max(0, i - RESTATEMENT_WINDOW),
                                                                  min(len(prose), i + RESTATEMENT_WINDOW + 1)) if j != i))
            if prose_stems[i] <= nearby:
                add('WARN', 'restatement', 'only repeats words from the sentences around it; '
                    'delete it or make it state something new from the source', s)

    heads = [{w.lower() for w in re.findall(r'[A-Za-z-]+', s.text)[:FRAME_WORDS]} - FRAME_STOPWORDS for s in prose]
    i = 0
    while i + 2 < len(prose):
        shared = heads[i] & heads[i + 1] & heads[i + 2]
        if shared:
            add('WARN', 'parallel', f'three sentences in a row open on "{sorted(shared)[0]}"; '
                'change the shape of at least one (S5)', prose[i + 2])
            i += 3
        else:
            i += 1

    lengths = [len(s.text.split()) for s in prose]
    mean = statistics.mean(lengths) if lengths else 0.0
    short_share = sum(l <= 5 for l in lengths) / len(lengths) * 100 if lengths else 0.0
    if len(lengths) >= 10 and short_share < min_short:
        add('WARN', 'short-sentences', f'only {short_share:.1f}% of sentences have 5 words or fewer '
            f'(minimum {min_short:g}%); lead with a claim\'s core, never a split-off modifier')
    stats = {
        'source_words': source_words,
        'draft_words': draft_words,
        'retention': round(retention, 1),
        'sentences': len(lengths),
        'mean_length': round(mean, 1),
        'max_length': max(lengths) if lengths else 0,
        'short_share': round(short_share, 1),
        'length_burstiness': round(statistics.stdev(lengths) / mean, 2) if len(lengths) > 1 and mean else 0.0,
    }
    return {
        'findings': findings,
        'stats': stats,
        'fact_sheet_numbers_used': _sort_numbers((draft_numbers & fact_numbers) - source_numbers),
        'passed': not any(f['level'] == 'FAIL' for f in findings),
    }


def _excerpt(text, limit=110):
    return text if len(text) <= limit else text[:limit - 3] + '...'


def format_report(result):
    stats = result['stats']
    fact_kinds = {'new-number', 'missing-number', 'new-term', 'retention', 'hedge', 'modal', 'possible-drop'}
    facts = [f for f in result['findings'] if f['kind'] in fact_kinds]
    style = [f for f in result['findings'] if f['kind'] not in fact_kinds]

    def lines_for(findings):
        if not findings:
            return ['  none']
        out = []
        for f in findings:
            where = f'  [{f["where"]}]' if f['where'] else ''
            out.append(f'  {f["level"]}  {f["kind"]}: {f["message"]}{where}')
            if f['text']:
                out.append(f'        "{_excerpt(f["text"])}"')
        return out

    used = ', '.join(result['fact_sheet_numbers_used']) or 'none'
    fails = sum(f['level'] == 'FAIL' for f in result['findings'])
    warns = sum(f['level'] == 'WARN' for f in result['findings'])
    lines = [
        '=== FACT CHECK ===',
        f'Words: source {stats["source_words"]}, draft {stats["draft_words"]} ({stats["retention"]}% retention)',
        f'Fact-sheet numbers used: {used}',
        *lines_for(facts),
        '',
        '=== STYLE CHECK ===',
        *lines_for(style),
        '',
        '=== STATS (informational) ===',
        f'Sentences: {stats["sentences"]}  Mean length: {stats["mean_length"]}  Max length: {stats["max_length"]}',
        f'Short sentences (<=5 words): {stats["short_share"]}%  Length burstiness (stdev/mean): {stats["length_burstiness"]}',
        '',
        f'RESULT: {"PASS" if result["passed"] else "FAIL"} ({fails} failures, {warns} warnings)',
    ]
    return '\n'.join(lines)


def format_ledger(source, facts=''):
    facts = read_fact_sheet(facts)
    source_numbers = _text_numbers(source)
    fact_numbers = _text_numbers(facts) - source_numbers
    source_terms = extract_terms(source)
    fact_terms = extract_terms(facts) - source_terms
    return '\n'.join([
        '=== FACT LEDGER ===',
        'Numbers in the source (every one must appear in the draft):',
        '  ' + (', '.join(_sort_numbers(source_numbers)) or 'none'),
        'Numbers from the fact sheet (may be added):',
        '  ' + (', '.join(_sort_numbers(fact_numbers)) or 'none'),
        'Acronyms and formulas in the source:',
        '  ' + (', '.join(sorted(source_terms)) or 'none'),
        'Acronyms and formulas from the fact sheet (may be added):',
        '  ' + (', '.join(sorted(fact_terms)) or 'none'),
        'Numbers are normalized: "7.0" is listed as 7, "fifty" as 50, "3,860" as 3860.',
        'No other number, acronym or formula may appear in the draft, except an acronym',
        'you define at first use for a term the source spells out: "full term (ACRONYM)".',
    ])


def _read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def main(argv=None):
    parser = argparse.ArgumentParser(description='Academic Humanizer: Phase 2 Draft Checker (v6.4.0)')
    parser.add_argument('source', help='Original text file')
    parser.add_argument('draft', nargs='?', help='Rewritten draft (omit to print the fact ledger)')
    parser.add_argument('--facts', help='Author-supplied fact sheet')
    parser.add_argument('--min-retention', type=float, default=95.0, help='Minimum draft/source word ratio, %% (default 95)')
    parser.add_argument('--max-retention', type=float, default=110.0, help='Warn above this word ratio, %% (default 110)')
    parser.add_argument('--max-words', type=int, default=16, help='Warn on sentences longer than this (default 16)')
    parser.add_argument('--min-short', type=float, default=15.0, help='Warn if fewer than this %% of sentences have <=5 words (default 15)')
    args = parser.parse_args(argv)

    source = _read(args.source)
    facts = _read(args.facts) if args.facts else ''
    if not args.draft:
        print(format_ledger(source, facts))
        return 0

    result = check(source, _read(args.draft), facts, args.min_retention, args.max_retention, args.max_words, args.min_short)
    print(format_report(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
