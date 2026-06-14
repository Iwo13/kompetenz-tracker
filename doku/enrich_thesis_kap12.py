"""
Thesis enrichment – Kapitel 1.2 Organisatorische Einbettung Fliesstext
Ergänzt basierend auf:
  - CIT-Organigramm (Anhang/Organigramm.pdf)
  - Chapter Ausbildungsplätze Konstitution (Anhang/Chapter_Ausbildungsplätze.docx)

Fügt 3 Fliesstext-Absätze nach [Vorgabe]-Placeholder ein:
  1. CIT und Kreisorganisation – Zellstrukturdesign, Organigramm-Referenz
  2. Peripheriekreise vs. Zentrumskreise – Kreis Future als Lernenden-Heimkreis
  3. Chapter AUP – Konstitution, High-Level Sicht, direkter Bezug zu HK-Tracker
Aktualisiert den [TODO]-Organigramm-Hinweis.
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
# 1.2 – Fliesstext nach [Vorgabe]-Placeholder
# ─────────────────────────────────────────────────────────
vorgabe_12 = find_para(
    doc,
    '[Vorgabe] Organisatorische Einbettung, zentrale Randbedingungen'
)
assert vorgabe_12, 'Ref not found: [Vorgabe] 1.2'

fliesstext_12 = [
    # Absatz 1: CIT und Kreisorganisation
    ('Die Corporate IT (CIT) der FHNW ist die organisatorische Heimat des HK-Trackers. '
     'Seit Sommer 2023 operiert die CIT nach dem Prinzip des Zellstrukturdesigns '
     '(vgl. [R39] Pfläging & Hermann 2020): Anstelle einer klassischen Hierarchie besteht '
     'die Organisation aus dezentralen, selbstorganisierten Kreisen. Der Leiter CIT und '
     'die People Manager*in übernehmen übergreifende Führungs- und Personalaufgaben, '
     'während Betrieb und Wertschöpfung in den Kreisen selbst verantwortet werden '
     '(vgl. CIT-Organigramm, Abbildung A.1 im Anhang).',
     'Normal'),
    # Absatz 2: Kreistypen, Kreis Future
    ('Das CIT-Organigramm unterscheidet zwei Kreis-Typen: Peripheriekreise erbringen '
     'direkte IT-Dienstleistungen für die FHNW – darunter Workplace Engineering, '
     'Cloud Infrastructure Services, Collaboration, Enterprise Platforms, '
     'Software Engineering, Web, Network & Datacenter, Protection & Design sowie '
     'vier IT-Servicedesk-Standorte (Windisch, Brugg, Muttenz, Olten). '
     'Zentrumskreise unterstützen interne Belange der CIT: People & Culture, '
     'Strategy & Business Alignment – und Kreis Future, der Heimkreis der '
     'ICT-Lernenden. Kreis Future ist verantwortlich für die Entwicklung der Lernenden '
     'zu Fachpersonen, Kompetenzerweiterung, gegenseitige Unterstützung, '
     'Anlassorganisation und Kommunikation unter den Lernenden '
     '(vgl. [R42] Kuhn 2024).',
     'Normal'),
    # Absatz 3: Chapter AUP und direkter Bezug zu HK-Tracker
    ('Ergänzend zu den Kreisen koordinieren Chapters themenübergreifende Aufgaben '
     'innerhalb der CIT. Das Chapter «Ausbildungsplätze» (Kürzel: CP-AUP, '
     'Chapter Lead: Iwo Kuhn) vernetzt alle Praxisbildner über die Kreisgrenzen hinweg: '
     'Rotationskoordination, Kompetenz-Alignment zwischen den zehn Ausbildungsplätzen, '
     'gegenseitige Unterstützung sowie – ausdrücklich in der Chapter-Konstitution '
     'festgehalten – die Bereitstellung einer «High-Level Sicht zu den individuellen '
     'Kompetenzfortschritten» für die aktiven Praxisbildner (vgl. [R43] CIT FHNW 2024). '
     'Der HK-Tracker ist das digitale Werkzeug, das diesen in der Konstitution '
     'beschriebenen Bedarf erstmals systematisch adressiert.',
     'Normal'),
]

insert_paras_after(vorgabe_12, fliesstext_12)
print('1.2 Fliesstext ✓')

# ─────────────────────────────────────────────────────────
# [TODO] Organigramm – aktualisieren
# ─────────────────────────────────────────────────────────
todo_org = find_para(doc, '[TODO: Organigramm FHNW Berufsbildung als Abbildung einfügen')
if todo_org:
    # Replace text in the run
    for run in todo_org.runs:
        if '[TODO:' in run.text:
            run.text = '[Abbildung A.1: CIT-Organigramm – siehe Anhang/Organigramm.pdf]'
            break
    print('TODO Organigramm aktualisiert ✓')

# ─────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────
doc.save(SRC)
print('Gespeichert:', SRC)
