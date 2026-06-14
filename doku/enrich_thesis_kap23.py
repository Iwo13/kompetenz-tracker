"""
Thesis enrichment - Kapitel 2.3 Erwartete Benefits

Restrukturierung nach erkannten Prioritaeten aus Kapitel 1 und 2:
  NACHHER: Qual B1 (Transparenz) -> Qual B2 (Qualitaet) -> Qual B3 (Rotation)
           -> Qual B4 (BBG Art.20) -> Qual B5 (Upskilling)
           -> Quant B6 (Zeit) -> Quant B7 (Konsistenz) -> B8 (Strat. KI)
           -> Risikobenefit -> Negative Benefits

Algorithmus-Notizen:
  - addnext + reversed(items)   = Eintraege NACH ref in Vorwaertsreihenfolge
  - addprevious + items         = Eintraege VOR ref in Vorwaertsreihenfolge (kein reversed!)
  - Rename via w:t XML-Elemente (robust gegenueber Split-Runs)
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
    """Insert items AFTER ref_para in forward order. Uses addnext+reversed."""
    ref_p = ref_para._p
    for text, style in reversed(items):
        ref_p.addnext(make_xml_para(text, style))


def insert_before(ref_para, items):
    """Insert items BEFORE ref_para in forward order. Uses addprevious+forward."""
    ref_p = ref_para._p
    for text, style in items:
        ref_p.addprevious(make_xml_para(text, style))


def find_para(doc, text_fragment, style_name=None):
    for p in doc.paragraphs:
        if text_fragment in p.text:
            if style_name is None or p.style.name == style_name:
                return p
    return None


def fix_para_label(para, old_fragment, new_fragment):
    """Rename text fragment in a paragraph, handling split-run XML safely.
    Collapses all w:t content into the first t-element after replacement."""
    t_elems = list(para._p.iter(qn('w:t')))
    combined = ''.join((t.text or '') for t in t_elems)
    if old_fragment not in combined:
        return False
    new_combined = combined.replace(old_fragment, new_fragment, 1)
    # Put new text in first t, clear the rest
    t_elems[0].text = new_combined
    for t in t_elems[1:]:
        t.text = ''
    return True


# ---- Find reference paragraphs ----
ref_vorgabe_23     = find_para(doc, '[Vorgabe] Erwartete Benefits und Benefits-Kalkulation')
ref_quant_b1       = find_para(doc, 'Quantitativer Benefit 1: Zeitersparnis')
ref_quant_b2       = find_para(doc, 'Quantitativer Benefit 2: Konsistenz')
ref_qual_b1_rot    = find_para(doc, 'Qualitativer Benefit 1: Bessere Rotationsplanung')
ref_qual_b2_up     = find_para(doc, 'Qualitativer Benefit 2: Upskilling Berufsbildner')
ref_upskilling_sub = find_para(doc, 'Berufsbildner lernen durch KI-Begr')

assert ref_vorgabe_23,     'Ref not found: [Vorgabe] 2.3'
assert ref_quant_b1,       'Ref not found: Quant B1'
assert ref_quant_b2,       'Ref not found: Quant B2'
assert ref_qual_b1_rot,    'Ref not found: Qual B1 Rotation'
assert ref_qual_b2_up,     'Ref not found: Qual B2 Upskilling'
assert ref_upskilling_sub, 'Ref not found: Upskilling Sub-Bullet'


# ========================================================
# SCHRITT 1: Quant-Block (B1 Zeit + B2 Konsistenz) nach Qual-Block verschieben
#            Einfuegen NACH dem letzten Upskilling-Sub-Bullet
# ========================================================
body = doc.element.body
all_children = list(body)

idx_qb1  = all_children.index(ref_quant_b1._p)
idx_qlb1 = all_children.index(ref_qual_b1_rot._p)

quant_block = all_children[idx_qb1:idx_qlb1]

for elem in quant_block:
    body.remove(elem)

# Einfuegen in Vorwaertsreihenfolge nach Upskilling-Sub-Bullet
ref_p = ref_upskilling_sub._p
for elem in quant_block:
    ref_p.addnext(elem)
    ref_p = elem  # Cursor nach vorne schieben

print(f'Quant-Block verschoben ({len(quant_block)} Elemente) OK')


# ========================================================
# SCHRITT 2: Benefit-Nummern umbenennen (robust via XML w:t)
# ========================================================
fix_para_label(ref_qual_b1_rot,    'Qualitativer Benefit 1:',  'Qualitativer Benefit 3:')
fix_para_label(ref_qual_b2_up,     'Qualitativer Benefit 2:',  'Qualitativer Benefit 5:')
fix_para_label(ref_quant_b1,       'Quantitativer Benefit 1:', 'Quantitativer Benefit 6:')
fix_para_label(ref_quant_b2,       'Quantitativer Benefit 2:', 'Quantitativer Benefit 7:')
print('Benefit-Nummern umbenannt OK')


# ========================================================
# SCHRITT 3: Fliesstext-Intro nach [Vorgabe]
# ========================================================
insert_after(ref_vorgabe_23, [
    ('Die erwarteten Benefits des HK-Trackers werden bewusst nicht mit der '
     'Zeitersparnis eroeffnet - diese ist ein willkommener Sekundaereffekt, aber '
     'nicht das strategische Primaerziel. Die Leitfrage lautet: Welchen qualitativen '
     'Sprung erleben Lernende, Praxisplatzbetreuer und Berufsbildner in der '
     'Kompetenzentwicklung? Entsprechend gliedert sich die Benefit-Analyse in: '
     'qualitative Primaer-Benefits (B1-B5), die Transparenz und '
     'Beurteilungsqualitaet adressieren; quantifizierbare Sekundaer-Benefits (B6-B7) '
     'mit messbaren Effizienzgewinnen; sowie einen strategischen Organisationsbenefit '
     '(B8) fuer den CIT-Transformationspfad.',
     'Normal'),
])
print('Fliesstext-Intro OK')


# ========================================================
# SCHRITT 4: Neue Qual B1 (Transparenz) und B2 (Qualitaet) VOR Qual B3 (Rotation)
#            insert_before verwendet forward-Iteration mit addprevious
# ========================================================
insert_before(ref_qual_b1_rot, [
    ('Qualitativer Benefit 1: Transparenz - Einheitliche Datenbasis fuer alle drei Rollen  '
     'vgl. [R43] Chapter AUP Konstitution; [R42] Kuhn 2024',
     'List Bullet'),
    ('Lernende, Praxisplatzbetreuer und Berufsbildner sehen erstmals dieselben '
     'Kompetenznachweise, Bewertungen und Fortschrittsdaten in Echtzeit. '
     'Bisher existierten drei parallele, inkompatible Sichten: Excel-Tabellen beim '
     'Berufsbildner, muendliche Ueberlieferung an den APs und situative '
     'Lerndokumentation der Lernenden.',
     'List Bullet 2'),
    ('Konstitutionsanforderung erfuellt: Das Chapter AUP hat in seiner Konstitution '
     'eine "High-Level Sicht zu individuellen Kompetenzfortschritten" als '
     'Leistungsmerkmal verankert (vgl. [R43]). Der HK-Tracker liefert genau diese '
     'Sicht - erstmals digital, strukturiert und aktuell.',
     'List Bullet 2'),
    ('AP-Wechsel ohne Informationsverlust: Neue Praxisplatzbetreuer koennen Lernende '
     'sofort anhand ihrer bisherigen HK-Nachweise einordnen und gezielt an offenen '
     'Kompetenzen weiterarbeiten - statt von Null zu starten.',
     'List Bullet 2'),
    ('Qualitativer Benefit 2: Qualitaetserhoehung - Bloom-Taxonomie als Bewertungsstandard  '
     'vgl. [R10] Abrahamsson et al. 2025; Tag 08 Bloom-Stufen',
     'List Bullet'),
    ('Kompetenzbewertungen folgen neu einem einheitlichen paedagogischen Rahmen '
     '(Bloom-Taxonomie K1-K6). IT-Spezialisten ohne didaktische Grundausbildung '
     'erhalten eine methodische Stuetze, die bisher fehlte - Bewertungen entstehen '
     'nicht mehr intuitiv, sondern begruendet.',
     'List Bullet 2'),
    ('KI schlaegt nicht nur die Bloom-Stufe vor, sondern generiert auch eine '
     'sprachliche Begruendung. IT-Fachkraefte, die sich mit paedagogischen '
     'Formulierungen schwertun, werden aktiv unterstuetzt (vgl. Abschnitt 2.1 '
     'IST-Wertstrom: "Informatiker tun sich schwer mit Bewertungsformulierungen").',
     'List Bullet 2'),
    ('Bildungsberichte werden fundierter und vergleichbarer: statt subjektiver '
     'Einschaetzung strukturierte, begruendete Bewertungen als Grundlage fuer '
     'Abschlusspruefungen und Bildungsgespraeche.',
     'List Bullet 2'),
])
print('Qual B1 (Transparenz) + B2 (Qualitaet) eingefuegt OK')


# ========================================================
# SCHRITT 5: Rotation (B3) - Kompetenz-Luecken-Argument ergaenzen
# ========================================================
ref_rotation_last = find_para(doc, 'Reduktion von')
assert ref_rotation_last, 'Ref not found: Rotation letzter Sub-Bullet'

insert_after(ref_rotation_last, [
    ('Handlungskompetenzen, die ein Lernender an einem AP bereits nachgewiesen hat, '
     'sind beim naechsten Wechsel sofort sichtbar. Rotationsverantwortliche im '
     'Chapter AUP koennen Luecken gezielt schliessen statt zufaellig zuzuweisen.',
     'List Bullet 2'),
])
print('B3 Rotation Luecken-Argument OK')


# ========================================================
# SCHRITT 6: Neue Qual B4 (BBG Art. 20) VOR Qual B5 (Upskilling)
# ========================================================
insert_before(ref_qual_b2_up, [
    ('Qualitativer Benefit 4: Rechtskonformitaet - Strukturierte Grundlage fuer '
     'Bildungsberichte  vgl. [R49] berufsbildung.ch; BBG Art. 20',
     'List Bullet'),
    ('Bildungsberichte sind gesetzlich vorgeschrieben (BBG Art. 20 und '
     'Bildungsverordnung): Praxisplatzbetreuer muessen mindestens einmal pro Semester '
     'einen Bericht erstellen (vgl. [R49]). Bisher entstehen diese ohne strukturierte '
     'Datenbasis und ohne methodischen Bezug zur Bloom-Taxonomie.',
     'List Bullet 2'),
    ('Der HK-Tracker stellt alle relevanten Daten direkt fuer die Berichterstellung '
     'bereit: nachgewiesene Kompetenzen, Bloom-Niveaus, KI-generierte Begruendungen '
     'und offene Luecken - redaktioneller Aufwand sinkt, Qualitaet steigt.',
     'List Bullet 2'),
    ('Nachweisbarkeit und Revisionsicherheit: Kompetenzeinschaetzungen und '
     'Bildungsberichte sind historisch gespeichert - relevant bei kantonalen '
     'Ueberpruefungen und im Rahmen der Abschlusspruefungen (QV).',
     'List Bullet 2'),
])
print('Qual B4 (BBG Art. 20) eingefuegt OK')


# ========================================================
# SCHRITT 7: B6 Zeitersparnis - Messungs-Hinweis ergaenzen
# ========================================================
ref_hochrechnung = find_para(doc, 'Hochrechnung: [X Lernende]')
assert ref_hochrechnung, 'Ref not found: Hochrechnung'

insert_after(ref_hochrechnung, [
    ('Hinweis: Zeitersparnis ist als Sekundaereffekt eingestuft, nicht als '
     'primaeres Projektziel (vgl. 2.1 SOLL-Wertstrom). Konkrete Basisdaten '
     'werden im Pilotbetrieb (Phase 3) erhoben. Schaetzung: ca. 5-10 Min. '
     'manuelle Bloom-Bewertung vs. ca. 1-2 Min. KI-Vorschlag bestaetigen.',
     'List Bullet 2'),
])
print('B6 Zeitersparnis Messungs-Hinweis OK')


# ========================================================
# SCHRITT 8: Strategischer Benefit B8 nach Quant B7 Konsistenz
# ========================================================
ref_konsistenz_last = find_para(doc, 'Ziel: Abweichung < 0.5 Bloom-Stufen')
assert ref_konsistenz_last, 'Ref not found: Konsistenz letzter Sub-Bullet'

insert_after(ref_konsistenz_last, [
    ('Strategischer Benefit B8: HK-Tracker als KI-Proof-of-Concept fuer die CIT  '
     'vgl. [R46] CAS AI-SE; [R47] AI-Reiseplan CIT',
     'List Bullet'),
    ('Das Projekt demonstriert in der Praxis, dass Domain-Experten ohne aktive '
     'Programmierkenntnisse mit KI-Unterstuetzung professionelle Full-Stack-'
     'Webapplikationen realisieren koennen. Fuer die KI-Transformationsstrategie '
     'der CIT (vgl. [R47]) ist dieser Befund direkt relevant: Wissensarbeit '
     'veraendert sich fundamental - KI veraendert nicht einzelne Tools, sondern '
     'die Art, wie Probleme geloest werden.',
     'List Bullet 2'),
    ('Der HK-Tracker liefert dem Chapter AI praktische Erkenntnisse ueber '
     'Azure AI Foundry-Integration, LiteLLM-Gateway-Betrieb und Human-in-the-Loop-'
     'Design in einem internen FHNW-Kontext - uebertragbares Wissen fuer '
     'weitere CIT-Projekte.',
     'List Bullet 2'),
    ('Als CAS AI-SE Abschlussarbeit (vgl. [R46]) dokumentiert das Projekt nicht nur '
     'das Produkt, sondern den Entwicklungsprozess als Lernfeld: Wie funktioniert '
     'KI-gestuetzte Softwareentwicklung durch einen nicht-programmierenden '
     'Domain-Experten in einer Schweizer Bildungsinstitution?',
     'List Bullet 2'),
])
print('B8 Strategischer KI-Benefit OK')


# ========================================================
# Save
# ========================================================
doc.save(SRC)
print('Gespeichert:', SRC)
