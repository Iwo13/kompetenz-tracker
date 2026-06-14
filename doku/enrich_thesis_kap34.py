"""
Thesis enrichment - Kapitel 3.4 Einbezug der Stakeholder

Ergaenzungen:
  1. Fliesstext-Intro: Persona-Mapping auf reale Stakeholder
  2. Konkretes Stakeholder-Profil: Iwo Kuhn als Leiter ICT Berufsbildung HSI
     (8 Applikationsentwickler + 3 IMS Praktikanten)
  3. Korrektur para 393: Samuel Fricker ist Leiter CAS (nicht Betreuer);
     Norbert Seyff ist Betreuer der Abschlussarbeit
  4. Pilotbetrieb konkretisiert: 2 Lernende + 1 Praxisplatzbetreuer,
     zweiphasig (Schulung -> Feedback 1, Pilot -> Feedback 2)
  5. Neu: FHNW-weite Praesentation bei allen Berufsbildungszustaendigen
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = r'C:\Projekte\IT-Lehre Handlungskompetenzen\doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'
doc = Document(SRC)

STYLE_ID = {
    'Normal':         'Standard',
    'List Bullet':    'Aufzhlungszeichen',
    'List Bullet 2':  'Aufzhlungszeichen2',
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


def fix_para_text(para, old_fragment, new_fragment):
    t_elems = list(para._p.iter(qn('w:t')))
    combined = ''.join((t.text or '') for t in t_elems)
    if old_fragment not in combined:
        return False
    new_combined = combined.replace(old_fragment, new_fragment, 1)
    t_elems[0].text = new_combined
    for t in t_elems[1:]:
        t.text = ''
    return True


# ---- Referenzen ----
ref_vorgabe_34   = find_para(doc, '[Vorgabe] Einbezug der Stakeholder, inklusive Schulung')
ref_informell    = find_para(doc, 'Informelle Gespräche mit Berufsbildner-Kollegen')
ref_samuel       = find_para(doc, 'Konzept-Review durch Betreuer Prof. Dr. Samuel Fricker')
ref_pilot_bullet = find_para(doc, 'Geplanter Stakeholder-Einbezug (Phase 3 Pilot)')
ref_usability    = find_para(doc, 'Usability-Test mit 2 Lernenden')
ref_ai4km        = find_para(doc, 'Feedback-Kategorisierung mit AI4KM')
ref_schulung     = find_para(doc, 'Schulungskonzept:')

assert ref_vorgabe_34,   'Ref not found: [Vorgabe] 3.4'
assert ref_informell,    'Ref not found: Informelle Gespraeche'
assert ref_samuel,       'Ref not found: Samuel Fricker'
assert ref_pilot_bullet, 'Ref not found: Geplanter Einbezug'
assert ref_usability,    'Ref not found: Usability-Test'
assert ref_ai4km,        'Ref not found: AI4KM Feedback'
assert ref_schulung,     'Ref not found: Schulungskonzept'


# ========================================================
# 1. Fliesstext-Intro nach [Vorgabe]
# ========================================================
insert_after(ref_vorgabe_34, [
    ('Der Stakeholder-Einbezug im HK-Tracker-Projekt orientiert sich an den vier '
     'in Abschnitt 1.4.1 definierten Cooper-Personas und deren realen Entsprechungen '
     'in der FHNW Corporate IT. Die KUI-Persona (Leiter Berufsbildung) ist identisch '
     'mit dem Projektverantwortlichen selbst (Double-Role). Die Michi-Praxisbildner-'
     'Persona umfasst die Praxisplatzbetreuer an den zehn CIT-Ausbildungsplaetzen. '
     'Die Heinz-Lernenden-Persona repraesentiert die aktuelle Lernenden-Kohorte: '
     'acht Lernende in der Fachrichtung Applikationsentwicklung (EFZ) und drei '
     'Praktikanten der Informatikmittelschule (IMS). '
     'Die Einbindung erfolgt gestaffelt – von informellen Reviews in der '
     'Entwicklungsphase bis zur strukturierten Pilotevaluation.',
     'Normal'),
])
print('Fliesstext-Intro OK')


# ========================================================
# 2. Konkretes Stakeholder-Profil nach "Informelle Gespräche..."
# ========================================================
insert_after(ref_informell, [
    ('Stakeholder-Profil Berufsbildner (KUI-Persona): Iwo Kuhn ist Leiter der '
     'ICT Berufsbildung an der FHNW Hochschule fuer Informatik (HSI) und '
     'verantwortlich fuer die Ausbildung von acht Lernenden in der Fachrichtung '
     'Applikationsentwicklung (Informatiker/in EFZ) sowie drei Praktikanten der '
     'Informatikmittelschule (IMS). In seiner Rolle als Chapter Lead CP-AUP '
     'koordiniert er alle zehn Ausbildungsplaetze der CIT. '
     'Als Primaerentwickler und gleichzeitig Hauptnutzer des HK-Trackers '
     'repraesentiert er die KUI-Persona direkt (vgl. Abschnitt 1.4).',
     'List Bullet 2'),
])
print('Stakeholder-Profil OK')


# ========================================================
# 3. Korrektur: Samuel Fricker = Leiter CAS (nicht Betreuer)
#              Norbert Seyff = Betreuer der Abschlussarbeit
# ========================================================
fixed = fix_para_text(
    ref_samuel,
    'Konzept-Review durch Betreuer Prof. Dr. Samuel Fricker',
    'Konzept-Review durch Betreuer Prof. Dr. Norbert Seyff (Betreuer Abschlussarbeit, '
    'Dozent Personalisierung CAS AI-SE, Modultag 11); '
    'Samuel Fricker (Prof. Dr.) ist Leiter des CAS AI-SE'
)
print(f'Samuel Fricker Korrektur: {"OK" if fixed else "NICHT GEFUNDEN – prueefen"}')


# ========================================================
# 4. Pilotbetrieb konkretisieren: zweiphasig, konkrete Personen
#    Einfuegen NACH "Geplanter Stakeholder-Einbezug" Hauptbullet,
#    VOR "Strukturierte Interviews mit 2 Berufsbildnern"
# ========================================================
ref_interviews = find_para(doc, 'Strukturierte Interviews mit 2 Berufsbildnern')
assert ref_interviews, 'Ref not found: Strukturierte Interviews'

insert_before(ref_interviews, [
    ('Pilotgruppe: 2 Lernende (Applikationsentwicklung EFZ) + 1 Praxisplatzbetreuer '
     '– repraesentieren die Kernpersonas Heinz Platt und Michi Praxisbildner.',
     'List Bullet 2'),
    ('Phase A – Schulung und erstes Feedback: Einfuehrungsschulung (~30 Min.) '
     'mit Live-Demo und App-Onboarding; anschliessend strukturiertes Feedback '
     'zu Verstaendlichkeit, Navigation und KI-Vorschlaegen (Think-Aloud-Protokoll '
     'und kurzer Fragebogen).',
     'List Bullet 2'),
    ('Phase B – Pilotbetrieb und abschliessendes Feedback: Selbststaendige Nutzung '
     'ueber mehrere Wochen im Alltagsbetrieb; anschliessend vertiefte Feedback-Runde '
     'zu Nutzungsfrequenz, wahrgenommenem Nutzen, Qualitaet der KI-Bewertungen '
     'und Verbesserungsideen.',
     'List Bullet 2'),
])
print('Pilotbetrieb zweiphasig OK')


# ========================================================
# 5. FHNW-weite Praesentation VOR Schulungskonzept
# ========================================================
insert_before(ref_schulung, [
    ('FHNW-weite Praesentation und Feedback-Runde:',
     'List Bullet'),
    ('Praesentiert wird der HK-Tracker bei allen Berufsbildungszustaendigen '
     'der FHNW – ueber die CIT hinaus. Ziel: Bekanntmachung des Projekts, '
     'Aufnahme von Rueckmeldungen zu Uebertragbarkeit und Interesse '
     'anderer Departemente, Identifikation weiterer Pilotpartner.',
     'List Bullet 2'),
    ('Feedback wird strukturiert aufgenommen (Bewertungsdimensionen: '
     'Relevanz, Benutzerfreundlichkeit, Erweiterungsbedarf auf andere '
     'Lehrberufe) und fliesst in die Weiterentwicklung des HK-Trackers ein.',
     'List Bullet 2'),
])
print('FHNW-weite Praesentation OK')


# ========================================================
# Save
# ========================================================
doc.save(SRC)
print('Gespeichert:', SRC)
