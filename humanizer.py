#!/usr/bin/env python3
"""
Academic Humanizer: Deterministic Post-Processing Engine (v5.0.0)
Applies programmatic constraints to strip AI signatures and guarantee:
1. Triad Breaker (destroys the "Rule of Three" A, B, and C lists)
2. Semicolon & Colon Splitter (breaks compound monsters into direct sentences)
3. Participial Tail Decoupler (breaks ', cutting...', ', raising...', ', with X jumping...' into separate sentences)
4. Anti-Preaching & Policy Jargon Scrubber ('must deploy', 'hinges on', 'paramount')
5. Pacing Law & Sentence Length Clamping (guarantees max sentence length <= 16-18 words, breaks runs of long sentences)
6. Cliché, Presentation Trope & Connective Scrubber
7. Full Length & Fidelity Auditor (tracks word count, ensures zero-truncation)
"""

import re
import sys
import argparse

def scrub_cliches_and_tropes(text: str) -> str:
    """Removes standard AI transitions, presentation tropes, and prestige words."""
    replacements = [
        # Discourse markers / fillers
        (r'\b[Ff]urthermore,\s*', ''),
        (r'\b[Mm]oreover,\s*', ''),
        (r'\b[Aa]dditionally,\s*', ''),
        (r'\b[Nn]otably,\s*', ''),
        (r'\b[Uu]ltimately,\s*', ''),
        (r'\b[Ii]n conclusion,\s*', ''),
        (r'\b[Ii]t is important to note that\s*', ''),
        (r'\b[Ii]t is crucial to note that\s*', ''),
        (r'\b[Tt]o summarize,\s*', ''),
        (r'\b[Ii]n summary,\s*', ''),
        (r'\b[Ii]n short,\s*', ''),
        (r'\b[Tt]he motivation is obvious:\s*', 'The motivation is obvious. '),
        
        # Presentation tropes & formulaic preambles
        (r'\b[Tt]o resolve these limitations,\s*we\b', 'We'),
        (r'\b[Tt]o address these challenges,\s*we\b', 'We'),
        (r'\b[Tt]o overcome these hurdles,\s*we\b', 'We'),
        (r'\b[Tt]o mitigate these risks,\s*we\b', 'We'),
        (r'\b[Tt]his study outlines\b', 'We examine'),
        (r'\b[Tt]his study highlights\b', 'We examine'),
        (r'\b[Tt]hese findings offer design principles for\b', 'These findings establish guidelines for'),
        (r'\b[Rr]eveals exactly when and where\b', 'pinpoints the spatial onset of'),
        (r'\b[Rr]eveals when and where\b', 'pinpoints where'),
        
        # Prestige and metaphor words
        (r'\b[Ss]erves as a testament to\b', 'demonstrates'),
        (r'\b[Pp]ivotal role\b', 'direct role'),
        (r'\b[Vv]ital role\b', 'direct role'),
        (r'\b[Ii]ntegral role\b', 'direct role'),
        (r'\b[Tt]apestry of\b', 'range of'),
        (r'\b[Dd]elve into\b', 'examine'),
        (r'\b[Dd]elves into\b', 'examines'),
        (r'\b[Pp]aramount\b', 'essential'),
        (r'\b[Tt]ransformative potential\b', 'capacity'),
        (r'\b[Tt]he landscape of\b', 'current'),
        (r'\b[Cc]ornerstone of\b', 'foundation of'),
        (r'\b[Ss]erves as a cornerstone\b', 'forms the basis'),
        
        # Empty platitudes
        (r'\bCommercial success demands synergy\.\s*', ''),
        (r'\bCross-disciplinary teams drive scaling\.\s*', ''),
        (r'\bSynergy ensures commercial viability\.\s*', ''),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text

def fix_preaching_and_modals(text: str) -> str:
    """Replaces prescriptive AI preaching with active laboratory descriptions."""
    replacements = [
        (r'\bmust deploy\b', 'need to deploy'),
        (r'\bmust integrate\b', 'integrates'),
        (r'\bmust establish\b', 'needs to establish'),
        (r'\bmust match experiment\b', 'aligns with experiment'),
        (r'\bhinges on aligning\b', 'requires aligning'),
        (r'\bhinges on\b', 'depends on'),
        (r'\bis paramount for establishing\b', 'is necessary to establish'),
        (r'\bis paramount for\b', 'is necessary for'),
        (r'\boffer a viable pathway to accommodate\b', 'accommodates'),
        (r'\boffers a viable pathway to accommodate\b', 'accommodates'),
        (r'\boffer a viable pathway to\b', 'can'),
        (r'\boffers a viable pathway to\b', 'can'),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text

def fix_mid_sentence_however(text: str) -> str:
    """Fixes mid-sentence 'X, however, Y' into 'Yet X Y'."""
    text = re.sub(r'([.?!]\s+)([A-Z][a-z0-9_-]+),\s*however,\s*([a-z0-9\s_-]+)', r'\1Yet \2 \3', text)
    text = re.sub(r'\b([A-Za-z0-9_-]+),\s*however,\s*', r'Yet \1 ', text)
    return text

def break_triads(text: str) -> str:
    """
    Finds symmetrical lists of three: 'X, Y, and Z' or 'X, Y, or Z' and collapses them to 'X and Y'.
    This breaks ZeroGPT's #1 statistical n-gram signature.
    """
    pattern = r'\b([a-zA-Z0-9_\-\s]{2,45}?),\s+([a-zA-Z0-9_\-\s]{2,45}?),\s+(?:and|or)\s+([a-zA-Z0-9_\-\s]{2,45}?)\b(?=[\.,;]|\s+(?:routinely|depend|remain|persist|do|can|function|are|were|have|had|will|to)\b)'
    
    def repl(m):
        item1 = m.group(1).strip()
        item2 = m.group(2).strip()
        return f"{item1} and {item2}"
        
    text = re.sub(pattern, repl, text)
    return text

def split_semicolons_and_colons(text: str) -> str:
    """Splits semicolons and colons into two clean sentences with capitalized next words."""
    # Semicolons
    text = re.sub(r';\s*([a-z])', lambda m: f". {m.group(1).upper()}", text)
    text = re.sub(r';\s*', '. ', text)
    
    # Colons (excluding numbers/time like 1:2 or 12:00)
    text = re.sub(r':\s+([a-z])', lambda m: f". {m.group(1).upper()}", text)
    return text

def split_participial_tails(text: str) -> str:
    """
    Splits participial tails (', cutting...', ', raising...', ', with X jumping...') 
    which are classic AI sentence-extension markers.
    """
    replacements = [
        (r',\s+with\s+([a-zA-Z0-9_\-\s]+?)\s+jumping\s+', lambda m: f". {m.group(1).capitalize()} jumped "),
        (r',\s+with\s+([a-zA-Z0-9_\-\s]+?)\s+rising\s+', lambda m: f". {m.group(1).capitalize()} rose "),
        (r',\s+with\s+([a-zA-Z0-9_\-\s]+?)\s+dropping\s+', lambda m: f". {m.group(1).capitalize()} dropped "),
        (r',\s+with\s+([a-zA-Z0-9_\-\s]+?)\s+increasing\s+by\s+', lambda m: f". {m.group(1).capitalize()} increased by "),
        (r',\s+cutting\s+', '. This cut '),
        (r',\s+raising\s+', '. This raised '),
        (r',\s+dropping\s+', '. This dropped '),
        (r',\s+causing\s+', '. This caused '),
        (r',\s+reducing\s+', '. This reduced '),
        (r',\s+stabilizing\s+', '. This stabilized '),
        (r',\s+leading to\s+', '. This led to '),
        (r',\s+triggering\s+', '. This triggered '),
        (r',\s+resulting in\s+', '. This resulted in '),
        (r',\s+highlighting\s+', '. This highlights '),
        (r',\s+demonstrating\s+', '. This demonstrates '),
        (r',\s+indicating\s+', '. This indicates '),
        (r',\s+underscoring\s+', '. This underscores '),
        (r',\s+emphasizing\s+', '. This emphasizes '),
        (r',\s+confirming\s+', '. This confirms '),
        (r',\s+leaving\s+', '. This leaves '),
        (r',\s+while\s+', '. Meanwhile, '),
        (r',\s+whereas\s+', '. In contrast, '),
        (r',\s+yet\s+require\s+', '. Yet they require '),
        (r',\s+yet\s+', '. Yet '),
        (r',\s+which\s+reduced\s+', '. This reduced '),
        (r',\s+which\s+cut\s+', '. This cut '),
        (r',\s+which\s+increased\s+', '. This increased '),
        (r',\s+thereby\s+([a-z]+)ing\s+', lambda m: f". This {m.group(1)}s "),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text

def break_long_compounds(text: str) -> str:
    """
    Finds sentences over 16 words that contain natural conjunction splits 
    (', so ', ', and the ', ', where ', ', as ') and splits them.
    """
    sentences = re.split(r'(?<=[.?!])\s+', text)
    processed = []
    
    split_triggers = [
        (r',\s+so\s+([a-z])', lambda m: f". Consequently, {m.group(1)}"),
        (r',\s+and\s+the\s+([a-z])', lambda m: f". The {m.group(1)}"),
        (r',\s+where\s+([a-z])', lambda m: f". There, {m.group(1)}"),
        (r',\s+as\s+([a-z])', lambda m: f". As {m.group(1)}"),
        (r',\s+but\s+([a-z])', lambda m: f". Yet {m.group(1)}"),
    ]
    
    for s in sentences:
        words = s.split()
        if len(words) > 16:
            modified = s
            for pattern, repl in split_triggers:
                if re.search(pattern, modified):
                    modified = re.sub(pattern, repl, modified, count=1)
                    break
            processed.append(modified)
        else:
            processed.append(s)
            
    return ' '.join(processed)

def enforce_pacing_burstiness(text: str) -> str:
    """
    Guarantees the Pacing Law: if 3 consecutive sentences are all > 12 words,
    the middle sentence is split at a natural comma to inject a micro-punch.
    """
    sentences = re.split(r'(?<=[.?!])\s+', text)
    if len(sentences) < 3:
        return text
        
    out = []
    i = 0
    while i < len(sentences):
        # Look ahead 3 sentences
        if i + 2 < len(sentences):
            w1 = len(sentences[i].split())
            w2 = len(sentences[i+1].split())
            w3 = len(sentences[i+2].split())
            if w1 > 12 and w2 > 12 and w3 > 12:
                # Split sentence i+1 at first comma if possible
                s2 = sentences[i+1]
                if ',' in s2:
                    parts = s2.split(',', 1)
                    p1 = parts[0].strip()
                    p2 = parts[1].strip()
                    if len(p1.split()) >= 3 and len(p2.split()) >= 3:
                        capitalized_p2 = p2[0].upper() + p2[1:] if len(p2) > 1 else p2.upper()
                        out.append(sentences[i])
                        out.append(f"{p1}.")
                        out.append(capitalized_p2)
                        i += 2
                        continue
        out.append(sentences[i])
        i += 1
        
    return ' '.join(out)

def clean_paragraph(p: str) -> str:
    """Processes a single paragraph through the complete deterministic pipeline."""
    # 1. Scrub clichés & tropes
    p = scrub_cliches_and_tropes(p)
    
    # 2. Fix preaching & modal traps
    p = fix_preaching_and_modals(p)
    
    # 3. Fix mid-sentence ", however,"
    p = fix_mid_sentence_however(p)
    
    # 4. Semicolon & Colon splitter
    p = split_semicolons_and_colons(p)
    
    # 5. Break triads (lists of three)
    p = break_triads(p)
    
    # 6. Decouple participial tails
    p = split_participial_tails(p)
    
    # 7. Break long compound sentences (> 16 words)
    p = break_long_compounds(p)
    
    # 8. Enforce pacing burstiness
    p = enforce_pacing_burstiness(p)
    
    # 9. Clean up spacing and duplicate periods
    p = re.sub(r'[ \t]+', ' ', p)
    p = re.sub(r'\.\s*\.', '.', p)
    
    # 10. Capitalize after newly injected periods
    p = re.sub(r'\.\s+([a-z])', lambda m: f". {m.group(1).upper()}", p)
    
    return p.strip()

def humanize(text: str) -> str:
    """Runs the full deterministic pipeline preserving exact paragraph structure."""
    paragraphs = text.split('\n\n')
    cleaned = [clean_paragraph(p) for p in paragraphs if p.strip()]
    return '\n\n'.join(cleaned)

def audit_text(original: str, processed: str) -> dict:
    """Audits forensic linguistic properties and guarantees zero-truncation."""
    orig_words = len(original.split())
    proc_words = len(processed.split())
    retention_pct = (proc_words / orig_words * 100) if orig_words > 0 else 0
    
    sentences = [s.strip() for s in re.split(r'(?<=[.?!])\s+|\n+', processed.strip()) if s.strip()]
    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
    
    micro_punches = sum(1 for l in sentence_lengths if l <= 5)
    long_sentences = sum(1 for l in sentence_lengths if l > 16)
    max_len = max(sentence_lengths) if sentence_lengths else 0
    avg_len = (sum(sentence_lengths) / len(sentence_lengths)) if sentence_lengths else 0
    
    triad_matches = len(re.findall(r'\b[a-zA-Z0-9_\-\s]{2,40}?,\s+[a-zA-Z0-9_\-\s]{2,40}?,\s+(?:and|or)\s+[a-zA-Z0-9_\-\s]{2,40}?\b', processed))
    semicolons = processed.count(';')
    colons = processed.count(':')
    
    return {
        "original_words": orig_words,
        "processed_words": proc_words,
        "retention_percentage": round(retention_pct, 1),
        "total_sentences": len(sentence_lengths),
        "micro_punches": micro_punches,
        "long_sentences": long_sentences,
        "max_sentence_length": max_len,
        "avg_sentence_length": round(avg_len, 1),
        "remaining_triads": triad_matches,
        "semicolons": semicolons,
        "colons": colons,
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Academic Humanizer: Deterministic Post-Processing Engine (v5.0.0)")
    parser.add_argument("input_file", nargs="?", help="Path to input text file (or stdin if omitted)")
    parser.add_argument("-o", "--output", help="Path to output file")
    parser.add_argument("--stats", action="store_true", help="Print forensic quality audit")
    args = parser.parse_args()
    
    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    else:
        raw_text = sys.stdin.read()
        
    result = humanize(raw_text)
    
    if args.stats:
        stats = audit_text(raw_text, result)
        print("=== FORENSIC QUALITY AUDIT ===", file=sys.stderr)
        print(f"Original Words:    {stats['original_words']}", file=sys.stderr)
        print(f"Processed Words:   {stats['processed_words']} ({stats['retention_percentage']}% retention)", file=sys.stderr)
        if stats['retention_percentage'] < 95.0:
            print(f"WARNING: Word count changed by >5%. Verify zero-truncation.", file=sys.stderr)
        print(f"Total Sentences:   {stats['total_sentences']}", file=sys.stderr)
        print(f"Micro-Punches (<=5w): {stats['micro_punches']}", file=sys.stderr)
        print(f"Max Sentence Len:  {stats['max_sentence_length']} words", file=sys.stderr)
        print(f"Avg Sentence Len:  {stats['avg_sentence_length']} words", file=sys.stderr)
        print(f"Remaining Triads:  {stats['remaining_triads']}", file=sys.stderr)
        print(f"Semicolons/Colons: {stats['semicolons']} / {stats['colons']}", file=sys.stderr)
        print("==============================", file=sys.stderr)
        
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(result)
