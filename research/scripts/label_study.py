#!/usr/bin/env python3
"""
Reproduces the ZeroGPT sentence-label study in research/ZEROGPT_LABEL_STUDY.md.

For each labelled rewrite it computes per-sentence features and reports how well
each one separates sentences ZeroGPT highlighted from those it did not (AUC).

  python3 research/scripts/label_study.py            # surface features only
  python3 research/scripts/label_study.py --lm       # also GPT-2 / Qwen2.5-0.5B features
                                                     # (needs torch + transformers)
"""

import argparse
import json
import math
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'academic-humanizer', 'scripts'))
from check_draft import segment  # noqa: E402

DATA = os.path.join(ROOT, 'research', 'data')
NOMINAL = re.compile(r'\b\w{3,}(?:tions?|sions?|ments?|ness|ity|ities|ances?|ences?|isms?)\b', re.IGNORECASE)
ING = re.compile(r'\b\w{3,}ing\b')


def load():
    labels = json.load(open(os.path.join(DATA, 'zerogpt_sentence_labels.json')))
    docs = {}
    for name, d in labels.items():
        text = open(os.path.join(DATA, d['file']), encoding='utf-8').read()
        rows, unknown = [], False
        for s in segment(text):
            if s.heading:
                continue
            if d.get('unknown_from_prefix') and s.text.startswith(d['unknown_from_prefix']):
                unknown = True
            if unknown or any(s.text.startswith(u) for u in d.get('unknown_prefixes', [])):
                label = None
            else:
                label = int(any(s.text.startswith(y) for y in d['yellow_prefixes']))
            rows.append({'text': s.text, 'label': label})
        docs[name] = {'text': text, 'rows': rows, 'score': d['zerogpt_score']}
    return docs


def auc(xs, ys):
    pos = [x for x, y in zip(xs, ys) if y == 1]
    neg = [x for x, y in zip(xs, ys) if y == 0]
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def surface_features(rows):
    n = len(rows)
    for i, r in enumerate(rows):
        words = re.findall(r"[A-Za-z][A-Za-z'-]*", r['text']) or ['x']
        r['f'] = {
            'earlier_in_document': -i / n,
            'length_words': len(words),
            'mean_word_length': sum(map(len, words)) / len(words),
            'long_word_rate': sum(len(w) >= 9 for w in words) / len(words),
            'nominalization_rate': len(NOMINAL.findall(r['text'])) / len(words),
            'ing_rate': len(ING.findall(r['text'])) / len(words),
            'no_digit': -int(bool(re.search(r'\d', r['text']))),
        }


def lm_features(docs):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(os.cpu_count() or 4)
    for model_name in ('gpt2', 'Qwen/Qwen2.5-0.5B'):
        tok = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name).eval()
        ctx = min(getattr(model.config, 'max_position_embeddings', 1024), 2048)
        short = model_name.split('/')[-1]
        for doc in docs.values():
            enc = tok(doc['text'], return_offsets_mapping=True)
            ids, offs = enc['input_ids'], enc['offset_mapping']
            token_stats = []
            with torch.no_grad():
                for start in range(0, len(ids), ctx // 2):
                    window = ids[max(0, start - ctx // 2):start + ctx // 2]
                    if len(window) < 2:
                        continue
                    logits = model(torch.tensor([window])).logits[0]
                    lp = torch.log_softmax(logits, -1)
                    first = start - max(0, start - ctx // 2)
                    for j in range(max(first, 1), len(window)):
                        t = window[j]
                        rank = int((logits[j - 1] > logits[j - 1][t]).sum()) + 1
                        token_stats.append((offs[max(0, start - ctx // 2) + j], -lp[j - 1][t].item(), rank))
            pos = 0
            for r in doc['rows']:
                a = doc['text'].find(r['text'][:30], pos)
                b = a + len(r['text'])
                pos = max(pos, a)
                toks = [(nll, rank) for (o, nll, rank) in token_stats if o[0] >= a and o[1] <= b]
                if toks:
                    r['f'][f'{short}_mean_nll'] = sum(t[0] for t in toks) / len(toks)
                    r['f'][f'{short}_top10_share'] = sum(t[1] <= 10 for t in toks) / len(toks)
                    r['f'][f'{short}_mean_logrank'] = sum(math.log(t[1]) for t in toks) / len(toks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lm', action='store_true', help='add language-model features')
    args = parser.parse_args()
    docs = load()
    for doc in docs.values():
        surface_features(doc['rows'])
    if args.lm:
        lm_features(docs)

    rows = [r for d in docs.values() for r in d['rows'] if r['label'] is not None]
    print(f'Labelled sentences: {len(rows)} ({sum(r["label"] for r in rows)} highlighted)\n')
    for name, d in docs.items():
        known = [r for r in d['rows'] if r['label'] is not None]
        print(f'{name}: ZeroGPT {d["score"]}%, highlighted {sum(r["label"] for r in known)}/{len(known)} '
              f'= {sum(r["label"] for r in known) / len(known) * 100:.1f}% of known sentences')

    seq = [r['label'] for d in docs.values() for r in d['rows'] if r['label'] is not None]
    pairs = list(zip(seq, seq[1:]))
    after_y = [b for a, b in pairs if a == 1]
    after_n = [b for a, b in pairs if a == 0]
    print(f'\nP(highlighted | previous highlighted) = {sum(after_y) / len(after_y):.2f}')
    print(f'P(highlighted | previous not)         = {sum(after_n) / len(after_n):.2f}\n')

    print('AUC per feature (0.5 = chance; >0.5 = higher value -> more likely highlighted)')
    ys = [r['label'] for r in rows]
    for key in rows[0]['f']:
        xs = [r['f'].get(key, float('nan')) for r in rows]
        keep = [(x, y) for x, y in zip(xs, ys) if x == x]
        print(f'  {key:28s} {auc([k[0] for k in keep], [k[1] for k in keep]):.2f}')


if __name__ == '__main__':
    main()
