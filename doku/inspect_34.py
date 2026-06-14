import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
doc = Document(r'C:\Projekte\IT-Lehre Handlungskompetenzen\doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx')
in34 = False
for i, p in enumerate(doc.paragraphs):
    if '3.4' in p.text and p.style.name.startswith('Heading'):
        in34 = True
    if in34 and p.style.name.startswith('Heading') and '3.4' not in p.text:
        break
    if in34:
        print(f'{i:3d} [{p.style.name}] {p.text[:140]}')
