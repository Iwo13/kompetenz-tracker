import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

doc = Document(r"doku\HK_Interview_Berufsbildner_Iwo.docx")
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if t:
        style = p.style.name if p.style else '?'
        print(f"[{i:3d}] ({style[:18]}) {t}")
