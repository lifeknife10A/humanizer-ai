#!/usr/bin/env python3
"""
Academic Humanizer v8.0 — Stage 2: Rephraser scaffold with strict fidelity gates
(research prototype)

Ablation Study 1 established that deterministic surface tricks cannot beat an
enterprise detector: clause splitting was null (75%->77%) and dictionary swapping
was worse (75%->91%, triggering Turnitin's AIR-1 "AI-revised" paraphrase
classifier). The only path that worked empirically was end-to-end neural
regeneration. This module is NOT that regenerator; it is the **fidelity-rejection
gate and plumbing around one** — the repo's actual, durable contribution.

IMPORTANT, read before trusting any output:
  * This scaffold does not, by itself, beat any detector. It generates candidate
    rephrasings (via a pluggable generator you supply) and KEEPS one only if it
    passes strict fidelity gates, else it keeps the original paragraph.
  * Best-of-N "selection" is only as good as its guidance scorer, and the repo
    has no evidence any LOCAL scorer transfers to Turnitin (label study: proxies
    at chance; AuthorMist: 2% cross-detector). The default scorer expresses NO
    preference (keeps the first passing candidate). Do not read a low proxy score
    as "this will pass Turnitin". Validate against the real detector.

Architecture:
  Generator (pluggable):  generate(text, n) -> [candidate strings]
    - NullGenerator   : returns [text]          (passthrough; for tests/plumbing)
    - FileGenerator   : returns pre-supplied candidates (external drafts, Clever
                        AI output, previous rounds) to run them through the gates
    - OllamaGenerator : calls a local Ollama model (base or instruct) over HTTP
  FidelityGate (the moat; deterministic, light deps):
    - numbers EXACT     : extract_numbers(orig) == extract_numbers(cand)   (H1)
    - terms EXACT       : extract_terms(orig)  == extract_terms(cand)      (H2)
    - length band       : retention within [min, max] (no truncation/padding, H5)
    - meaning preserved : SBERT cosine >= --sbert-threshold if sentence-transformers
                          is installed; ELSE content-lemma-stem overlap (Jaccard)
                          >= --overlap-threshold as a conservative fallback.
    NOTE: for a rephraser we do NOT require content-lemma *equality* (that is the
    splitter's gate and would reject every real paraphrase); meaning is guarded by
    semantic similarity instead.
  GuidanceScorer (pluggable, optional): score(text) -> float, lower = more human.
    - NullScorer : 0.0 for everything (no preference). Real proxies are future
                   work and must be calibrated against the target detector first.

Usage:
  stage2_rephraser.py INPUT.txt --generator null|ollama -o OUT.txt [--source SRC]
                      [--n 4] [--model llama3.2] [--sbert-threshold 0.9]
  stage2_rephraser.py INPUT.txt --gate-draft CANDIDATE.txt   # just gate an external draft
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

_SKILL = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',
                                      'skills', 'academic-humanizer', 'scripts'))
if _SKILL not in sys.path:
    sys.path.insert(0, _SKILL)
from check_draft import extract_numbers, extract_terms, _stems, check, format_report  # noqa: E402

DEFAULT_SBERT_THRESHOLD = 0.90
DEFAULT_OVERLAP_THRESHOLD = 0.34   # conservative content-stem Jaccard when SBERT is absent
MIN_RETENTION = 0.90
MAX_RETENTION = 1.15


# ---------- generators ----------

class Generator:
    def generate(self, text, n):
        raise NotImplementedError


class NullGenerator(Generator):
    """Passthrough: the original text is its own only candidate. Exercises the gates/plumbing."""
    def generate(self, text, n):
        return [text]


class FileGenerator(Generator):
    """Serves pre-supplied candidates (external humanized drafts, Clever AI output, prior rounds).
    Built with a dict {stripped_input_text: [candidate, ...]}; returns [] for unknown inputs."""
    def __init__(self, candidates_by_text):
        self.candidates = {' '.join(k.split()): v for k, v in candidates_by_text.items()}

    def generate(self, text, n):
        return list(self.candidates.get(' '.join(text.split()), []))[:n]

    @classmethod
    def from_aligned(cls, baseline_paragraphs, candidate_paragraphs):
        """Pairs baseline paragraphs with candidate paragraphs by index (one candidate each)."""
        mapping = {}
        for base, cand in zip(baseline_paragraphs, candidate_paragraphs):
            mapping.setdefault(base, []).append(cand)
        return cls(mapping)


class OllamaGenerator(Generator):
    """Calls a local Ollama model (base or instruct). Network errors yield [] so the loop
    falls back to the original paragraph. stdlib-only (urllib); no new dependency."""
    PROMPT = ('Rewrite the following academic paragraph in plain, direct, human academic English. '
              'Keep every number, statistic, citation, and technical term exactly. Do not add or '
              'remove facts. Return only the rewritten paragraph.\n\nParagraph:\n{text}\n\nRewrite:')

    def __init__(self, model='llama3.2', host='http://localhost:11434', temperature=0.8, timeout=120):
        self.model, self.host, self.temperature, self.timeout = model, host, temperature, timeout

    def generate(self, text, n):
        out = []
        for _ in range(n):
            cand = self._one(text)
            if cand:
                out.append(cand)
        return out

    def _one(self, text):
        body = json.dumps({
            'model': self.model,
            'prompt': self.PROMPT.format(text=text),
            'stream': False,
            'options': {'temperature': self.temperature},
        }).encode('utf-8')
        req = urllib.request.Request(f'{self.host}/api/generate', data=body,
                                     headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode('utf-8')).get('response', '').strip()
        except (urllib.error.URLError, OSError, ValueError):
            return None


# ---------- guidance scorers ----------

class GuidanceScorer:
    def score(self, text):
        raise NotImplementedError


class NullScorer(GuidanceScorer):
    """Expresses no preference. Selection then keeps the first passing candidate."""
    def score(self, text):
        return 0.0


# ---------- fidelity gate ----------

_SBERT_MODEL = None


def _sbert():
    """Lazily loads a sentence-transformers model, or returns None if unavailable."""
    global _SBERT_MODEL
    if _SBERT_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer, util  # noqa: F401
            _SBERT_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            _SBERT_MODEL = False
    return _SBERT_MODEL or None


def _overlap(a, b):
    """Jaccard overlap of content-word stems (check_draft._stems). Cheap meaning proxy."""
    sa, sb = _stems(a), _stems(b)
    if not sa or not sb:
        return 1.0 if sa == sb else 0.0
    return len(sa & sb) / len(sa | sb)


def semantic_similarity(original, candidate):
    """(score, method). SBERT cosine if available, else content-stem Jaccard."""
    model = _sbert()
    if model is not None:
        from sentence_transformers import util
        emb = model.encode([original, candidate])
        return float(util.cos_sim(emb[0], emb[1])), 'sbert'
    return _overlap(original, candidate), 'overlap'


def _words(text):
    return len(text.split())


class FidelityGate:
    def __init__(self, sbert_threshold=DEFAULT_SBERT_THRESHOLD, overlap_threshold=DEFAULT_OVERLAP_THRESHOLD,
                 min_retention=MIN_RETENTION, max_retention=MAX_RETENTION):
        self.sbert_threshold = sbert_threshold
        self.overlap_threshold = overlap_threshold
        self.min_retention = min_retention
        self.max_retention = max_retention

    def check(self, original, candidate):
        """Returns (passed, details). A candidate passes only if every gate passes."""
        reasons = []
        if extract_numbers(original) != extract_numbers(candidate):
            reasons.append('numbers changed')
        if extract_terms(original) != extract_terms(candidate):
            reasons.append('terms/acronyms changed')
        ratio = _words(candidate) / max(1, _words(original))
        if not (self.min_retention <= ratio <= self.max_retention):
            reasons.append(f'length ratio {ratio:.2f} outside [{self.min_retention}, {self.max_retention}]')
        sim, method = semantic_similarity(original, candidate)
        threshold = self.sbert_threshold if method == 'sbert' else self.overlap_threshold
        if sim < threshold:
            reasons.append(f'{method} similarity {sim:.2f} < {threshold}')
        return (not reasons), {'reasons': reasons, 'similarity': round(sim, 3), 'method': method,
                               'length_ratio': round(ratio, 3)}


# ---------- paragraph-level rephrase loop ----------

def _paragraphs(text):
    """Blank-line-separated paragraphs, with their separators, so structure is preserved."""
    return re.split(r'(\n\s*\n)', text)


def rephrase(baseline, generator, gate, n=4, scorer=None):
    """Rephrases each paragraph; keeps the best passing candidate, else the original.
    Returns (new_text, events)."""
    scorer = scorer or NullScorer()
    out, events = [], []
    for chunk in _paragraphs(baseline):
        if chunk.strip() == '':
            out.append(chunk)
            continue
        candidates = generator.generate(chunk, n)
        passing = []
        for cand in candidates:
            ok, details = gate.check(chunk, cand)
            if ok and ' '.join(cand.split()) != ' '.join(chunk.split()):
                passing.append((scorer.score(cand), cand, details))
        if passing:
            passing.sort(key=lambda t: t[0])   # lowest guidance score = most human (if a scorer is set)
            _, chosen, details = passing[0]
            out.append(chosen)
            events.append({'status': 'rephrased', 'candidates': len(candidates),
                           'passed': len(passing), 'detail': details, 'original': chunk.strip()[:80]})
        else:
            out.append(chunk)
            events.append({'status': 'kept-original', 'candidates': len(candidates),
                           'passed': 0, 'original': chunk.strip()[:80]})
    return ''.join(out), events


def gate_document(baseline, candidate_doc, gate):
    """Use case 2: gate an externally humanized draft, paragraph-aligned, without generating.
    Returns a list of per-paragraph {passed, detail}."""
    base = [p for p in _paragraphs(baseline) if p.strip()]
    cand = [p for p in _paragraphs(candidate_doc) if p.strip()]
    results = []
    for i, b in enumerate(base):
        if i >= len(cand):
            results.append({'index': i, 'passed': False, 'detail': {'reasons': ['no aligned candidate paragraph']}})
            continue
        ok, detail = gate.check(b, cand[i])
        results.append({'index': i, 'passed': ok, 'detail': detail})
    return results


# ---------- CLI ----------

def _build_generator(name, args):
    if name == 'null':
        return NullGenerator()
    if name == 'ollama':
        return OllamaGenerator(model=args.model, temperature=args.temperature)
    raise ValueError(f'unknown generator {name} (CLI supports null, ollama; FileGenerator is programmatic)')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Academic Humanizer v8.0 Stage 2 rephraser scaffold')
    parser.add_argument('input', help='Baseline academic prose (plain text)')
    parser.add_argument('--generator', choices=['null', 'ollama'], default='null')
    parser.add_argument('--gate-draft', metavar='CANDIDATE', help='Only gate this external draft against INPUT')
    parser.add_argument('-o', '--output', help='Where to write the rephrased text (default: stdout)')
    parser.add_argument('--source', help='Original source for a final check_draft report')
    parser.add_argument('--n', type=int, default=4, help='Candidates per paragraph (default 4)')
    parser.add_argument('--model', default='llama3.2', help='Ollama model (default llama3.2)')
    parser.add_argument('--temperature', type=float, default=0.8)
    parser.add_argument('--sbert-threshold', type=float, default=DEFAULT_SBERT_THRESHOLD)
    args = parser.parse_args(argv)

    with open(args.input, encoding='utf-8') as f:
        baseline = f.read()
    gate = FidelityGate(sbert_threshold=args.sbert_threshold)

    if args.gate_draft:
        with open(args.gate_draft, encoding='utf-8') as f:
            cand = f.read()
        results = gate_document(baseline, cand, gate)
        passed = sum(r['passed'] for r in results)
        print(f'Gated {len(results)} paragraphs: {passed} pass, {len(results) - passed} fail.')
        for r in results:
            if not r['passed']:
                print(f"  paragraph {r['index']}: {', '.join(r['detail']['reasons'])}")
        return 0 if passed == len(results) else 1

    generator = _build_generator(args.generator, args)
    new_text, events = rephrase(baseline, generator, gate, n=args.n)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(new_text if new_text.endswith('\n') else new_text + '\n')
        with open(args.output + '.manifest.json', 'w', encoding='utf-8') as f:
            json.dump({'generator': args.generator, 'n': args.n, 'events': events}, f, indent=2)
        print(f'Written: {args.output} (+ .manifest.json)')
    else:
        sys.stdout.write(new_text)
    rephrased = sum(1 for e in events if e['status'] == 'rephrased')
    print(f'Paragraphs rephrased: {rephrased}/{len([e for e in events])}; '
          f'kept original: {sum(1 for e in events if e["status"] == "kept-original")}.', file=sys.stderr)
    if args.source:
        with open(args.source, encoding='utf-8') as f:
            source = f.read()
        print('\n' + format_report(check(source, new_text)), file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
