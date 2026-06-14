"""
Thesis enrichment – «AI as Enabler» (KI als Voraussetzung, nicht nur Optimierung)

Kernbotschaft: Ohne KI (Claude Code) gäbe es diese App nicht.
Der Berufsbildner ist Domain-Experte mit 20+ Jahren IT-Berufserfahrung,
aber ohne aktive Programmierkenntnisse seit ~20 Jahren.
Vor KI-Entwicklungswerkzeugen: professionelle Webapplikation unrealisierbar.

Ergänzungen:
  1.1 Ausgangslage: neuer Bullet – strukturelle Lücke Domain-Wissen vs. Programmierkompetenz
  1.3 KI-Projektziele: Claude Code von «Werkzeug» zu «Enabler» schärfen
  2.1 IST-Wertstrom: Lücke als strukturell-unmögliche Umsetzung benennen
  2.1 SOLL-Wertstrom: Claude Code als «sine qua non» ergänzen
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
# 1.  1.1 Ausgangslage – strukturelle Lücke
#     Einfügen NACH "Abgrenzung: HK-Tracker fokussiert..."
# ─────────────────────────────────────────────────────────
ref_abgrenzung = find_para(doc, 'Abgrenzung: HK-Tracker fokussiert auf interne FHNW')
assert ref_abgrenzung, 'Ref not found: Abgrenzung 1.1'

insert_paras_after(ref_abgrenzung, [
    ('Strukturelle Realisierungslücke: Der einzige Träger des vollständigen '
     'Domain-Wissens – Berufsbildner, Chapter Lead AUP und Coach des Kreis '
     'Future – verfügt über keine aktiven Programmierkenntnisse. Die berufliche '
     'Entwicklungsarbeit endete vor rund 20 Jahren; seither fehlen die '
     'technischen Grundkompetenzen zur eigenständigen Realisierung einer '
     'professionellen Webapplikation. Ohne KI-gestützte Entwicklungswerkzeuge '
     'wäre ein digitaler HK-Tracker für diese Organisation schlicht '
     'nicht umsetzbar – nicht aus Ressourcengründen, sondern strukturell.',
     'List Bullet'),
])
print('1.1 Strukturelle Lücke ✓')

# ─────────────────────────────────────────────────────────
# 2.  1.3 KI-Projektziele – Claude Code von «Tool» zu «Enabler»
#     Ersetze den Sub-Bullet "Einsatz: Spezifikationsgetriebene..."
#     mit einem neuen, schärferen Bullet
#     Einfügen NACH "KI 3: Claude Code ... als KI-gestütztes Entwicklungswerkzeug"
# ─────────────────────────────────────────────────────────
ref_k3 = find_para(doc, 'KI 3: Claude Code (Anthropic) als KI-gestütztes Entwicklungswerkzeug')
assert ref_k3, 'Ref not found: KI 3 Claude Code'

insert_paras_after(ref_k3, [
    ('Enabler-Rolle (sine qua non): Der Berufsbildner und Projektverantwortliche '
     'verfügt über kein aktives Programmier-Knowhow. Claude Code ermöglicht '
     'ihm als Domain-Experten, eine professionelle Full-Stack-Webapplikation '
     '(React/TypeScript + ASP.NET Core + SQL Server + Azure) zu realisieren. '
     'Ohne KI wäre dieses Projekt strukturell unmöglich – die App würde nicht '
     'existieren. Claude Code ist damit keine Effizienzsteigerung, sondern '
     'die Voraussetzung für die Existenz des Projekts.',
     'List Bullet 2'),
])
print('1.3 Claude Code Enabler ✓')

# ─────────────────────────────────────────────────────────
# 3.  2.1 IST-Wertstrom – Umsetzungs-Unmöglichkeit ohne AI
#     Einfügen NACH "IT-Fachkräfte tun sich generell schwer..."
# ─────────────────────────────────────────────────────────
ref_it_formulierung = find_para(
    doc, 'IT-Fachkräfte tun sich generell schwer mit der sprachlichen Formulierung'
)
assert ref_it_formulierung, 'Ref not found: IT-Fachkräfte Formulierung'

insert_paras_after(ref_it_formulierung, [
    ('Fehlende digitale Lösung strukturell bedingt: Die Person mit dem '
     'vollständigen Domain-Wissen (Bildungsplan, Ausbildungsabläufe, '
     'Kompetenzbeurteilung, Rotationslogik) besitzt keine ausreichenden '
     'Programmierkenntnisse, um eigenständig ein digitales Werkzeug zu '
     'entwickeln. Eine Auftragsentwicklung hätte weder Budget noch '
     'Priorisierung erhalten. Die Lücke zwischen Domain-Wissen und '
     'Umsetzungskompetenz war vor dem Aufkommen von KI-Entwicklungswerkzeugen '
     'praktisch unüberbrückbar.',
     'List Bullet 2'),
])
print('2.1 IST Umsetzungs-Unmöglichkeit ✓')

# ─────────────────────────────────────────────────────────
# 4.  2.1 SOLL-Wertstrom – Claude Code als Enabler
#     Einfügen NACH "Kernpunkt SOLL: Nicht primär Zeitersparnis..."
# ─────────────────────────────────────────────────────────
ref_kernpunkt = find_para(doc, 'Kernpunkt SOLL: Nicht primär Zeitersparnis')
assert ref_kernpunkt, 'Ref not found: Kernpunkt SOLL'

insert_paras_after(ref_kernpunkt, [
    ('Claude Code als Entwicklungs-Enabler: Der gesamte SOLL-Zustand setzt '
     'KI-gestützte Softwareentwicklung als Voraussetzung voraus. Claude Code '
     '(Anthropic) ermöglicht dem Berufsbildner ohne aktive Programmierkenntnisse, '
     'eine professionelle Webapplikation eigenständig zu konzipieren, zu '
     'entwickeln und zu betreiben. KI demokratisiert hier die '
     'Softwareentwicklung: Domain-Expertise ersetzt die fehlende '
     'Programmierkompetenz als treibende Kraft. «Vibe Coding» im besten Sinne – '
     'nicht als Abkürzung, sondern als einzig möglicher Weg.',
     'List Bullet 2'),
])
print('2.1 SOLL Claude Code Enabler ✓')

# ─────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────
doc.save(SRC)
print('Gespeichert:', SRC)
