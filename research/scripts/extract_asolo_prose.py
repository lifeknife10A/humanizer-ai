import re

with open('/Users/krish/Desktop/Human Computer Interaction/Lab/HCI_Conference_Paper.tex', 'r') as f:
    tex = f.read()

start = tex.find('\\begin{abstract}')
end = tex.find('\\begin{thebibliography}')
if end == -1: end = len(tex)
body = tex[start:end]

# Clean up common latex commands
body = re.sub(r'\\(textbf|textit|emph|texttt)\{([^}]+)\}', r'\2', body)
body = re.sub(r'\\(section|subsection|subsubsection)\*?\{([^}]+)\}', r'\n\n\2\n\n', body)
body = re.sub(r'\\cite\{[^}]+\}', '', body)
body = re.sub(r'%.*', '', body)
body = re.sub(r'\$([^$]+)\$', r'\1', body)
body = body.replace(r'\,', ' ').replace('~', ' ').replace(r'\pm', '±')
body = re.sub(r'\\(begin|end)\{[^}]+\}', '', body)
body = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{[^}]*\})?', ' ', body)
# Normalize whitespace
paragraphs = [re.sub(r'\s+', ' ', p).strip() for p in body.split('\n\n') if p.strip()]
clean_text = '\n\n'.join(p for p in paragraphs if len(p.split()) > 5)

outpath = '/Users/krish/Github/humanizer-ai/research/data/asolo_baseline_prose.txt'
with open(outpath, 'w') as f:
    f.write(clean_text)

print(f'Wrote {len(clean_text.split())} words to {outpath}')
print('Sample first 400 chars:\n', clean_text[:400])
