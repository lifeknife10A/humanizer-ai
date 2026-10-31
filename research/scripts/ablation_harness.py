#!/usr/bin/env python3
"""
Academic Humanizer v8.0 — Ablation Harness (research)

Isolates the effect of each candidate humanization transform so we can measure
what *actually* moves a detector, instead of trusting the post-hoc diff story in
MULTI_AGENT_ARCHITECTURAL_BRIEFING.md (see V8_DETERMINISTIC_FIRST_ARCHITECTURE.md
§2, §6). It generates variants of a baseline draft, runs each through the Phase 2
number/fact gate (check_draft.py), and writes a manifest + Markdown report. It
does NOT score detectors — you feed the variants to your detector pipeline and
fill in the scores.

Five independently toggleable transforms (all deterministic, no LLM):
  clause_split        dependency-based coordinate + participial clause splitting
                      (delegates to ast_clause_splitter.py; internally fidelity-gated).
  demonstrative_chain replaces a referring common-noun subject with "This"/"These"
                      on non-paragraph-initial sentences (number-agreed).
  paren_isolation     splits multi-stat parentheticals into back-to-back parens,
                      e.g. "(t(11)=13.42, p<0.001)" -> "(t(11)=13.42) (p<0.001)".
  lexical_repeat      distributes an attributive adjective across a noun
                      coordination, e.g. "poor feedback and filtering" ->
                      "poor feedback and poor filtering".
  voice_alternation   turns a safe "We <verb>ed <object> ..." active clause into
                      passive, e.g. "We conducted empathy mapping." ->
                      "Empathy mapping was conducted."

Each transform applies only where its pattern safely matches and no-ops
elsewhere; the harness records coverage (how many sentences it changed). Every
variant is checked against the baseline: a variant is "numbers_ok" when
check_draft reports no new-number and no missing-number FAIL.

Modes:
  --mode single          baseline + one variant per transform (only that transform)
  --mode all             baseline + one variant with all transforms
  --mode leave-one-out   baseline + the all-variant + one variant per transform
                         with that transform disabled

Usage:
  ablation_harness.py INPUT.txt [--mode single|all|leave-one-out]
                      [--outdir research/ablation_runs] [--model en_core_web_sm]

spaCy + a model is needed for every transform except paren_isolation. If spaCy is
missing, only paren_isolation runs and the rest no-op (reported as unavailable).
"""

import argparse
import json
import os
import re
import sys
from collections import OrderedDict

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_SKILL = os.path.abspath(os.path.join(_HERE, '..', '..', 'skills', 'academic-humanizer', 'scripts'))
if _SKILL not in sys.path:
    sys.path.insert(0, _SKILL)

import ast_clause_splitter as ACS           # noqa: E402
from check_draft import check, segment, format_report  # noqa: E402

TRANSFORMS = ['clause_split', 'demonstrative_chain', 'paren_isolation', 'lexical_repeat', 'voice_alternation']
# Split first (so later transforms see shorter sentences); parentheticals last.
APPLY_ORDER = ['clause_split', 'voice_alternation', 'demonstrative_chain', 'lexical_repeat', 'paren_isolation']
NEEDS_SPACY = {'clause_split', 'demonstrative_chain', 'lexical_repeat', 'voice_alternation'}

SUBJECT_DEPS = ACS.SUBJECT_DEPS
VOWELS = ACS.VOWELS


# ---------- paragraph helper ----------

def _for_each_paragraph(text, fn):
    """Applies fn to each blank-line-separated paragraph, preserving the separators.
    fn(paragraph_text) -> (new_text, n_changed). Returns (new_text, total_changed)."""
    parts = re.split(r'(\n\s*\n)', text)
    out, changed = [], 0
    for chunk in parts:
        if chunk.strip() == '':
            out.append(chunk)
            continue
        new, n = fn(chunk)
        out.append(new)
        changed += n
    return ''.join(out), changed


# ---------- transform: clause_split ----------

def t_clause_split(text, nlp):
    new, events = ACS.split_text(text, nlp, max_words=16, participial=True)
    return new, sum(1 for k, _, _ in events if k.startswith('split'))


# ---------- transform: paren_isolation (regex, no spaCy) ----------

