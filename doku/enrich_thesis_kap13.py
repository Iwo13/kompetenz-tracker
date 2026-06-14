"""
Thesis enrichment – Kapitel 1.3 KI-bezogene Unternehmens- und Projektziele
Ergänzt basierend auf:
  - AI-Reiseplan-CIT 28.04.2026.jpg  (Workshop-Folie, 6 strategische Treiber)
  - CIT-Organigramm (Chapter AI: Nicola Elsener, Oliver Grässle)
  - CAS AI-SE FHNW (12 ECTS, 14 Kurstage, ca. 6 CIT-Mitarbeitende)

Fügt 3 Fliesstext-Absätze nach [Vorgabe]-Placeholder ein:
  1. Strategischer KI-Kontext CIT – 6 Leitthesen AI-Reiseplan + Chapter AI
  2. CAS AI-SE als Upskilling-Massnahme – 6 CIT-Mitarbeitende, diese Thesis als Produkt
  3. Überleitung zu den KI-Projektzielen
Ergänzt R46 (FHNW CAS AI-SE) und R47 (AI-Reiseplan CIT) in der Bibliografie.
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


def find_para(doc, text_fragment, style_name=None):
    for p in doc.paragraphs:
        if text_fragment in p.text:
            if style_name is None or p.style.name == style_name:
                return p
    return None


# ─────────────────────────────────────────────────────────
# 1.3 – Fliesstext nach [Vorgabe]-Placeholder
# ─────────────────────────────────────────────────────────
vorgabe_13 = find_para(
    doc,
    '[Vorgabe] Unternehmens- und Projektziele mit KI-Fokus'
)
assert vorgabe_13, 'Ref not found: [Vorgabe] 1.3'

fliesstext_13 = [
    # Absatz 1: Strategischer KI-Kontext CIT
    ('Künstliche Intelligenz ist für die Corporate IT FHNW kein peripheres Trendthema, '
     'sondern ein strategischer Transformationstreiber. In einem internen Workshop im '
     'April 2026 erarbeitete die CIT sechs Leitthesen, warum sie sich mit und durch KI '
     'entwickeln muss (vgl. AI-Reiseplan CIT, Abbildung A.2 im Anhang; [R47]): '
     'Wissensarbeit verändert sich fundamental – KI verändert nicht einzelne Tools, '
     'sondern die Art, wie Analyse, Entscheidung und Problemlösung funktionieren. '
     'Die FHNW erwartet als Bildungs- und Forschungsinstitution eine zukunftsfähige IT. '
     'Ohne bewusste Gestaltung entsteht Wildwuchs – AI-Tools werden bereits genutzt, '
     'mit oder ohne Rahmen. Rollen und Verantwortlichkeiten verschieben sich, und die '
     'CIT muss klären, welche Kompetenzen künftig gefragt sind. Zusammenarbeit und '
     'Lernkultur sind entscheidend: Experimentieren und gemeinsames Lernen müssen '
     'möglich sein. Und schliesslich: Die Transformation geschieht sowieso – Passivität '
     'ist keine neutrale Option. Organisatorisch ist KI in der CIT durch das Chapter AI '
     '(Chapter Leads: Nicola Elsener, Oliver Grässle) verankert '
     '(vgl. CIT-Organigramm, Abbildung A.1).',
     'Normal'),
    # Absatz 2: CAS AI-SE als Upskilling
    ('Als konkrete Upskilling-Massnahme besuchen rund sechs Mitarbeitende der CIT das '
     'Certificate of Advanced Studies «Künstliche Intelligenz für Softwareentwicklung» '
     '(CAS AI-SE) an der FHNW Hochschule für Informatik – 12 ECTS, 14 Kurstage, '
     'mit Fokus auf KI-Einsatz in Requirements Engineering, Architektur, Entwicklung, '
     'Testing und Betrieb (vgl. [R46] FHNW 2026). Die vorliegende Abschlussarbeit ist '
     'ein direktes Ergebnis dieses CAS: Der HK-Tracker wird nicht nur als Praxisprojekt '
     'entwickelt, sondern dient gleichzeitig als konkretes Lernfeld für den produktiven '
     'KI-Einsatz in der eigenen Organisation – und damit als Beitrag zur '
     'KI-Transformation der CIT.',
     'Normal'),
    # Absatz 3: Überleitung
    ('Aus diesem strategischen Rahmen leiten sich die KI-bezogenen Projektziele '
     'des HK-Trackers direkt ab:',
     'Normal'),
]

insert_paras_after(vorgabe_13, fliesstext_13)
print('1.3 Fliesstext ✓')

# ─────────────────────────────────────────────────────────
# Bibliografie – R46 + R47
#     Insert AFTER R45
# ─────────────────────────────────────────────────────────
ref_r45 = find_para(doc, '[R45] FHNW', style_name='List Paragraph')
assert ref_r45, 'Ref not found: R45'

insert_paras_after(ref_r45, [
    ('[R46] FHNW. (2026). CAS Künstliche Intelligenz für Softwareentwicklung (AI-SE). '
     'Hochschule für Informatik, Fachhochschule Nordwestschweiz. '
     'https://www.fhnw.ch/de/informatik/weiterbildung/angebot/weiterbildungen/'
     'cas-artificial-intelligence-software-engineering',
     'List Paragraph'),
    ('[R47] CIT FHNW. (2026, 28. April). AI-Reiseplan CIT – Workshop-Folie: '
     'Warum muss sich die CIT mit und durch KI entwickeln? '
     'Internes Dokument, Corporate IT FHNW.',
     'List Paragraph'),
])
print('Bibliografie R46-R47 ✓')

# ─────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────
doc.save(SRC)
print('Gespeichert:', SRC)
