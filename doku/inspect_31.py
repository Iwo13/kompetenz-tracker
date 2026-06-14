import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
doc = Document(r'C:\Projekte\IT-Lehre Handlungskompetenzen\doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx')
in31 = False
for i, p in enumerate(doc.paragraphs):
    if '3.1' in p.text and p.style.name.startswith('Heading'):
        in31 = True
    if in31 and ('3.2' in p.text or '4.' in p.text[:3]) and p.style.name.startswith('Heading'):
        break
    if in31:
        print(f'{i:3d} [{p.style.name}] {p.text[:140]}')
