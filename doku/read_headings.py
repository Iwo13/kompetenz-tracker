import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

doc = Document(r"doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx")
for i, p in enumerate(doc.paragraphs):
    s = p.style.name if p.style else ''
    if s.startswith('Heading') or s.startswith('berschrift') or s.lower().startswith('head'):
        print(f"[{i:4d}] ({s}) {p.text.strip()}")
