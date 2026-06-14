import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
doc = Document(r'C:\Projekte\IT-Lehre Handlungskompetenzen\doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx')
in23 = False
for i, p in enumerate(doc.paragraphs):
    if '2.3' in p.text and p.style.name.startswith('Heading'):
        in23 = True
    if in23 and ('2.4' in p.text or '3.' in p.text[:4]) and p.style.name.startswith('Heading'):
        break
    if in23:
        print(f'{i:3d} [{p.style.name}] {p.text[:140]}')
