import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
doc = Document(r'C:\Projekte\IT-Lehre Handlungskompetenzen\doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx')
keywords = ['erweiter', 'lehrberuf-agnostisch', 'Kauffrau', 'Langfristige Vision', 'Konfigurationsschritt']
for i, p in enumerate(doc.paragraphs):
    if any(k.lower() in p.text.lower() for k in keywords):
        print(f'{i:3d} [{p.style.name}] {p.text[:140]}')
