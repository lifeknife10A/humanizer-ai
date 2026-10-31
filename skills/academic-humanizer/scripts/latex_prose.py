#!/usr/bin/env python3
"""
Academic Humanizer: LaTeX Prose Extractor (v7.14.0)

A rewrite of a LaTeX paper must change its prose and nothing else. This script
turns a .tex file into a plain-text prose view, with every piece of LaTeX the
rewrite must not touch replaced by a numbered placeholder. After the rewrite it
puts the .tex file back together from the rewritten view.

  latex_prose.py extract PAPER.tex -o source.txt --map paper.map.json [--legend legend.txt]
  latex_prose.py restore DRAFT.txt --map paper.map.json -o PAPER_NEW.tex [--compile]

Placeholders in the prose view:
  ⟦n⟧          LaTeX kept exactly as it is: math, \\cite, \\ref, \\label, comments,
               figures, tables, other environments and commands. Keep each one
               exactly once, in the same place in its sentence.
  ⟦n⟧...⟦/n⟧   a command whose argument is prose: section headings, \\emph, \\textbf,
               \\footnote. Reword the text between the markers; keep both markers.

The preamble, the title and author block, keywords, figure and table
environments (captions included) and the bibliography are kept whole. List
items keep their \\item markers.

In the prose view, LaTeX escapes and ligatures are plain characters: \\% is %,
\\& is &, `` and '' are curly quotes, --- is an em dash, -- an en dash, ~ a no-break
space. restore converts them back. The prose may not contain a backslash, ~ or ^.

Prose that wasn't changed is restored byte for byte. Rewritten prose may differ
from the original in line breaks and spacing, which LaTeX ignores.

Exit codes: 0 ok, 1 compile or verification failure,
            2 the draft's placeholders don't match the map (nothing written).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter

OPEN, CLOSE = '\u27e6', '\u27e7'
TOKEN = re.compile(r'\u27e6(/?)(\d+)\u27e7')
NBSP, THIN = '\u00a0', '\u202f'

# Commands whose single argument is prose: the wrapper is kept, the text can be reworded.
PAIRED = {'emph', 'textbf', 'textit', 'textsl', 'textsc', 'textup', 'textmd', 'textrm', 'textnormal',
          'underline', 'footnote', 'part', 'chapter', 'section', 'subsection', 'subsubsection',
          'paragraph', 'subparagraph'}
HEADINGS = {'part', 'chapter', 'section', 'subsection', 'subsubsection', 'paragraph', 'subparagraph'}
# Environments whose body is prose. Every other environment is kept whole.
PROSE_ENVS = {'abstract', 'itemize', 'enumerate', 'description', 'quote', 'quotation', 'center',
              'flushleft', 'flushright'}
ESCAPED = '%&#_${}'
SOFT = {' ': ' ', '\n': ' ', '@': '', '/': '', '-': ''}   # control symbols the prose view drops
PROSE_CONTROL = ESCAPED + ',' + ''.join(SOFT)
ACCENTS = set('\'"`^~=.')
CONTROL = re.compile(r'\\(?:([A-Za-z@]+)(\*?)|(.))', re.S)
BEGIN = re.compile(r'\\begin\s*\{([^{}]*)\}')
FORBIDDEN = re.compile(r'[\\~^]')


class PlaceholderError(Exception):
    def __init__(self, problems):
        super().__init__('\n'.join(problems))
        self.problems = problems


# ---------- prose conversion ----------

def _to_view(raw):
    """LaTeX prose to plain text: escapes, quotes, dashes and spaces become ordinary characters."""
    out, i = [], 0
    while i < len(raw):
        c = raw[i]
        if c == '\\' and i + 1 < len(raw):
            n = raw[i + 1]
            if n in ESCAPED:
                out.append(n)
            elif n == ',':
                out.append(THIN)
            else:
                out.append(SOFT.get(n, c + n))
            i += 2
            continue
        out.append(NBSP if c == '~' else c)
        i += 1
    text = ''.join(out)
    text = (text.replace('---', '\u2014').replace('--', '\u2013')
            .replace('``', '\u201c').replace("''", '\u201d'))
    # A single line break is a space; a blank line stays a paragraph break.
    return re.sub(r'[ \t\r\n]+',
                  lambda m: '\n\n' if m.group().count('\n') >= 2 else (' ' if '\n' in m.group() else m.group()),
                  text)


def _to_raw(view):
    """Plain text back to LaTeX prose."""
    text = ''.join('\\' + c if c in ESCAPED else c for c in view)
    return (text.replace('\u2014', '---').replace('\u2013', '--').replace('\u201c', '``')
            .replace('\u201d', "''").replace(NBSP, '~').replace(THIN, '\\,'))


# ---------- scanning helpers ----------

def _group_end(s, i, end, opener='{', closer='}'):
    """Index just past the group that opens at s[i], skipping escapes and comments."""
    depth, j = 0, i
    while j < end:
        ch = s[j]
        if ch == '\\':
            j += 2
            continue
        if ch == '%':
            nl = s.find('\n', j, end)
            j = end if nl < 0 else nl + 1
            continue
        if opener == '[' and ch == '{':
            j = _group_end(s, j, end)
            continue
        if ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return end


def _math_end(s, i, end):
    delim = '$$' if s.startswith('$$', i) else '$'
    j = i + len(delim)
    while j < end:
        if s[j] == '\\':
            j += 2
            continue
        if s.startswith(delim, j):
            return j + len(delim)
        j += 1
    return end


def _args(s, j, end, brackets_only=False):
    """Index just past the [..] and {..} arguments that directly follow a command."""
    while j < end and (s[j] == '[' or (s[j] == '{' and not brackets_only)):
        j = _group_end(s, j, end, *(('[', ']') if s[j] == '[' else ('{', '}')))
    return j


def _env_end(s, j, end, name):
    """(start, end) of the \\end{name} that closes an environment whose body starts at j."""
    depth = 1
    for m in re.finditer(r'\\(begin|end)\s*\{' + re.escape(name) + r'\}', s[:end]):
        if m.start() < j:
            continue
        depth += 1 if m.group(1) == 'begin' else -1
        if depth == 0:
            return m.start(), m.end()
    return end, end


# ---------- extraction ----------

class _Extractor:
    def __init__(self):
        self.parts = []        # ('raw', latex) | ('brk',) | ('tok', inner)
        self.atoms, self.pairs, self.headings = {}, {}, []
        self.inputs = []
        self.n = 0

    def _new(self):
        self.n += 1
        return str(self.n)

    def prose(self, text):
        if text:
            self.parts.append(('raw', text))

    def brk(self):
        self.parts.append(('brk',))

    def atom(self, text):
        # A no-break space right before a citation, reference or formula travels with it.
        if self.parts and self.parts[-1][0] == 'raw' and self.parts[-1][1].endswith('~') \
                and not self.parts[-1][1].endswith('\\~'):
            self.parts[-1] = ('raw', self.parts[-1][1][:-1])
            text = '~' + text
        n = self._new()
        self.atoms[n] = text
        self.parts.append(('tok', n))

    def parse(self, s, i, end):
        start = i
        while i < end:
            c = s[i]
            if c == '\\' and i + 1 < end and s[i + 1] in PROSE_CONTROL:
                i += 2
                continue
            if c in '%$\\{}':
                self.prose(s[start:i])
                i = self._special(s, i, end)
                start = i
                continue
            i += 1
        self.prose(s[start:end])

    def _special(self, s, i, end):
        c = s[i]
        if c == '%':
            nl = s.find('\n', i, end)
            j = end if nl < 0 else nl + 1
        elif c == '$':
            j = _math_end(s, i, end)
        elif c == '{':
            j = _group_end(s, i, end)
        elif c == '}':
            j = i + 1
        else:
            return self._control(s, i, end)
        self.atom(s[i:j])
        return j

    def _control(self, s, i, end):
        m = CONTROL.match(s, i)
        if not m:
            self.atom(s[i:i + 1])
            return i + 1
        name, star, sym = m.groups()
        j = m.end()
        if name is None:
            if sym == '[':
                k = s.find('\\]', j, end)
                j = end if k < 0 else k + 2
            elif sym == '(':
                k = s.find('\\)', j, end)
                j = end if k < 0 else k + 2
            elif sym == '\\':
                j = _args(s, j + (1 if s.startswith('*', j) else 0), end, brackets_only=True)
            elif sym in ACCENTS and j < end:
                j = _group_end(s, j, end) if s[j] == '{' else j + 1
            self.atom(s[i:j])
            return j
        if name == 'begin':
            return self._environment(s, i, end)
        if name == 'verb' and j < end:
            k = s.find(s[j], j + 1, end)
            j = end if k < 0 else k + 1
            self.atom(s[i:j])
            return j
        if name == 'item':
            j = _args(s, j, end, brackets_only=True)
            self.brk()
            self.atom(s[i:j])
            return j
        if name in PAIRED and j < end and s[j] == '{':
            k = _group_end(s, j, end)
            heading = name in HEADINGS
            n = self._new()
            self.pairs[n] = [s[i:j + 1], s[k - 1:k]]
            if heading:
                self.headings.append(n)
                self.brk()
            self.parts.append(('tok', n))
            self.parse(s, j + 1, k - 1)
            self.parts.append(('tok', '/' + n))
            if heading:
                self.brk()
            return k
        j = _args(s, j, end)
        if name in ('input', 'include', 'subfile'):
            self.inputs.append(s[i:j])
        self.atom(s[i:j])
        return j

    def _environment(self, s, i, end):
        m = BEGIN.match(s, i)
        if not m:
            self.atom(s[i:i + 6])
            return i + 6
        name, j = m.group(1).strip(), m.end()
        k, k2 = _env_end(s, j, end, name)
        if name.rstrip('*') not in PROSE_ENVS:
            self.atom(s[i:k2])
            return k2
        j = _args(s, j, end)
        self.brk()
        self.atom(s[i:j])
        self.brk()
        self.parse(s, j, k)
        self.brk()
        self.atom(s[k:k2])
        self.brk()
        return k2


def extract(tex):
    """Returns (prose view, map). The map holds everything needed to rebuild the .tex file."""
    begin = re.search(r'\\begin\s*\{document\}', tex)
    finish = None
    if begin:
        ends = list(re.finditer(r'\\end\s*\{document\}', tex))
        finish = ends[-1].start() if ends and ends[-1].start() > begin.end() else len(tex)
        head, body, tail = tex[:begin.end()], tex[begin.end():finish], tex[finish:]
    else:
        head, body, tail = '', tex, ''
    ex = _Extractor()
    ex.parse(body, 0, len(body))

    view_parts, segments = [], {}
    pending_raw, pending_view, prev = [], [], 'START'

    def flush(nxt):
        view = re.sub(r'[ \t\r\n\x00]*\x00[ \t\r\n\x00]*', '\n\n', ''.join(pending_view))
        if prev == 'START':
            view = view.lstrip()
        if nxt == 'END':
            view = view.rstrip()
        segments[f'{prev}|{nxt}'] = {'view': view, 'raw': ''.join(pending_raw)}
        view_parts.append(view)
        pending_raw.clear()
        pending_view.clear()

    for part in ex.parts:
        if part[0] == 'raw':
            pending_raw.append(part[1])
            pending_view.append(_to_view(part[1]))
        elif part[0] == 'brk':
            pending_view.append('\x00')
        else:
            flush(part[1])
            view_parts.append(f'{OPEN}{part[1]}{CLOSE}')
            prev = part[1]
    flush('END')

    mapping = {
        'tool': 'academic-humanizer latex_prose.py', 'version': 1,
        'head': head, 'tail': tail,
        'atoms': ex.atoms, 'pairs': ex.pairs, 'headings': ex.headings,
        'segments': segments, 'inputs': ex.inputs,
    }
    return ''.join(view_parts) + '\n', mapping


def _excerpt(latex, limit=60):
    flat = ' '.join(latex.split())
    return flat if len(flat) <= limit else flat[:limit - 3] + '...'


def describe(n, mapping):
    if n in mapping['atoms']:
        return _excerpt(mapping['atoms'][n])
    opening, closing = mapping['pairs'][n]
    return f'{opening}...{closing}'


def legend(mapping):
    lines = ['Placeholders in the prose view and the LaTeX each one holds.',
             'Keep every placeholder exactly once. Reword only the text between a pair.', '']
    for n in sorted(set(mapping['atoms']) | set(mapping['pairs']), key=int):
        tag = f'{OPEN}{n}{CLOSE}...{OPEN}/{n}{CLOSE}' if n in mapping['pairs'] else f'{OPEN}{n}{CLOSE}'
        lines.append(f'{tag:16s} {describe(n, mapping)}')
    return '\n'.join(lines) + '\n'


# ---------- restoration ----------

def _pieces(view):
    """[(kind, value)] where kind is 'text' or 'tok' (value '12' or '/12')."""
    out, pos = [], 0
    for m in TOKEN.finditer(view):
        out.append(('text', view[pos:m.start()]))
        out.append(('tok', m.group(1) + m.group(2)))
        pos = m.end()
    out.append(('text', view[pos:]))
    return out


def validate(view, mapping):
    """Problems that would stop the draft from being turned back into LaTeX."""
    atoms, pairs, headings = mapping['atoms'], mapping['pairs'], set(mapping['headings'])
    expected = Counter(list(atoms) + list(pairs) + ['/' + n for n in pairs])
    found = Counter(v for k, v in _pieces(view) if k == 'tok')
    problems = []
    for tok in sorted(expected - found, key=lambda t: int(t.lstrip('/'))):
        problems.append(f'{OPEN}{tok}{CLOSE} is missing. It holds: {describe(tok.lstrip("/"), mapping)}')
    for tok, count in sorted(found.items(), key=lambda t: int(t[0].lstrip('/'))):
        if tok not in expected:
            problems.append(f'{OPEN}{tok}{CLOSE} is not in the map; delete it')
        elif count > 1:
            problems.append(f'{OPEN}{tok}{CLOSE} appears {count} times; keep it once. It holds: '
                            f'{describe(tok.lstrip("/"), mapping)}')
    if problems:
        return problems
    stack, inner = [], {}
    pieces = _pieces(view)
    for idx, (kind, value) in enumerate(pieces):
        if kind == 'text':
            for m in FORBIDDEN.finditer(value):
                around = value[max(0, m.start() - 40):m.end() + 40]
                problems.append(f'The prose contains {m.group()}: "...{" ".join(around.split())}...". '
                                'Write no LaTeX in the prose; keep the placeholders instead.')
            for n in stack:
                inner[n] = inner.get(n, '') + value
            continue
        if value.startswith('/'):
            n = value[1:]
            if not stack or stack[-1] != n:
                problems.append(f'{OPEN}/{n}{CLOSE} closes before the markers opened after '
                                f'{OPEN}{n}{CLOSE}; pairs must nest')
                if n in stack:
                    stack.remove(n)
            else:
                stack.pop()
        elif value in pairs:
            stack.append(value)
    for n in stack:
        problems.append(f'{OPEN}{n}{CLOSE} is never closed by {OPEN}/{n}{CLOSE}')
    if any('nest' in p or 'never closed' in p for p in problems):
        return problems
    for n, text in inner.items():
        if n in headings and '\n' in text.strip():
            problems.append(f'The heading {OPEN}{n}{CLOSE}...{OPEN}/{n}{CLOSE} spans several lines; keep it on one')
        elif re.search(r'\n[ \t]*\n', text):
            problems.append(f'A blank line falls inside {OPEN}{n}{CLOSE}...{OPEN}/{n}{CLOSE} '
                            f'({describe(n, mapping)}); LaTeX won\'t accept it there')
    return problems


def restore(view, mapping):
    """Rebuilds the .tex file. Raises PlaceholderError when the placeholders don't match the map."""
    view = view.strip()
    problems = validate(view, mapping)
    if problems:
        raise PlaceholderError(problems)
    by_view = {}
    for seg in mapping['segments'].values():
        by_view.setdefault(seg['view'], set()).add(seg['raw'])
    pieces = _pieces(view)
    out = [mapping['head']]
    for idx, (kind, value) in enumerate(pieces):
        if kind == 'tok':
            n = value.lstrip('/')
            if n in mapping['atoms']:
                out.append(mapping['atoms'][n])
            else:
                out.append(mapping['pairs'][n][1 if value.startswith('/') else 0])
            continue
        prev = pieces[idx - 1][1] if idx > 0 else 'START'
        nxt = pieces[idx + 1][1] if idx + 1 < len(pieces) else 'END'
        stored = mapping['segments'].get(f'{prev}|{nxt}')
        if stored and stored['view'] == value:
            out.append(stored['raw'])
        elif len(by_view.get(value, ())) == 1:
            out.append(next(iter(by_view[value])))
        elif stored:
            # Same neighbours, new wording: keep the original spacing at both edges.
            lead = re.match(r'[ \t\r\n]*', stored['raw']).group()
            trail = re.search(r'[ \t\r\n]*$', stored['raw']).group()
            out.append(lead + _to_raw(value.strip()) + trail if value.strip() else stored['raw'])
        else:
            raw = _to_raw(value)
            if prev == 'START' and mapping['head']:
                raw = '\n' + raw
            if nxt == 'END' and mapping['tail']:
                raw += '\n'
            out.append(raw)
    out.append(mapping['tail'])
    return ''.join(out)


