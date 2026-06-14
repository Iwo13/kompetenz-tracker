"""
Thesis enrichment – Kapitel 1 Einleitung Fliesstext
Ersetzt den [Vorgabe]-Placeholder in Kapitel 1 durch echten Einleitungstext.
Ergänzt:
  - Fliesstext-Absätze als Kapitel-Intro (vor 1.1)
  - R44: SBFI/ICT-Berufsbildung Bildungsplan Informatiker EFZ
  - R45: FHNW Berufsbildung (URL)
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
# 1.  Kapitel 1 Einleitung – Fliesstext
#     Ersetze [Vorgabe]-Paragraph durch echten Einleitungstext
# ─────────────────────────────────────────────────────────
vorgabe_kap1 = find_para(
    doc,
    '[Vorgabe] Pflichtkapitel gemäss Vorgabe. Enthält: Problembeschreibung'
)
assert vorgabe_kap1, 'Ref not found: [Vorgabe] Kapitel 1'

# Fliesstext-Absätze (werden nach dem [Vorgabe]-Para eingefügt)
intro_absaetze = [
    ('Die Schweizer Berufsbildung im ICT-Bereich verpflichtet Ausbildungsbetriebe, Lernende '
     'zu einem breiten Spektrum von Handlungskompetenzen (HK) zu befähigen. Die dafür '
     'massgeblichen Kompetenzziele sind in den Bildungsplänen des Staatssekretariats für '
     'Bildung, Forschung und Innovation (SBFI) verbindlich festgelegt und strukturieren die '
     'betriebliche Grundbildung in den Berufen Informatiker/in EFZ und ICT-Fachmann/-frau EFZ. '
     'vgl. [R44] ICT-Berufsbildung / SBFI 2021',
     'Normal'),
    ('Die Fachhochschule Nordwestschweiz (FHNW) bildet als Ausbildungsbetrieb an mehreren '
     'Standorten ICT-Lernende aus – darunter in der Corporate IT (CIT) in Windisch, Olten und '
     'Muttenz. vgl. [R45] FHNW Berufsbildung  Berufsbildner und Praxisbildner begleiten die '
     'Lernenden dabei fachlich, koordinieren deren Rotation durch verschiedene Ausbildungsplätze '
     'und beurteilen die erbrachten Kompetenznachweise anhand der Bloom-Taxonomie. Die '
     'Dokumentation dieser Kompetenzen erfolgte bislang vollständig manuell – in '
     'Excel-Tabellen und Word-Dokumenten – ohne standardisierte digitale Unterstützung und '
     'ohne automatisierte Erkennung von Abdeckungslücken im Bildungsplan.',
     'Normal'),
    ('Die vorliegende Abschlussarbeit beschreibt Konzeption, Entwicklung und Pilotbetrieb des '
     'HK-Trackers: einer webbasierten Applikation, die Kompetenzerfassung, '
     'Bloom-taxonomie-basierte Bewertung, Ausbildungsplatz-Rotation und HK-Abdeckungsanalyse '
     'digital unterstützt und durch den Einsatz von KI (Azure OpenAI GPT-4o) schrittweise '
     'automatisiert. Claude Code – das KI-gestützte Entwicklungswerkzeug von Anthropic – '
     'kommt dabei als zentrales Hilfsmittel im Entwicklungsprozess selbst zum Einsatz.',
     'Normal'),
    ('Die Einleitung gliedert sich in Ausgangslage und Problemstellung (1.1), '
     'organisatorische Einbettung der CIT FHNW (1.2), KI-bezogene Unternehmens- und '
     'Projektziele (1.3) sowie Stakeholder- und Kontextanalyse (1.4).',
     'Normal'),
]

insert_paras_after(vorgabe_kap1, intro_absaetze)
print('Kapitel 1 Fliesstext ✓')

# Optionally mark the [Vorgabe] paragraph as internal note
# (leave in place so it's still visible as guidance during drafting)

# ─────────────────────────────────────────────────────────
# 2.  Bibliografie – R44 + R45
#     Insert AFTER R43 (List Paragraph style)
# ─────────────────────────────────────────────────────────
ref_r43 = find_para(doc, '[R43] FHNW CIT', style_name='List Paragraph')
assert ref_r43, 'Ref not found: R43'

insert_paras_after(ref_r43, [
    ('[R44] ICT-Berufsbildung Schweiz / SBFI. (2021). Bildungsplan Informatikerin EFZ / '
     'Informatiker EFZ (Fachrichtung Betriebsinformatik und Applikationsentwicklung). '
     'Staatssekretariat für Bildung, Forschung und Innovation. '
     'https://www.ict-berufsbildung.ch/grundbildung/ict-lehren/informatiker-in-efz/',
     'List Paragraph'),
    ('[R45] FHNW. (o. J.). Berufsbildung – Lernende und Karriere. '
     'Fachhochschule Nordwestschweiz. '
     'https://www.fhnw.ch/de/die-fhnw/karriere/berufsbildung',
     'List Paragraph'),
])
print('Bibliografie R44-R45 ✓')

# ─────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────
doc.save(SRC)
print('Gespeichert:', SRC)
