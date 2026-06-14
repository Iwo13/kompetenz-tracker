import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
doc = Document(r'C:\Projekte\IT-Lehre Handlungskompetenzen\doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx')
for i, p in enumerate(doc.paragraphs):
    if 'XLSX' in p.text or 'xlsx' in p.text.lower():
        print(f'{i:3d} [{p.style.name}] {repr(p.text[:100])}')