def _split_parenthetical(inner):
    """Splits the inside of one (...) on top-level ', ' into back-to-back parens.
    A comma not followed by a space (e.g. '3,860') never splits."""
    parts, depth, start = [], 0, 0
    i = 0
    while i < len(inner):
        c = inner[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif c == ',' and depth == 0 and i + 1 < len(inner) and inner[i + 1] == ' ':
            parts.append(inner[start:i])
            start = i + 2
            i += 2
            continue
        i += 1
    parts.append(inner[start:])
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) <= 1:
        return None
    return ' '.join('(' + p + ')' for p in parts)


def t_paren_isolation(text, nlp=None):
    out, changed, i, depth, start = [], 0, 0, 0, 0
    # Walk the string, find top-level (...) groups, rewrite multi-stat ones.
    result = []
    i = 0
    while i < len(text):
        c = text[i]
        if c == '(':
            j, d = i, 0
            while j < len(text):
                if text[j] == '(':
                    d += 1
                elif text[j] == ')':
                    d -= 1
                    if d == 0:
                        break
                j += 1
            if j < len(text):
                inner = text[i + 1:j]
                rewritten = _split_parenthetical(inner)
                if rewritten:
                    result.append(rewritten)
                    changed += 1
                else:
                    result.append(text[i:j + 1])
                i = j + 1
                continue
        result.append(c)
        i += 1
    return ''.join(result), changed


# ---------- transform: demonstrative_chain ----------

def _demonstrative_for(noun_token):
    return 'These' if noun_token.tag_ in ('NNS', 'NNPS') else 'This'


def t_demonstrative_chain(text, nlp):
    def para(chunk):
        doc = nlp(chunk)
        sents = list(doc.sents)
        pieces, changed = [], 0
        for idx, sent in enumerate(sents):
            s = sent.text
            if idx == 0:
                pieces.append(s)
                continue  # first sentence has no antecedent to point back to
            root = next((t for t in sent if t.dep_ == 'ROOT'), None)
            subj = next((t for t in sent if t.dep_ in SUBJECT_DEPS and t.head == root), None) if root else None
            # Only replace a referring COMMON-noun subject (not pronouns, names, or "we/our").
            if (subj is not None and subj.pos_ == 'NOUN'
                    and subj.left_edge.i == sent.start and subj.lemma_.lower() not in ('we', 'i')):
                a = subj.left_edge.idx - sent.start_char
                last = subj.right_edge
                b = last.idx + len(last.text) - sent.start_char
                repl = _demonstrative_for(subj)
                new = s[:a] + repl + s[b:]
                pieces.append(new)
                changed += 1
            else:
                pieces.append(s)
        return ' '.join(pieces), changed
    return _for_each_paragraph(text, para)


# ---------- transform: lexical_repeat ----------

def t_lexical_repeat(text, nlp):
    def para(chunk):
        doc = nlp(chunk)
        pieces, changed = [], 0
        for sent in doc.sents:
            s = sent.text
            edit = None
            for tok in sent:
                # noun coordination: N1 (amod ADJ) ... and N2(conj) ; repeat the adjective before N2.
                # N2 may be a plain noun or a gerund (VBG) acting as a noun in the coordination.
                if tok.dep_ != 'conj' or not (tok.pos_ in ('NOUN', 'PROPN') or tok.tag_ == 'VBG'):
                    continue
                head = tok.head
                if head.pos_ != 'NOUN':
                    continue
                adj = next((c for c in head.children if c.dep_ == 'amod' and c.pos_ == 'ADJ'), None)
                if adj is None or any(c.dep_ == 'amod' for c in tok.children):
                    continue
                pos = tok.idx - sent.start_char   # insert adjective right before the second noun
                edit = (pos, adj.text + ' ')
                break
            if edit:
                pos, ins = edit
                pieces.append(s[:pos] + ins + s[pos:])
                changed += 1
            else:
                pieces.append(s)
        return ' '.join(pieces), changed
    return _for_each_paragraph(text, para)


# ---------- transform: voice_alternation (active -> passive, safe subset) ----------

def t_voice_alternation(text, nlp):
    def para(chunk):
        doc = nlp(chunk)
        pieces, changed = [], 0
        for sent in doc.sents:
            new = _to_passive(sent)
            if new is not None:
                pieces.append(new)
                changed += 1
            else:
                pieces.append(sent.text)
        return ' '.join(pieces), changed
    return _for_each_paragraph(text, para)


