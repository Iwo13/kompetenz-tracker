"""
Thesis enrichment - Kapitel 3.1 Tooling und Infrastruktur

Ergaenzungen:
  1. Fliesstext-Intro nach [Vorgabe]: Entwicklungs-Workflow (PowerPoint -> Claude Code -> App)
  2. Claude Code Sub-Bullets: Modell (Sonnet), Abo (~CHF 20), Arbeitgeber-Spesen max. CHF 19.99
  3. PowerPoint als visuelle Spezifikation: 21 Slides als AI-Guideline uebergeben
  4. Verbale Requirements als zweite Spezifikations-Modalitaet (Lernende-AP-Zuweisung)
  5. Enterprise Architekt Entscheid: Azure + MS SQL Server vorgeschrieben
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


def insert_after(ref_para, items):
    """Insert items AFTER ref in forward order (addnext + reversed)."""
    ref_p = ref_para._p
    for text, style in reversed(items):
        ref_p.addnext(make_xml_para(text, style))


def insert_before(ref_para, items):
    """Insert items BEFORE ref in forward order (addprevious + forward)."""
    ref_p = ref_para._p
    for text, style in items:
        ref_p.addprevious(make_xml_para(text, style))


def find_para(doc, text_fragment, style_name=None):
    for p in doc.paragraphs:
        if text_fragment in p.text:
            if style_name is None or p.style.name == style_name:
                return p
    return None


# ---- Referenz-Paragraphen ----
ref_vorgabe_31  = find_para(doc, '[Vorgabe] Tooling-Entscheide: Welche Werkzeuge')
ref_frontend    = find_para(doc, 'Frontend: React 18')
ref_backend     = find_para(doc, 'Backend: ASP.NET Core 8')
ref_db          = find_para(doc, 'Datenbank: SQL Server')
ref_claude_code = find_para(doc, 'Entwicklungswerkzeug: Claude Code (Anthropic)')
ref_claude_mem  = find_para(doc, 'CLAUDE.md + Memory-System')

assert ref_vorgabe_31,  'Ref not found: [Vorgabe] 3.1'
assert ref_frontend,    'Ref not found: Frontend React'
assert ref_backend,     'Ref not found: Backend ASP.NET'
assert ref_db,          'Ref not found: Datenbank SQL Server'
assert ref_claude_code, 'Ref not found: Claude Code Bullet'
assert ref_claude_mem,  'Ref not found: CLAUDE.md Memory'


# ========================================================
# 1. Fliesstext-Intro nach [Vorgabe]
# ========================================================
insert_after(ref_vorgabe_31, [
    ('Die Tooling-Entscheide in diesem Projekt sind eng mit dem besonderen '
     'Entwicklungskontext verknuepft: Der Projektverantwortliche verfolgt keinen '
     'klassischen Softwareentwicklungs-Workflow, sondern einen KI-gestuetzten '
     'Spezifikations- und Generierungsansatz. Die Entwicklungsarbeit verlief in '
     'zwei Spezifikations-Modalitaeten: einerseits visuelle Mockups in PowerPoint '
     '(21 Slides, abgedeckt in Anhang A.4), die als detaillierte UI-Guidelines an '
     'Claude Code uebergeben wurden; andererseits verbale Anforderungsbeschreibungen '
     'fuer Features, bei denen die KI das Interface-Design selbst vorschlug und '
     'umsetzte. Der Techstack selbst wurde nicht frei gewaehlt, sondern in '
     'Abstimmung mit dem Enterprise Architekten der FHNW vorgegeben.',
     'Normal'),
])
print('3.1 Fliesstext-Intro OK')


# ========================================================
# 2. Claude Code Bullet enrichieren
#    Sub-Bullets einfuegen NACH "CLAUDE.md + Memory-System..."
# ========================================================
insert_after(ref_claude_mem, [
    ('Modell: claude-sonnet-4-6 (Claude Sonnet, Anthropic, Stand Juni 2026) '
     '- eingesetzt ueber Claude.ai Pro-Abonnement sowie Claude Code CLI '
     'als VSCode-Extension.',
     'List Bullet 2'),
    ('Kosten und Finanzierung: Das Claude Pro-Abonnement kostet ca. CHF 20 pro '
     'Monat. Der Arbeitgeber FHNW erstattet KI-Tool-Abonnements bis max. CHF 19.99 '
     'pro Monat als Spesen - das Abonnement wird damit vollstaendig durch die '
     'Organisation getragen.',
     'List Bullet 2'),
    ('PowerPoint als visuelle Spezifikation: Vor dem Codieren wurden UI-Konzepte '
     'und Interaktionsablaeufe in Microsoft PowerPoint als Pixel-genaue Wireframes '
     'ausgearbeitet (vgl. Anhang A.4: Konzept_Kompetenzen_Ausbildungsplaetze.pptx, '
     '21 Slides). Diese Mockups wurden Claude Code als visuelle Guidelines '
     'uebergeben - die KI uebersetzte die Layouts direkt in React/TypeScript-Code. '
     'Die Uebereinstimmung zwischen Mockup und Implementierung war hoch; '
     'Abweichungen wurden iterativ per Chat-Anweisung korrigiert.',
     'List Bullet 2'),
    ('Verbale Spezifikation als Alternative: Features ohne Mockup wurden durch '
     'praezise verbale Anforderungsbeschreibungen spezifiziert. Beispiel: die '
     'Funktion zur Zuweisung von Lernenden an Ausbildungsplaetze wurde ausschliesslich '
     'per Textbeschreibung vorgegeben - Claude Code schlug Interface-Design und '
     'Datenmodell selbst vor und setzte beides direkt um.',
     'List Bullet 2'),
])
print('Claude Code Sub-Bullets OK')


# ========================================================
# 3. Enterprise Architekt Entscheid - Backend-Abschnitt ergaenzen
#    Einfuegen NACH "Begruendung: FHNW .NET-Stack..."
# ========================================================
ref_backend_begruendung = find_para(doc, 'FHNW .NET-Stack, Azure-Integration nativ')
assert ref_backend_begruendung, 'Ref not found: Backend Begruendung'

insert_after(ref_backend_begruendung, [
    ('Architekturentscheid durch Enterprise Architekten: Der Techstack wurde nicht '
     'frei gewaehlt, sondern in Abstimmung mit dem FHNW Enterprise Architekten '
     'festgelegt. Dessen Entscheid: Azure als Hosting-Plattform, '
     'Microsoft SQL Server (Azure SQL Database) als Datenbankschicht. '
     'Begruendung: Alignment mit bestehender FHNW-Infrastruktur, '
     'etablierte Governance-Prozesse, direkter Betriebssupport durch die CIT.',
     'List Bullet 2'),
])
print('Enterprise Architekt Entscheid OK')


# ========================================================
# Save
# ========================================================
doc.save(SRC)
print('Gespeichert:', SRC)