def verify(original_map, tex):
    """Re-extracts the rebuilt file and confirms every protected piece of LaTeX survived unchanged."""
    _, new_map = extract(tex)
    problems = []
    for label, key in (('LaTeX pieces', 'atoms'), ('command wrappers', 'pairs')):
        before = Counter(json.dumps(v) for v in original_map[key].values())
        after = Counter(json.dumps(v) for v in new_map[key].values())
        if before != after:
            lost = sum((before - after).values())
            gained = sum((after - before).values())
            problems.append(f'{label} changed after rebuilding: {lost} lost, {gained} new')
    if new_map['head'] != original_map['head'] or new_map['tail'] != original_map['tail']:
        problems.append('the preamble or the end of the document changed')
    return problems


def compile_tex(path):
    """(ok, message). Builds the PDF twice so references resolve; the PDF lands next to the .tex file."""
    engine = shutil.which('pdflatex') or shutil.which('xelatex') or shutil.which('lualatex')
    if not engine:
        return None, 'No LaTeX engine found (pdflatex, xelatex or lualatex). Compile the file yourself.'
    folder, name = os.path.split(os.path.abspath(path))
    with tempfile.TemporaryDirectory() as build:
        for _ in range(2):
            r = subprocess.run([engine, '-interaction=nonstopmode', '-halt-on-error', '-output-directory',
                                build, name], cwd=folder, capture_output=True, text=True, timeout=600)
            if r.returncode != 0:
                errors = [line for line in r.stdout.splitlines() if line.startswith(('!', 'l.'))][:6]
                return False, 'LaTeX failed:\n  ' + '\n  '.join(errors or r.stdout.splitlines()[-10:])
        pdf = os.path.join(build, os.path.splitext(name)[0] + '.pdf')
        target = os.path.splitext(os.path.abspath(path))[0] + '.pdf'
        shutil.copyfile(pdf, target)
    return True, f'Compiled with {os.path.basename(engine)}: {target}'