def _to_passive(sent):
    """"<Subj> <VBD-ed> <obj> <tail>." -> "<Obj> was/were <VBD> <tail>." or None.
    Restricted to regular -ed verbs (past tense == past participle) with a leading
    subject and a direct object, so the conversion is grammatical without a verb table."""
    root = next((t for t in sent if t.dep_ == 'ROOT' and t.pos_ == 'VERB'), None)
    if root is None or root.tag_ != 'VBD' or not root.text.lower().endswith('ed'):
        return None
    # Skip already-passive clauses and any sentence with a coordinate clause, so we never
    # half-convert "We did X, and Y happened" into a lopsided passive.
    if any(c.dep_ in ('auxpass', 'conj', 'cc') for c in root.children):
        return None
    subj = next((c for c in root.children if c.dep_ in ('nsubj',)), None)
    obj = next((c for c in root.children if c.dep_ == 'dobj'), None)
    if subj is None or obj is None:
        return None
    subj_tokens = list(subj.subtree)
    obj_tokens = list(obj.subtree)
    # Require: subject starts the sentence, verb after subject, object after verb.
    if min(t.i for t in subj_tokens) != sent.start:
        return None
    if not (max(t.i for t in subj_tokens) < root.i < min(t.i for t in obj_tokens)):
        return None
    obj_end = max(t.i for t in obj_tokens)
    tail = [t for t in sent if t.i > obj_end and not (t.is_punct and t.text in '.?!')]
    aux = 'were' if obj.tag_ in ('NNS', 'NNPS') else 'was'
    obj_text = ''.join(t.text_with_ws for t in obj_tokens).strip()
    tail_text = ''.join(t.text_with_ws for t in tail).strip()
    verb = root.text
    sentence = f'{obj_text[:1].upper()}{obj_text[1:]} {aux} {verb}'
    if tail_text:
        sep = '' if tail_text[0] in ',;:' else ' '
        sentence += sep + tail_text
    return sentence.rstrip() + '.'


TRANSFORM_FUNCS = {
    'clause_split': t_clause_split,
    'demonstrative_chain': t_demonstrative_chain,
    'paren_isolation': t_paren_isolation,
    'lexical_repeat': t_lexical_repeat,
    'voice_alternation': t_voice_alternation,
}


# ---------- orchestration ----------

def apply_transforms(text, flags, nlp):
    """Applies enabled transforms in APPLY_ORDER. Returns (new_text, {transform: n_changed})."""
    counts = OrderedDict()
    for name in APPLY_ORDER:
        if not flags.get(name):
            continue
        if name in NEEDS_SPACY and nlp is None:
            counts[name] = 'unavailable (no spaCy)'
            continue
        text, n = TRANSFORM_FUNCS[name](text, nlp)
        counts[name] = n
    return text, counts


def variant_specs(mode):
    """Returns an ordered list of (variant_id, flags_dict). Always includes 'baseline'."""
    off = {t: False for t in TRANSFORMS}
    specs = [('baseline', dict(off))]
    if mode == 'single':
        for t in TRANSFORMS:
            f = dict(off)
            f[t] = True
            specs.append((f'single__{t}', f))
    elif mode == 'all':
        specs.append(('all', {t: True for t in TRANSFORMS}))
    elif mode == 'leave-one-out':
        specs.append(('all', {t: True for t in TRANSFORMS}))
        for t in TRANSFORMS:
            f = {x: True for x in TRANSFORMS}
            f[t] = False
            specs.append((f'loo__minus_{t}', f))
    else:
        raise ValueError(f'unknown mode: {mode}')
    return specs


def fidelity(baseline, variant_text):
    """Runs check_draft and extracts the number-fidelity verdict and key stats."""
    result = check(baseline, variant_text)
    new_numbers = [f['message'] for f in result['findings'] if f['kind'] == 'new-number']
    missing_numbers = [f['message'] for f in result['findings'] if f['kind'] == 'missing-number']
    fails = [f for f in result['findings'] if f['level'] == 'FAIL']
    return {
        'numbers_ok': not new_numbers and not missing_numbers,
        'new_numbers': new_numbers,
        'missing_numbers': missing_numbers,
        'retention': result['stats']['retention'],
        'all_fail_free': not fails,
        'warnings': sum(1 for f in result['findings'] if f['level'] == 'WARN'),
    }


def _counts(text):
    return len(text.split()), len([s for s in segment(text) if not s.heading])


