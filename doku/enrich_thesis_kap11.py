"""
Thesis enrichment – Kapitel 1.1 Ausgangslage Fliesstext
Fügt drei Fliesstext-Absätze nach dem [Vorgabe]-Placeholder ein:
  1. Praxisbildner: IT-Spezialisten, begrenzte pädagogische Ressourcen
  2. Lernende: Fokus auf IT statt Kompetenz-Dokumentation
  3. Transparenzlücken: Kompetenzen je AP, Rotation, Wissenstransfer beim AP-Wechsel
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
# 1.1 Ausgangslage – Fliesstext nach dem [Vorgabe]-Placeholder
# ─────────────────────────────────────────────────────────
vorgabe_11 = find_para(
    doc,
    '[Vorgabe] Problembeschreibung: Warum besteht das Problem?'
)
assert vorgabe_11, 'Ref not found: [Vorgabe] 1.1'

fliesstext = [
    # Absatz 1: Praxisbildner
    ('Die Praxisbildner an den CIT-Ausbildungsplätzen sind in erster Linie Fachspezialisten '
     'in ihren jeweiligen IT-Bereichen – sei es Netzwerk, Cloud-Infrastruktur, '
     'Webentwicklung oder Collaboration – und betreuen Lernende neben ihrer regulären '
     'Arbeit. Für eine fundierte Kompetenzbeurteilung nach Bloom-Taxonomie fehlt ihnen '
     'häufig sowohl die pädagogische Ausbildung als auch die zeitlichen Ressourcen. '
     'Die Beurteilung von Handlungskompetenzen ist damit eine Aufgabe, die zwar '
     'verpflichtend ist, im Arbeitsalltag aber regelmässig gegenüber dem operativen '
     'IT-Betrieb zurücktritt.',
     'Normal'),
    # Absatz 2: Lernende
    ('Auch auf Seiten der Lernenden besteht eine strukturelle Herausforderung: Lernende '
     'bevorzugen verständlicherweise die praktische IT-Arbeit gegenüber der administrativen '
     'Dokumentation ihres Kompetenzfortschritts. Dabei sind sie gemäss den Vorgaben des '
     'Bildungsplans verpflichtet, ihre Handlungskompetenzen eigenständig nachzuweisen und '
     'kontinuierlich zu dokumentieren. In der Praxis geschieht dies oft erst unmittelbar '
     'vor Beurteilungsterminen und bleibt damit punktuell statt prozessbegleitend.',
     'Normal'),
    # Absatz 3: Transparenzlücken
    ('Erschwerend wirken strukturelle Transparenzlücken auf mehreren Ebenen: Welche '
     'Handlungskompetenzen an welchem Ausbildungsplatz erworben werden können, ist zwar '
     'in einer Excel-Datei erfasst, wird im Alltag jedoch kaum konsultiert. Die Rotation '
     'der Lernenden zwischen den zehn CIT-Ausbildungsplätzen wird ebenfalls über eine '
     'Excel-Tabelle koordiniert – mit entsprechend eingeschränkter Übersicht über '
     'Abdeckungslücken oder Planungskonflikte. Wenn Lernende den Ausbildungsplatz wechseln, '
     'steht dem aufnehmenden Praxisbildner keine strukturierte Übersicht zur Verfügung, '
     'welche Kompetenzen bereits nachgewiesen wurden und welche Arbeiten dazu beigetragen '
     'haben. Diese Information wäre jedoch entscheidend, um die Einarbeitung gezielt auf '
     'bestehende Lücken auszurichten und eine nahtlose Weiterführung der '
     'Kompetenzentwicklung zu gewährleisten.',
     'Normal'),
]

insert_paras_after(vorgabe_11, fliesstext)
print('1.1 Fliesstext ✓')

# ─────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────
doc.save(SRC)
print('Gespeichert:', SRC)