# ---------- command line ----------

def _read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def _write(path, text):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Academic Humanizer: LaTeX Prose Extractor (v7.14.0)')
    sub = parser.add_subparsers(dest='command', required=True)
    ex = sub.add_parser('extract', help='Write the prose view of a .tex file and its map')
    ex.add_argument('tex')
    ex.add_argument('-o', '--output', required=True, help='Prose view to write (use it as source.txt)')
    ex.add_argument('--map', required=True, help='Map file to write (needed by restore)')
    ex.add_argument('--legend', help='Also write a list of placeholders and the LaTeX each one holds')
    re_ = sub.add_parser('restore', help='Rebuild the .tex file from a rewritten prose view')
    re_.add_argument('draft')
    re_.add_argument('--map', required=True)
    re_.add_argument('-o', '--output', required=True, help='.tex file to write')
    re_.add_argument('--compile', action='store_true', help='Also build the PDF with pdflatex, if installed')
    args = parser.parse_args(argv)

    if args.command == 'extract':
        view, mapping = extract(_read(args.tex))
        _write(args.output, view)
        with open(args.map, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=1)
        if args.legend:
            _write(args.legend, legend(mapping))
        words = len(TOKEN.sub(' ', view).split())
        print(f'Prose view: {args.output} ({words} words of prose)')
        print(f'Placeholders: {len(mapping["atoms"])} kept LaTeX pieces, {len(mapping["pairs"])} reworded '
              f'commands ({len(mapping["headings"])} of them headings)')
        print(f'Map: {args.map}' + (f'   Legend: {args.legend}' if args.legend else ''))
        if mapping['inputs']:
            print('Not followed (extract each of these files separately): ' + ', '.join(mapping['inputs']))
        return 0

    mapping = json.loads(_read(args.map))
    try:
        tex = restore(_read(args.draft), mapping)
    except PlaceholderError as e:
        print('Nothing written. Fix the draft and run restore again:', file=sys.stderr)
        for p in e.problems:
            print(f'  {p}', file=sys.stderr)
        return 2
    _write(args.output, tex)
    print(f'Written: {args.output}')
    problems = verify(mapping, tex)
    if problems:
        print('VERIFY FAILED: ' + '; '.join(problems))
        return 1
    print('Verified: every protected piece of LaTeX is unchanged.')
    if args.compile:
        ok, message = compile_tex(args.output)
        print(message)
        if ok is False:
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
