"""
Thesis enrichment - Erweiterbarkeit auf weitere Lehrberufe

Ergaenzungen:
  1. 2.2 KI 4 (Basisdaten-Import): Architektur-Note – neuer Lehrberuf = neues JSON
  2. 4.2 Wissenschaftlicher Beitrag: bestehende Sub-Bullet ausbauen mit Mechanismus + Beispiele
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
    ref_p = ref_para._p
    for text, style in reversed(items):
        ref_p.addnext(make_xml_para(text, style))


def insert_before(ref_para, items):
    ref_p = ref_para._p
    for text, style in items:
        ref_p.addprevious(make_xml_para(text, style))


def find_para(doc, text_fragment, style_name=None):
    for p in doc.paragraphs:
        if text_fragment in p.text:
            if style_name is None or p.style.name == style_name:
                return p
    return None


# ========================================================
# 1. 2.2 KI 4: Erweiterbarkeits-Note nach XLSX-Import-Bullet
# ========================================================
ref_xlsx_import = find_para(doc, 'XLSX-Import: Kompetenzen der Ausbildungspl')
assert ref_xlsx_import, 'Ref not found: XLSX-Import KI4'

insert_after(ref_xlsx_import, [
    ('Erweiterbarkeit auf weitere Lehrberufe: Die Architektur ist bewusst '
     'lehrberuf-agnostisch ausgelegt. Das Datenmodell kennt keinen fixen Bezug '
     'auf Informatik EFZ – der Lehrberuf wird als konfigurierbarer Parameter '
     'behandelt. Ein neuer Lehrberuf wird durch Hinterlegen einer weiteren '
     'JSON-Datei (strukturiert nach SBFI-Bildungsplan) aktiviert; '
     'mit dem geplanten KI-gestützten PDF-Import genuegt zukuenftig das '
     'Einlesen des offiziellen SBFI-Bildungsplan-Dokuments. '
     'Bestehende Bewertungs- und Rotationslogik bleibt unverändert.',
     'List Bullet 2'),
])
print('2.2 KI 4 Erweiterbarkeits-Note OK')


# ========================================================
# 2. 4.2 Wissenschaftlicher Beitrag: Sub-Bullet ausbauen
#    Bestehende Zeile: "Anwendbar auf andere Hochschulen, Lehrberufe..."
#    -> Weitere Sub-Bullets (List Bullet 2 bleibt, neue als List Bullet 2 darunter)
# ========================================================
ref_transferierbar = find_para(doc, 'Anwendbar auf andere Hochschulen, Lehrberufe')
assert ref_transferierbar, 'Ref not found: Transferierbarkeit 4.2'

insert_after(ref_transferierbar, [
    ('Technischer Mechanismus: Ein neuer Lehrberuf erfordert ausschliesslich '
     'das Hinterlegen einer strukturierten JSON-Datei mit den Handlungskompetenzen '
     'und Leistungszielen des jeweiligen SBFI-Bildungsplans. '
     'Saemtliche App-Funktionen – Kompetenzerfassung, Bloom-Bewertung, '
     'Rotationsplanung, KI-Auswertung – arbeiten unmittelbar auf den neuen Daten. '
     'Kein Anpassungsbedarf im Applikationscode.',
     'List Bullet 2'),
    ('Konkrete Erweiterungsszenarien: Kauffrau/Kaufmann EFZ (Fachrichtung IT), '
     'Mediamatiker/in EFZ, Entwickler digitales Business EFZ – alle verfuegen '
     'ueber SBFI-Bildungsplaene mit Handlungskompetenzen und sind damit '
     'direkt importierbar. Auch andere FHNW-Departemente oder '
     'Schweizer Ausbildungsbetriebe mit aehnlichen Lehrberufs-Portfolios '
     'koennten den HK-Tracker ohne Code-Aenderung adaptieren.',
     'List Bullet 2'),
    ('Langfristige Vision: Mit dem geplanten KI-gestuetzten PDF-Import (KI 4, '
     'vgl. Abschnitt 2.2) genuegt das Hochladen des offiziellen SBFI-Dokuments, '
     'um einen neuen Lehrberuf zu aktivieren – die Erweiterung wird von einem '
     'technischen Prozess zu einem reinen Konfigurationsschritt.',
     'List Bullet 2'),
])
print('4.2 Transferierbarkeit ausgebaut OK')


# ========================================================
# Save
# ========================================================
doc.save(SRC)
print('Gespeichert:', SRC)
