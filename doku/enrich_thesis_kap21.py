"""
Thesis enrichment – Kapitel 2.1 Wertstromanalyse
Ergänzt basierend auf Benutzerinput + berufsbildung.ch (R49):

IST-Wertstrom: 5 neue präzise Schwachstellen
  – Feedback nicht bildungszielbezogen
  – Lerndokumentation situativ statt kontinuierlich (Lernende)
  – Bildungsberichte Pflicht (BBG Art. 20) aber ohne Kompetenz-Methodik (Praxisplatzbetreuer)
  – Rotationsplanung ignoriert bereits erlangte Kompetenzen
  – IT-Spezialisten schwer mit Bewertungsformulierungen

SOLL-Wertstrom + Reframing:
  – Zentralbotschaft: Transparenz + Qualitätserhöhung, NICHT primär Zeitersparnis
  – Gemeinsame Datenbasis für alle drei Rollen
  – KI unterstützt Bewertung UND Formulierung
  – Lücken werden explizit verbalisiert

Neue Referenz R49: berufsbildung.ch Dokumentieren und Bewerten
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
# 1.  Fliesstext-Intro für 2.1 nach [Vorgabe]-Placeholder
#     Reframing: Transparenz + Qualität als Kernziel
# ─────────────────────────────────────────────────────────
vorgabe_21 = find_para(doc, '[Vorgabe] Wertstromanalyse: aktuellen Prozess (Ist)')
assert vorgabe_21, 'Ref not found: [Vorgabe] 2.1'

insert_paras_after(vorgabe_21, [
    ('Die Wertstromanalyse orientiert sich an der Value-Stream-Mapping-Methode '
     '(vgl. [R17] DORA 2025 Report, S. 73) und vergleicht den manuellen IST-Prozess '
     'mit dem KI-gestützten SOLL-Zustand. Der primäre Nutzen des HK-Trackers liegt '
     'dabei nicht in der Zeitersparnis, sondern in der Transparenz und der '
     'Qualitätserhöhung bei der Kompetenzentwicklung der Lernenden: Alle drei '
     'beteiligten Rollen – Lernende, Praxisplatzbetreuer und Berufsbildner – '
     'erhalten erstmals eine gemeinsame, strukturierte Sicht auf Fortschritt, '
     'Abdeckung und Lücken.',
     'Normal'),
])
print('2.1 Fliesstext-Intro ✓')

# ─────────────────────────────────────────────────────────
# 2.  IST-Wertstrom: 5 neue Schwachstellen
#     Einfügen NACH dem letzten IST-Bullet
#     ("Gesamtaufwand Berufsbildner...")
# ─────────────────────────────────────────────────────────
ref_ist_last = find_para(doc, 'Gesamtaufwand Berufsbildner: geschätzt')
assert ref_ist_last, 'Ref not found: IST Gesamtaufwand'

insert_paras_after(ref_ist_last, [
    ('Feedback an Lernende erfolgt mündlich und unstrukturiert – nicht auf Basis '
     'der Bildungsziele des Bildungsplans EFZ. Handlungskompetenzen werden selten '
     'explizit angesprochen.',
     'List Bullet 2'),
    ('Lerndokumentation durch Lernende: rechtlich vorgeschrieben (BBG Art. 20), '
     'wird aber in der Praxis sehr situativ geführt – meist kurz vor '
     'Bildungsgesprächs-Terminen, nicht prozessbegleitend.',
     'List Bullet 2'),
    ('Bildungsberichte durch Praxisplatzbetreuer: gemäss Pflicht nach '
     'berufsbildung.ch (vgl. [R49]) mindestens einmal pro Semester zu erstellen. '
     'Praxisplatzbetreuer sind IT-Fachspezialisten und verfügen in der Regel '
     'über keine didaktische Grundausbildung in der Kompetenzbewertung – '
     'Bewertungen entstehen intuitiv, ohne Bezug zur Bloom-Taxonomie.',
     'List Bullet 2'),
    ('Rotationsplanung in Excel ohne Berücksichtigung bereits erlangter '
     'Kompetenzen: Welche HKs ein Lernender schon nachgewiesen hat, fliesst '
     'nicht in die Wahl des nächsten Ausbildungsplatzes ein.',
     'List Bullet 2'),
    ('IT-Fachkräfte tun sich generell schwer mit der sprachlichen Formulierung '
     'von Bewertungen: Kompetenznachweise bleiben oberflächlich oder '
     'technisch-beschreibend, ohne den pädagogischen Lernzuwachs zu benennen.',
     'List Bullet 2'),
])
print('2.1 IST Schwachstellen ✓')

# ─────────────────────────────────────────────────────────
# 3.  SOLL-Wertstrom: Reframing + Qualitätsziele ergänzen
#     Einfügen NACH dem letzten SOLL-Bullet
#     ("Zeitersparnis Berufsbildner: Ziel > 50%...")
# ─────────────────────────────────────────────────────────
ref_soll_last = find_para(doc, 'Zeitersparnis Berufsbildner: Ziel > 50% Reduktion')
assert ref_soll_last, 'Ref not found: SOLL Zeitersparnis'

insert_paras_after(ref_soll_last, [
    ('Gemeinsame Datenbasis: Lernende, Praxisplatzbetreuer und Berufsbildner '
     'sehen dieselben Kompetenznachweise, Bewertungen und Fortschrittsdaten – '
     'Transparenz als Grundlage für konstruktive Bildungsgespräche.',
     'List Bullet 2'),
    ('KI unterstützt nicht nur die Bewertung (Bloom-Stufe), sondern auch die '
     'Formulierung: Begründungstexte durch Azure OpenAI helfen IT-Fachkräften, '
     'Kompetenznachweise pädagogisch treffend zu verbalisieren.',
     'List Bullet 2'),
    ('Lücken werden explizit verbalisiert: fehlende HKs sind für alle '
     'Beteiligten sichtbar und mit Sprache benannt – nicht nur als Zahl, '
     'sondern als konkrete Entwicklungsaufgabe.',
     'List Bullet 2'),
    ('Kernpunkt SOLL: Nicht primär Zeitersparnis, sondern Transparenz und '
     'Qualitätserhöhung in der Entwicklung der Lernenden. '
     'Zeitersparnis ist ein willkommener Nebeneffekt, nicht das Hauptziel.',
     'List Bullet 2'),
])
print('2.1 SOLL Reframing ✓')

# ─────────────────────────────────────────────────────────
# 4.  Bibliografie – R49
# ─────────────────────────────────────────────────────────
ref_r48 = find_para(doc, '[R48] Seyff', style_name='List Paragraph')
assert ref_r48, 'Ref not found: R48'

insert_paras_after(ref_r48, [
    ('[R49] SDBB / Berufsbildung.ch. (o. J.). Dokumentieren und Bewerten '
     '– Bildungsbericht und Lerndokumentation in der beruflichen Grundbildung. '
     'Schweizerisches Dienstleistungszentrum Berufsbildung. '
     'https://www.berufsbildung.ch/de/lehrverlauf/dokumentieren-und-bewerten',
     'List Paragraph'),
])
print('Bibliografie R49 ✓')

# ─────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────
doc.save(SRC)
print('Gespeichert:', SRC)
