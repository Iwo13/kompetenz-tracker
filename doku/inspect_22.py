import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
doc = Document(r'C:\Projekte\IT-Lehre Handlungskompetenzen\doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx')
in22 = False
for i, p in enumerate(doc.paragraphs):
    if '2.2' in p.text and 'KI-Einsatz' in p.text:
        in22 = True
    if in22 and '2.3' in p.text and p.style.name.startswith('Heading'):
        break
    if in22:
        print(f'{i:3d} [{p.style.name}] {p.text[:130]}')
