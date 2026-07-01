import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

doc = Document(r"doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx")
paras = doc.paragraphs

# Abkürzungsverzeichnis: ab Heading-Index bis zum nächsten Heading 1
start = None
for i, p in enumerate(paras):
    if 'Abkürzungsverzeichnis' in p.text and p.style.name.startswith('Heading'):
        start = i
        break

if start is None:
    print("Nicht gefunden")
else:
    for i in range(start, min(start + 80, len(paras))):
        p = paras[i]
        t = p.text.strip()
        s = p.style.name if p.style else ''
        if i > start and (s.startswith('Heading 1') or s.startswith('berschrift1')):
            break
        if t:
            print(f"[{i:4d}] ({s[:22]}) {t[:130]}")
