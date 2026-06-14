import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
doc = Document(r'C:\Projekte\IT-Lehre Handlungskompetenzen\doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx')
keywords = ['erweiter', 'lehrber', 'bildungspl', 'skalier', 'andere berufe', 'weitere berufe', 'portier', 'generisch']
for i, p in enumerate(doc.paragraphs):
    txt = p.text.lower()
    if any(k in txt for k in keywords):
        print(f'{i:3d} [{p.style.name}] {p.text[:130]}')
