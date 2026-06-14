"""
Thesis enrichment – Kapitel 2.2 Geplanter KI-Einsatz

Änderungen:
  1. Fliesstext-Intro nach [Vorgabe]: 5 KI-Komponenten, geordnet nach strategischer Bedeutung
  2. Claude Code (bisher KI 3) wird zu KI 1 – als existenzielle Voraussetzung
     → Physische Verschiebung im Dokument: Claude Code Block VOR Azure OpenAI
  3. Umbenennung: KI 1 Azure OpenAI → KI 2, KI 2 Embeddings → KI 3
  4. Neuer KI 4: Basisdaten-Import (Bildungspläne PDF + AP-Kompetenzen XLSX)
  5. Neuer KI 5: Dokumentenbeurteilung – bereits implementiert in AiEvaluationService.cs
     (POST /users/{userId}/documents/{docId}/ai-evaluate, Azure OpenAI GPT-4o)
  6. Bibliografie R50: SBFI Bildungsplan ICT-Berufsbildung
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = r'C:\Projekte\IT-Lehre Handlungskompetenzen\doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'
doc = Document(SRC)

STYLE_ID = {
    'Normal':          'Standard',
    'Heading 2':       'berschrift2',
    'Heading 3':       'berschrift3',
    'List Bullet':     'Aufzhlungszeichen',
    'List Bullet 2':   'Aufzhlungszeichen2',
    'List Paragraph':  'Listenabsatz',
}


def make_xml_para(text, style_name):
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), STYLE_ID.get(style_name, 'Standard'))
    pPr.append(pStyle)
    p.append(pPr)
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = text
    if text and (text[0] == ' ' or text[-1] == ' '):
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    r.append(t)
    p.append(r)
    return p


def insert_paras_after(ref_para, items):
    ref_p = ref_para._p
    for text, style in reversed(items):
        ref_p.addnext(make_xml_para(text, style))


def find_para(doc, text_fragment, style_name=None):
    for p in doc.paragraphs:
        if text_fragment in p.text:
            if style_name is None or p.style.name == style_name:
                return p
    return None


# ─────────────────────────────────────────────────────────
# 1.  Claude Code Block (KI 3) physisch VOR KI 1 Azure OpenAI verschieben
# ─────────────────────────────────────────────────────────
ref_ki1_azure  = find_para(doc, 'KI 1: Azure OpenAI (GPT-4o)')
ref_ki2_embed  = find_para(doc, 'KI 2: Embedding-basierte')
ref_ki3_claude = find_para(doc, 'KI 3: Claude Code (Anthropic) als KI-gestütztes')
ref_litellm    = find_para(doc, 'LiteLLM Gateway als Abstraktionsschicht')

assert ref_ki1_azure,  'Ref not found: KI 1 Azure OpenAI'
assert ref_ki2_embed,  'Ref not found: KI 2 Embeddings'
assert ref_ki3_claude, 'Ref not found: KI 3 Claude Code'
assert ref_litellm,    'Ref not found: LiteLLM Gateway'

# Collect all paragraph XML elements of the Claude Code block
# (from KI 3 inclusive up to but not including LiteLLM)
body = doc.element.body
all_body_children = list(body)

idx_ki3    = all_body_children.index(ref_ki3_claude._p)
idx_litellm_body = all_body_children.index(ref_litellm._p)

claude_block_elems = all_body_children[idx_ki3:idx_litellm_body]

# Remove from current position
for elem in claude_block_elems:
    body.remove(elem)

# Insert before KI 1 Azure OpenAI
ki1_azure_p = ref_ki1_azure._p
for elem in claude_block_elems:
    ki1_azure_p.addprevious(elem)

print(f'Claude Code Block verschoben ({len(claude_block_elems)} Paragraphen) ✓')

# ─────────────────────────────────────────────────────────
# 2.  KI-Nummern umbenennen in den Runs
#     KI 3: Claude Code → KI 1: Claude Code
#     KI 1: Azure OpenAI → KI 2: Azure OpenAI
#     KI 2: Embedding → KI 3: Embedding
# ─────────────────────────────────────────────────────────
# After the move, ref objects are still valid (same _p elements, just different position)
def rename_ki_bullet(para, old_prefix, new_prefix):
    for run in para.runs:
        if old_prefix in run.text:
            run.text = run.text.replace(old_prefix, new_prefix, 1)
            return True
    return False

rename_ki_bullet(ref_ki3_claude, 'KI 3: Claude Code', 'KI 1: Claude Code')
rename_ki_bullet(ref_ki1_azure,  'KI 1: Azure OpenAI', 'KI 2: Azure OpenAI')
rename_ki_bullet(ref_ki2_embed,  'KI 2: Embedding-basierte', 'KI 3: Embedding-basierte')
print('KI-Nummern umbenannt ✓')

# ─────────────────────────────────────────────────────────
# 3.  Fliesstext-Intro nach [Vorgabe]-Placeholder
# ─────────────────────────────────────────────────────────
vorgabe_22 = find_para(doc, 'Welche KI wird für welche Software-Engineering')
assert vorgabe_22, 'Ref not found: [Vorgabe] 2.2'

insert_paras_after(vorgabe_22, [
    ('Der HK-Tracker setzt KI an fünf strategisch unterschiedlichen Stellen ein. '
     'Die Nummerierung folgt der Bedeutungsrangfolge, nicht der chronologischen '
     'Einführungsreihenfolge: KI 1 – Claude Code – nimmt eine Sonderstellung ein, '
     'weil sie nicht als optionale Erweiterung zum Projekt hinzukommt, sondern als '
     'existenzielle Grundvoraussetzung gilt: Ohne KI-gestützte Softwareentwicklung '
     'gäbe es dieses Projekt nicht. KI 2 bis KI 5 sind In-App-Intelligenzfunktionen, '
     'die den Nutzern direkt zugutekommen – von der Kompetenzbeurteilung über die '
     'Datengrundlage bis zur Dokumentenanalyse.',
     'Normal'),
])
print('2.2 Fliesstext-Intro ✓')

# ─────────────────────────────────────────────────────────
# 4.  KI 4: Basisdaten-Import
#     Einfügen NACH den KI 3 Embeddings Sub-Bullets (vor LiteLLM)
# ─────────────────────────────────────────────────────────
# Find last sub-bullet of KI 3 embeddings block = the one before LiteLLM
# We look for the Konsistenz-bullet which is the last Embeddings sub-bullet
ref_ki3_last = find_para(doc, 'Ziel: Konsistenz in Bewertungen')
assert ref_ki3_last, 'Ref not found: KI 3 Konsistenz-Bullet'

insert_paras_after(ref_ki3_last, [
    ('KI 4: Basisdaten-Import – Strukturierte Aufbereitung von Bildungsplänen und '
     'Ausbildungsplatz-Kompetenzen  vgl. [R50] SBFI 2020; [R07] SBFI 2022',
     'List Bullet'),
    ('Input: PDF-Bildungspläne des SBFI (Informatiker/in EFZ, ICT-Fachmann/-frau EFZ) '
     'sowie Excel-Dateien mit Ausbildungsplatz-Kompetenzen (Rotationsplanung, '
     'AP-Kompetenzmatrix)',
     'List Bullet 2'),
    ('Aktueller Stand: Kompetenzziele der Bildungspläne sind als vorstrukturierte '
     'JSON-Dateien im Backend hinterlegt (kompetenzen-informatiker-efz.json, '
     'kompetenzen-ict-fachmann-efz.json) – gepflegt durch den Berufsbildner. '
     'KI-gestützter PDF-Import ist als Erweiterung geplant.',
     'List Bullet 2'),
    ('Geplanter KI-Einsatz: LLM-gestützte Extraktion und Strukturierung von '
     'Handlungskompetenzen, Leistungszielen und Bloom-Niveaus direkt aus den '
     'SBFI-Bildungsplan-PDFs – damit bei Planänderungen kein manueller Pflegeaufwand '
     'durch den Berufsbildner entsteht.',
     'List Bullet 2'),
    ('XLSX-Import: Kompetenzen der Ausbildungsplätze (welche HKs an welchem AP '
     'erlangt werden können) sollen per Excel-Upload importierbar werden – '
     'KI verarbeitet semi-strukturierte Daten und gleicht sie mit den '
     'Bildungsplan-HKs ab.',
     'List Bullet 2'),
])
print('KI 4 Basisdaten-Import ✓')

# ─────────────────────────────────────────────────────────
# 5.  KI 5: Dokumentenbeurteilung
#     Einfügen NACH dem letzten KI 4 Sub-Bullet (XLSX-Import)
# ─────────────────────────────────────────────────────────
ref_ki4_last = find_para(doc, 'KI verarbeitet semi-strukturierte Daten und gleicht')
assert ref_ki4_last, 'Ref not found: KI 4 letzter Sub-Bullet'

insert_paras_after(ref_ki4_last, [
    ('KI 5: Dokumentenbeurteilung – KI-gestützte Analyse von Lernenden-Dokumenten  '
     'vgl. [R10] Abrahamsson et al. 2025; AiEvaluationService.cs',
     'List Bullet'),
    ('Input: Von Lernenden hochgeladene Dokumente (PDF, DOCX, TXT, max. 8 000 Zeichen) '
     '– z. B. Projektberichte, Lerntagebücher, Reflexionstexte',
     'List Bullet 2'),
    ('KI-Prozess: Azure OpenAI GPT-4o analysiert den Dokumenttext anhand der '
     'Leistungsziele aus dem Bildungsplan EFZ (inklusive Bloom-Definitionen K1–K6) '
     'und gibt ein strukturiertes JSON-Ergebnis zurück: Kurzbeschreibung, '
     'Umsetzungsmethode, erkannte Lücken sowie bis zu zehn Kompetenz-Zuordnungen '
     'mit Bloom-Stufe und Konfidenzwert.',
     'List Bullet 2'),
    ('Implementierungsstatus: Vollständig implementiert (AiEvaluationService.cs, '
     'Endpunkt POST /users/{userId}/documents/{docId}/ai-evaluate). '
     'Frontend-Button «✦ AI-Analyse starten» in DokumenteView.tsx. '
     'Derzeit deaktiviert – in Betrieb sobald FHNW Azure-AI-Foundry-Key verfügbar.',
     'List Bullet 2'),
    ('Menschliche Kontrolle (Human-in-the-Loop): KI-Vorschläge werden dem Lernenden '
     'zur Übernahme angeboten; Bloom-Stufe darf den im Bildungsplan definierten '
     'Maximalwert des jeweiligen Lernziels nicht überschreiten. '
     'Endgültige Bewertung erfordert Bestätigung durch Praxisplatzbetreuer.',
     'List Bullet 2'),
])
print('KI 5 Dokumentenbeurteilung ✓')

# ─────────────────────────────────────────────────────────
# 6.  Bibliografie – R50 (SBFI Bildungsplan Informatiker EFZ)
#     Insert AFTER R49
# ─────────────────────────────────────────────────────────
ref_r49 = find_para(doc, '[R49] SDBB', style_name='List Paragraph')
assert ref_r49, 'Ref not found: R49'

insert_paras_after(ref_r49, [
    ('[R50] SBFI. (2020, 19. November). Bildungsplan zur Verordnung über die '
     'berufliche Grundbildung – Informatikerin EFZ / Informatiker EFZ. '
     'Staatssekretariat für Bildung, Forschung und Innovation. '
     'https://www.ict-berufsbildung.ch/ressourcen/bildungsverordnungen/',
     'List Paragraph'),
])
print('Bibliografie R50 ✓')

# ─────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────
doc.save(SRC)
print('Gespeichert:', SRC)
