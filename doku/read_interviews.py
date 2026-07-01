import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

files = [
    r"doku\HK_Interview_LernendePerson Altin Antworten.docx",
    r"doku\HK_Interview_LernendePerson Lorin Antworten.docx",
    r"doku\Interview_HK_Praxisbildner_Tobias.docx",
]

for f in files:
    print(f"\n{'='*70}")
    print(f"DATEI: {f}")
    print('='*70)
    doc = Document(f)
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if t:
            style = p.style.name if p.style else '?'
            print(f"[{i:3d}] ({style[:18]}) {t}")
