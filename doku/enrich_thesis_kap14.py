"""
Thesis enrichment – Kapitel 1.4 Stakeholder- und Kontextanalyse
Ergänzt basierend auf:
  - Personas.md (4 Cooper-Personas: Heinz, Viktor, Michi, KUI)
  - HK-Tracker-Personas.png (Anhang A.3)
  - Personalisierung.pdf (Seyff, Tag 11): Persona-Methodik, Persona Engine, Patkar & Seyff 2023
  - CAS Agile Coaching PA [R42] – Iwo Kuhn als erfahrener Berufsbildner + Chapter Lead AUP

Fügt ein:
  1. Fliesstext-Intro für 1.4 (nach [Vorgabe]-Placeholder)
  2. Erfahrungs-Ergänzung bei Stakeholder 2 – Berufsbildner (Iwo als Double-Role)
  3. Persona-Bild-Referenz + Persona-Engine-Hinweis in 1.4.1
  4. R48: Seyff Tag 11 Folien
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
    'Heading 1':       'berschrift1',
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


def insert_paras_before(ref_para, items):
    for text, style in items:
        ref_para.insert_paragraph_before(text, style)


def find_para(doc, text_fragment, style_name=None):
    for p in doc.paragraphs:
        if text_fragment in p.text:
            if style_name is None or p.style.name == style_name:
                return p
    return None


# ─────────────────────────────────────────────────────────
# 1.  1.4 – Fliesstext-Intro nach [Vorgabe]-Placeholder
# ─────────────────────────────────────────────────────────
vorgabe_14 = find_para(doc, '[Vorgabe] Stakeholder- und Kontextanalyse: Wer ist betroffen?')
assert vorgabe_14, 'Ref not found: [Vorgabe] 1.4'

fliesstext_14 = [
    ('Die Stakeholder-Analyse strukturiert die Interessengruppen des HK-Trackers nach dem '
     'Requirements Abstraction Model (RAM) von Gorschek & Wohlin (2006), das von '
     'Business Goals über System Goals bis zu technischen Constraints schichtet '
     '(vgl. [R05]). Vier Stakeholder-Gruppen wurden identifiziert: '
     'Lernende als direkte Endnutzer der Kompetenzerfassungs-Funktion; '
     'Berufsbildner als Primärnutzer mit Bewertungs- und Planungsverantwortung; '
     'Praxisbildner als dezentrale Betreuer an den einzelnen Ausbildungsplätzen; '
     'sowie die FHNW IT-Abteilung als Deployment- und Infrastruktur-Stakeholder. '
     'Die Nutzerprofile der drei operativen Gruppen werden in Abschnitt 1.4.1 '
     'als Cooper-Personas (zielorientiert) vertieft.',
     'Normal'),
]
insert_paras_after(vorgabe_14, fliesstext_14)
print('1.4 Fliesstext-Intro ✓')

# ─────────────────────────────────────────────────────────
# 2.  Stakeholder 2 – Berufsbildner: Erfahrungs-Ergänzung
#     Fügt Sub-Bullet nach "Risiko: Decision Fatigue..." ein
# ─────────────────────────────────────────────────────────
ref_fatigue = find_para(doc, 'Risiko: Decision Fatigue durch zu viele KI-Vorschläge')
assert ref_fatigue, 'Ref not found: Decision Fatigue bullet'

insert_paras_after(ref_fatigue, [
    ('Besonderheit: Der Berufsbildner (Iwo Kuhn) ist gleichzeitig Entwickler des '
     'HK-Trackers. Diese Double-Role ermöglicht direkte Requirements-Validierung '
     'aus der Nutzerperspektive. Er bringt langjährige Erfahrung als Berufsbildner, '
     'Chapter Lead CP-AUP und Coach des Kreis Future mit – dokumentiert in der '
     'CAS Agile Coaching Projektarbeit 2024 (vgl. [R42] Kuhn 2024).',
     'List Bullet 2'),
])
print('1.4 Berufsbildner Double-Role ✓')

# ─────────────────────────────────────────────────────────
# 3.  1.4.1 – Persona-Bild-Referenz + Persona-Engine-Hinweis
#     Einfügen NACH dem abschliessenden Satz "Die Personas wurden..."
# ─────────────────────────────────────────────────────────
ref_personas_note = find_para(doc, 'Die Personas wurden im Rahmen von Modultag 11 (Seyff')
assert ref_personas_note, 'Ref not found: Personas Modultag 11 note'

insert_paras_after(ref_personas_note, [
    ('Die vier Personas sind als visuelle Übersicht in Abbildung A.3 (Anhang) '
     'dokumentiert. Methodisch entsprechen sie aktuell dem Typ «Manual Persona '
     'Development» (MPD) – erstellt aus direkter Beobachtung und Erfahrung, '
     'nicht aus aggregierten Laufzeitdaten. Gemäss dem «Persona Engine»-Konzept '
     '(vgl. [R24] Patkar & Seyff, REFSQ 2023; [R48] Seyff, Tag 11 2026) sollen '
     'die Personas im Pilotbetrieb (Phase 3) durch strukturierte Feedback- und '
     'Monitoring-Daten validiert und schrittweise zu datengetriebenen Profilen '
     'weiterentwickelt werden – «created, validated, evolved» statt '
     '«created, never validated, never evolved».',
     'Normal'),
])
print('1.4.1 Persona Engine Hinweis ✓')

# ─────────────────────────────────────────────────────────
# 4.  Bibliografie – R48
#     Insert AFTER R47
# ─────────────────────────────────────────────────────────
ref_r47 = find_para(doc, '[R47] CIT FHNW', style_name='List Paragraph')
assert ref_r47, 'Ref not found: R47'

insert_paras_after(ref_r47, [
    ('[R48] Seyff, N. (2026, 12. Juni). Von klassischen Personas zu lebenden '
     'Nutzermodellen – Nutzerverständnis im Wandel der Software-Evolution. '
     'Vorlesungsfolien CAS AI-SE, Modultag 11. '
     'FHNW Hochschule für Informatik.',
     'List Paragraph'),
])
print('Bibliografie R48 ✓')

# ─────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────
doc.save(SRC)
print('Gespeichert:', SRC)
