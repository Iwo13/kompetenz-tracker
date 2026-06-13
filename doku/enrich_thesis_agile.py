"""
Thesis enrichment – CAS Agile Coaching pass
Adds content from:
  - CAS-PN-AgileCoachingICT-LernendeCIT.pdf  (Kuhn 2024)
  - Chapter_Ausbildungsplätze.docx            (CIT internal)
  - Rotationsplanung.xlsx                     (IST-Zustand evidence)

Sections enriched:
  1.1 Ausgangslage   – IST-Prozess Excel-Rotationsplanung konkretisiert
  1.2 Org.Einbettung – CIT Kreisorganisation / Chapter Ausbildungsplätze
  3.4 Einbezug Stakeholder – Agile-Coaching-PA als Vorphase
  Bibliografie       – R39-R43
  Glossar            – 4 neue Begriffe
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
    """Insert (text, style) items in FORWARD order AFTER ref_para."""
    ref_p = ref_para._p
    for text, style in reversed(items):
        ref_p.addnext(make_xml_para(text, style))


def insert_paras_before(ref_para, items):
    """Insert (text, style) items in FORWARD order BEFORE ref_para."""
    for text, style in items:
        ref_para.insert_paragraph_before(text, style)


def find_para(doc, text_fragment, style_name=None):
    for p in doc.paragraphs:
        if text_fragment in p.text:
            if style_name is None or p.style.name == style_name:
                return p
    return None


# ─────────────────────────────────────────────────────────
# 1.  Section 1.1 – IST-Prozess konkretisieren
#     Insert AFTER "Abgrenzung: HK-Tracker fokussiert..."
# ─────────────────────────────────────────────────────────
ref = find_para(doc, 'Abgrenzung: HK-Tracker fokussiert')
assert ref, 'Ref not found: Abgrenzung bullet'

insert_paras_after(ref, [
    ('IST-Prozess (vor HK-Tracker): Rotationsplanung wurde als Excel-Datei (Rotationsplanung.xlsx) '
     'geführt: Übersichts-Tab mit allen Lernenden (ca. 15 Personen, Jahrgänge BI20–BI23, AE21–AE22, '
     'FI24, PE24/25) und ihren Ausbildungsplätzen pro Semester; je ein Tab pro Ausbildungsplatz '
     '(10 APs: SDM, SDO, SDW, WEB, COL, NetDC, EP, WE, CIS, PnD) mit Praxisbildner, Belegung und '
     'abzudeckenden Handlungskompetenzen. Kompetenzabdeckung wurde manuell markiert (x = abgedeckt, '
     'o = an anderem AP zu erfüllen); keine automatische Lückenerkennung.  vgl. [R43] CIT FHNW 2024',
     'List Bullet'),
])
print('1.1 IST-Prozess ✓')

# ─────────────────────────────────────────────────────────
# 2.  Section 1.2 – CIT Kreisorganisation hinzufügen
#     Insert BEFORE the "[TODO: Organigramm...]" paragraph
# ─────────────────────────────────────────────────────────
ref_todo = find_para(doc, '[TODO: Organigramm FHNW Berufsbildung')
assert ref_todo, 'Ref not found: TODO Organigramm'

insert_paras_before(ref_todo, [
    ('Agile Organisationsstruktur CIT (seit Sommer 2023): Die Corporate IT FHNW stellte ihre '
     'Organisation auf Zellstrukturdesign (vgl. [R39] Pfläging & Hermann 2020) um – dezentrale '
     'Kreise mit Selbstorganisation statt klassischer Hierarchie.',
     'List Bullet'),
    ('Kreis Future – Heimkreis der ICT-Lernenden: Rollen: Taskmaster (Lernende, per Wahl), '
     'Coach (Berufsbildner Iwo Kuhn), Kreismitglieder. Selbstorganisation durch agile Zeremonien '
     '(Sprint-Planung, Reviews, Retrospektiven).  vgl. [R42] Kuhn 2024',
     'List Bullet'),
    ('Chapter «Ausbildungsplätze» – Koordinationsgremium der Praxisbildner: Chapter Lead Iwo Kuhn; '
     'Zweck: Rotationskoordination (Semesterplanung), Kompetenz-Alignment zwischen APs, '
     'gegenseitige Unterstützung.  vgl. [R43] CIT FHNW 2024',
     'List Bullet'),
    ('CIT Ausbildungsplätze (10 APs): SDM (IT-Servicedesk Muttenz), SDO (IT-Servicedesk Olten), '
     'SDW (IT-Servicedesk Windisch), WEB (Webentwicklung), COL (Collaboration), '
     'NetDC (Network & Datacenter), EP (Enterprise Platforms), WE (Workplace Engineering), '
     'CIS (Cloud Infrastructure Services), PnD (Protection and Design).',
     'List Bullet'),
])
print('1.2 CIT Kreisorganisation ✓')

# ─────────────────────────────────────────────────────────
# 3.  Section 3.4 – Agile Coaching PA als Vorphase
#     Insert AFTER "Informelle Gespräche mit Berufsbildner-Kollegen"
# ─────────────────────────────────────────────────────────
ref_conv = find_para(doc, 'Informelle Gespräche mit Berufsbildner-Kollegen')
assert ref_conv, 'Ref not found: Informelle Gespräche'

insert_paras_after(ref_conv, [
    ('Agile Coaching Projektarbeit 2024 (Vorphase): Im Rahmen des CAS Agile Coaching '
     '(vgl. [R42] Kuhn 2024) wurde mit dem Kreis Future eine Stakeholder-Analyse mittels '
     'Auftragskarussell-Methode (vgl. [R40] Andresen 2019) und Riemann-Thomann-Modell '
     '(vgl. [R41] Fleisch 2022) durchgeführt. Ergebnis: Lernende äusserten explizit den Bedarf '
     'nach Transparenz über ihren HK-Fortschritt und über die Tätigkeiten an anderen APs – '
     'ein zentrales Nutzeranliegen, das den HK-Tracker motiviert.',
     'List Bullet 2'),
])
print('3.4 Agile Coaching Vorphase ✓')

# ─────────────────────────────────────────────────────────
# 4.  Bibliografie – R39–R43
#     Insert AFTER R38 (List Paragraph style)
# ─────────────────────────────────────────────────────────
ref_r38 = find_para(doc, '[R38] AWS', style_name='List Paragraph')
assert ref_r38, 'Ref not found: R38 AWS'

insert_paras_after(ref_r38, [
    ('[R39] Pfläging, N. & Hermann, S. (2020). Zellstrukturdesign: Wie Organisationen '
     'Komplexität meistern. Verlag Franz Vahlen.',
     'List Paragraph'),
    ('[R40] Andresen, J. (2019). Agiles Coaching: Die neue Art, Teams zum Erfolg zu führen. '
     'Carl Hanser Verlag.',
     'List Paragraph'),
    ('[R41] Fleisch, N. (2022). Das Quartett der Persönlichkeit nach dem Riemann-Thomann-Modell. '
     'Haupt Verlag.',
     'List Paragraph'),
    ('[R42] Kuhn, I. (2024). Agile Coaching ICT-Lernende CIT. Projektarbeit CAS Agile Coaching, '
     'FHNW Windisch (unveröffentlicht).',
     'List Paragraph'),
    ('[R43] FHNW CIT (2024). Chapter «Ausbildungsplätze»: Konzept und Regelwerk. '
     'Internes Dokument, Corporate IT FHNW.',
     'List Paragraph'),
])
print('Bibliografie R39–R43 ✓')

# ─────────────────────────────────────────────────────────
# 5.  Glossar – 4 neue Begriffe
#     Insert BEFORE the first Glossar entry (ADR)
# ─────────────────────────────────────────────────────────
ref_adr = find_para(doc, 'ADR: Architecture Decision Record', style_name='List Paragraph')
assert ref_adr, 'Ref not found: ADR Glossar entry'

insert_paras_before(ref_adr, [
    ('Chapter «Ausbildungsplätze»: Koordinationsgremium der Praxisbildner in der CIT; '
     'verantwortlich für Rotationsplanung, HK-Abdeckungskoordination und gegenseitige '
     'Unterstützung; Chapter Lead: Iwo Kuhn.  vgl. [R43]',
     'List Paragraph'),
    ('Kreis Future: ICT-Lernenden-Heimkreis in der CIT-Kreisorganisation; Selbstorganisation '
     'durch Taskmaster und Coach; agile Zeremonien (Sprint-Planung, Reviews, Retrospektiven). '
     'vgl. [R42]',
     'List Paragraph'),
    ('Praxisbildner/in: Person, die Lernende an einem Ausbildungsplatz fachlich betreut '
     '(≠ Berufsbildner/in, der/die die Gesamtausbildung koordiniert und für das Lehrverhältnis '
     'verantwortlich ist).',
     'List Paragraph'),
    ('Zellstrukturdesign: Organisationsmodell für Unternehmen in komplexen Umfeldern '
     '(Pfläging & Hermann 2020) – dezentrale Kreise mit Selbstorganisation ersetzen klassische '
     'Hierarchie; CIT FHNW seit Sommer 2023.  vgl. [R39]',
     'List Paragraph'),
])
print('Glossar 4 neue Begriffe ✓')

# ─────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────
doc.save(SRC)
print('Gespeichert:', SRC)
