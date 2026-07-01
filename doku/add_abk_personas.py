import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DOC = r"doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx"
doc = Document(DOC)
paras = doc.paragraphs

def already(text):
    return any(text in p.text for p in paras)

def make_abk_para(abbr, expansion):
    """Erstellt einen List-Paragraph im gleichen Format wie die bestehenden Einträge."""
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), 'ListParagraph')
    pPr.append(pStyle)
    p.append(pPr)
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = f"{abbr}:\t{expansion}"
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r.append(t)
    p.append(r)
    return p

def find_para(needle):
    for p in paras:
        if needle in p.text:
            return p
    return None

new_entries = [
    # (Kürzel, Expansion, Referenztext nach dem eingefügt wird)
    ("BB",  "Berufsbildner (Rollenkürzel im Anforderungskatalog; Persona KUI)",  "API:\t"),   # nach API, vor CAS
    ("L",   "Lernende/r (Rollenkürzel im Anforderungskatalog; Persona Heinz/Viktor)", "KI / AI:\t"),  # nach KI/AI, vor LLM
    ("PPB", "Praxisplatzbetreuer / Praxisbildner (Rollenkürzel im Anforderungskatalog; Persona Michi)", "PWA:\t"),  # nach PWA, vor RAM
]

for abbr, expansion, after_text in new_entries:
    guard = f"{abbr}:\t"
    if already(guard):
        print(f"  [SKIP] {abbr} bereits vorhanden")
        continue
    ref = find_para(after_text)
    if not ref:
        print(f"  [FEHLER] Referenz '{after_text}' nicht gefunden für {abbr}")
        continue
    new_p = make_abk_para(abbr, expansion)
    ref._p.addnext(new_p)
    print(f"  [OK] {abbr} nach '{after_text.strip()}' eingefügt")

doc.save(DOC)
print(f"\nGespeichert: {DOC}")
