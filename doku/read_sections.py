import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document

doc = Document(r"doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx")
paras = doc.paragraphs

def show(label, start, end):
    print(f"\n{'='*70}")
    print(f"  {label}  (idx {start}–{end})")
    print('='*70)
    for i in range(start, min(end, len(paras))):
        t = paras[i].text.strip()
        s = paras[i].style.name if paras[i].style else ''
        if t:
            print(f"[{i:4d}] ({s[:20]}) {t[:120]}")

# 2.4.1 Anforderungskatalog Anfang
show("2.4.1 Anforderungskatalog (Kontext vor Tabelle)", 260, 270)

# 3.4 Einbezug Stakeholder
show("3.4 Einbezug Stakeholder", 457, 490)

# 4.4 Empfohlene nächste Schritte
show("4.4 Empfohlene nächste Schritte", 630, 660)