def run(baseline, mode, outdir, nlp):
    """Generates variants, writes files + manifest + report. Returns the manifest dict."""
    os.makedirs(outdir, exist_ok=True)
    base_words, base_sents = _counts(baseline)
    entries = []
    for vid, flags in variant_specs(mode):
        if vid == 'baseline':
            text, counts = baseline, {}
        else:
            text, counts = apply_transforms(baseline, flags, nlp)
        words, sents = _counts(text)
        fid = fidelity(baseline, text) if vid != 'baseline' else {
            'numbers_ok': True, 'new_numbers': [], 'missing_numbers': [], 'retention': 100.0,
            'all_fail_free': True, 'warnings': 0}
        path = os.path.join(outdir, f'{vid}.txt')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text if text.endswith('\n') else text + '\n')
        entries.append(OrderedDict([
            ('id', vid),
            ('active_flags', [t for t in TRANSFORMS if flags.get(t)]),
            ('transforms_applied', counts),
            ('words', words),
            ('word_delta', words - base_words),
            ('sentences', sents),
            ('sentence_delta', sents - base_sents),
            ('numbers_ok', fid['numbers_ok']),
            ('new_numbers', fid['new_numbers']),
            ('missing_numbers', fid['missing_numbers']),
            ('retention_pct', fid['retention']),
            ('warnings', fid['warnings']),
            ('file', os.path.basename(path)),
        ]))
    manifest = OrderedDict([
        ('mode', mode),
        ('baseline_words', base_words),
        ('baseline_sentences', base_sents),
        ('spacy_available', nlp is not None),
        ('variants', entries),
    ])
    with open(os.path.join(outdir, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    with open(os.path.join(outdir, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(_report_md(manifest))
    return manifest


def _report_md(manifest):
    lines = [f'# Ablation Report (mode: {manifest["mode"]})', '',
             f'Baseline: {manifest["baseline_words"]} words, {manifest["baseline_sentences"]} sentences. '
             f'spaCy available: {manifest["spacy_available"]}.', '',
             '| Variant | Active flags | Words (Δ) | Sents (Δ) | Numbers | Retention | Warnings |',
             '| :-- | :-- | --: | --: | :--: | --: | --: |']
    for v in manifest['variants']:
        flags = ', '.join(v['active_flags']) or '(none)'
        numbers = 'PASS' if v['numbers_ok'] else 'FAIL'
        lines.append(f'| {v["id"]} | {flags} | {v["words"]} ({v["word_delta"]:+d}) | '
                     f'{v["sentences"]} ({v["sentence_delta"]:+d}) | {numbers} | {v["retention_pct"]}% | {v["warnings"]} |')
    lines += ['', '## Detector scores (fill in after scanning)', '',
              '| Variant | Detector | AI % | Notes |', '| :-- | :-- | --: | :-- |']
    for v in manifest['variants']:
        lines.append(f'| {v["id"]} |  |  |  |')
    lines += ['', '## Number-fidelity failures', '']
    any_fail = False
    for v in manifest['variants']:
        if not v['numbers_ok']:
            any_fail = True
            lines.append(f'- **{v["id"]}**: new={v["new_numbers"]} missing={v["missing_numbers"]}')
    if not any_fail:
        lines.append('None — every variant preserved all source numbers.')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description='Academic Humanizer v8.0 ablation harness')
    parser.add_argument('input', help='Baseline academic prose (plain text)')
    parser.add_argument('--mode', choices=['single', 'all', 'leave-one-out'], default='single')
    parser.add_argument('--outdir', default=os.path.join('research', 'ablation_runs'))
    parser.add_argument('--model', default='en_core_web_sm', help='spaCy model (default en_core_web_sm)')
    args = parser.parse_args(argv)

    with open(args.input, encoding='utf-8') as f:
        baseline = f.read()
    try:
        nlp = ACS.load_nlp(args.model)
    except Exception:
        nlp = None
        print(f"Warning: spaCy model '{args.model}' not available; only paren_isolation will run.",
              file=sys.stderr)
    manifest = run(baseline, args.mode, args.outdir, nlp)
    print(f'Wrote {len(manifest["variants"])} variants to {args.outdir}/')
    print(f'  manifest.json and report.md written. spaCy available: {manifest["spacy_available"]}.')
    fails = [v['id'] for v in manifest['variants'] if not v['numbers_ok']]
    if fails:
        print('  number-fidelity FAIL on: ' + ', '.join(fails))
    return 0


if __name__ == '__main__':
    sys.exit(main())
