"""
Enriches Kapitel 4.3 "Grenzen und Risiken":

  1. Replaces [Vorgabe] intro (para 551) with proper flowing text
  2. Inserts new section 4.3.3 "Pädagogisches Risiko: Oberflächliches Kompetenz-Tracking"
     (before Heading 2 "4.4") with Risk + Gegenargumente + Lerndokumentation-Pflicht [R50]
"""
import sys
from xml.sax.saxutils import escape as xml_escape
from docx import Document
from docx.oxml.ns import qn
from lxml import etree

DOCX_PATH = r'doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'

NRM = 'Standard'
H3  = 'berschrift3'
LB  = 'Aufzhlungszeichen'
LB2 = 'Aufzhlungszeichen2'


def make_para(text, style_id, bold=False, italic=False):
    b = '<w:b/>' if bold else ''
    i = '<w:i/>' if italic else ''
    rpr = f'<w:rPr>{b}{i}</w:rPr>' if (bold or italic) else ''
    return etree.fromstring(
        f'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:pPr><w:pStyle w:val="{style_id}"/></w:pPr>'
        f'<w:r>{rpr}<w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r>'
        f'</w:p>'
    )


def fix_text(para, old, new):
    t_elems = list(para._p.iter(qn('w:t')))
    combined = ''.join((t.text or '') for t in t_elems)
    if old not in combined:
        return False
    t_elems[0].text = combined.replace(old, new, 1)
    for t in t_elems[1:]:
        t.text = ''
    return True


# =========================================================================
# New intro text (replaces [Vorgabe])
# =========================================================================
INTRO = (
    'Die kritische Reflexion der Grenzen und Risiken gliedert sich in vier Bereiche: '
    'rechtlich-datenschutzrechtliche Risiken, kognitiv-pädagogische Risiken, '
    'technische Risiken sowie methodische Grenzen. Zusätzlich werden in den '
    'Unterkapiteln 4.3.1–4.3.3 drei spezifische Risikofelder vertieft: '
    'Sicherheitsrisiken durch KI-generierten Code, Nachhaltigkeitsbetrachtung (SusAF) '
    'und das pädagogische Risiko eines oberflächlichen Kompetenz-Trackings.'
)

# =========================================================================
# New 4.3.3 section content (inserted before Heading 2 "4.4")
# =========================================================================
SECTION_433 = [
    ('4.3.3  Pädagogisches Risiko: Oberflächliches Kompetenz-Tracking', H3),

    ('Ein legitimes pädagogisches Risiko besteht darin, dass Lernende den HK-Tracker '
     'primär als administrative Pflicht wahrnehmen könnten, ohne sich inhaltlich mit '
     'der eigenen Kompetenzerreichung auseinanderzusetzen. '
     'Dieses Risiko verdient eine differenzierte Einordnung.', NRM),

    ('Einordnung: Status quo ist bereits suboptimal', H3),

    ('Die kritische Frage muss lauten: Ist der Zustand mit dem HK-Tracker schlechter '
     'als ohne ihn? Die Antwort ist klar nein. Auch heute setzen sich Lernende '
     'in der überwiegenden Mehrheit kaum systematisch mit ihrer Kompetenzerreichung '
     'auseinander — nicht weil sie es nicht wollen, sondern weil geeignete Instrumente '
     'zur Visualisierung und Reflexion fehlen. '
     'Der HK-Tracker kann diesen Zustand nur verbessern, nicht verschlechtern.', NRM),

    ('Drei strukturelle Gegenargumente', H3),

    ('Kompetenzförderung durch Aufgaben, nicht durch Reflexion: '
     'Handlungskompetenzen werden in der Berufsbildung primär durch das Bearbeiten '
     'realer Arbeitsaufgaben entwickelt (vgl. Kap. 2.1). '
     'Der HK-Tracker ändert diesen Grundmechanismus nicht — er visualisiert laufend, '
     'welche Kompetenzen durch welche Aufgaben bereits gefördert wurden und welche '
     'Bereiche noch unabgedeckt sind.', LB),
    ('Lückenidentifikation ermöglicht gezielte Aufgabenstellung: '
     'Wenn der Berufsbildner auf einen Blick erkennt, dass Lernende in bestimmten '
     'Handlungskompetenzen noch keine Erfahrung haben, kann er gezielt entsprechende '
     'Aufgaben zuweisen. Dies entspricht genau der pädagogischen Kernaufgabe '
     '(BBG Art. 20) und wird durch den Tracker werkzeugunterstützt.', LB),
    ('Transparenz schafft Orientierung: '
     'Lernende erhalten erstmals eine vollständige, übersichtliche Sicht auf den '
     'Inhalt ihrer Ausbildung und ihren aktuellen Stand. '
     'Diese Transparenz ist ein eigenständiger Wert — auch wenn keine aktive Reflexion '
     'stattfindet, entsteht implizites Bewusstsein über die eigene Ausbildungssituation.', LB),

    ('Gesetzliche Lerndokumentation als positiver Nebeneffekt', H3),

    ('Ein bedeutsamer struktureller Vorteil, der das pädagogische Risiko zusätzlich '
     'relativiert: Der HK-Tracker erfüllt gleichzeitig die gesetzlich vorgeschriebene '
     'Lerndokumentation. Der Bildungsplan Informatiker/in EFZ '
     '(Kapitel 3 «Ausbildung in berufsbezogener Praxis», [R50]) und die '
     'SBFI-Ausbildungsverordnung schreiben vor, dass Lernende laufend ihre '
     'wesentlichen Arbeiten, Fähigkeiten und Erfahrungen festhalten und dass der '
     'Berufsbildner dies mindestens einmal pro Semester kontrollieren und unterzeichnen '
     'muss. Der HK-Tracker schafft diese Lerndokumentation als strukturierten '
     'Nebeneffekt der laufenden HK-Erfassung — ohne zusätzlichen Aufwand '
     'für Lernende oder Berufsbildner.', NRM),

    ('Residualrisiko und Massnahme', H3),

    ('Das Residualrisiko — dass der Tracker zur reinen Checkbox-Übung ohne '
     'inhaltliche Auseinandersetzung degeneriert — ist real, aber mitigierbar. '
     'Für den Pilotbetrieb (Phase 3, Juli–August 2026) ist ein kurzes Onboarding '
     '(ca. 15 Minuten) geplant, das Lernenden und Berufsbildnern Zweck, '
     'Nutzen und Funktionsweise des Trackers erklärt. '
     'Langfristig empfiehlt sich eine Integration in die Semestergespräche '
     '(BBG Art. 20): Der HK-Tracker als Gesprächsgrundlage, nicht als '
     'Selbstzweck.', NRM),
]


def main():
    doc = Document(DOCX_PATH)
    paras = doc.paragraphs

    vorgabe_para = None
    h44_para = None

    for p in paras:
        s = p.style.name
        t = p.text.strip()
        if '[Vorgabe] Kritische Reflexion' in t and '4.3' in ''.join(
                q.text for q in paras[max(0, paras.index(p)-3):paras.index(p)+1]):
            vorgabe_para = p
        if '[Vorgabe] Kritische Reflexion: Grenzen' in t:
            vorgabe_para = p
        if ('berschrift2' in s or 'Heading 2' in s) and '4.4' in t:
            h44_para = p

    # Fallback: find by text alone
    if not vorgabe_para:
        for p in paras:
            if '[Vorgabe] Kritische Reflexion' in p.text:
                vorgabe_para = p
                break

    if not vorgabe_para:
        print("ERROR: [Vorgabe] intro para not found"); sys.exit(1)
    if not h44_para:
        print("ERROR: 4.4 heading not found"); sys.exit(1)

    print(f"Vorgabe para: {vorgabe_para.text[:70]}")
    print(f"4.4 heading:  {h44_para.text[:70]}")

    # 1. Replace [Vorgabe] intro with proper text
    ok = fix_text(vorgabe_para, vorgabe_para.text.strip(), INTRO)
    if not ok:
        # direct replacement
        t_elems = list(vorgabe_para._p.iter(qn('w:t')))
        if t_elems:
            t_elems[0].text = INTRO
            for t in t_elems[1:]:
                t.text = ''
            ok = True
    print(f"Intro replaced: {ok}")

    # 2. Insert 4.3.3 section before 4.4 heading
    anchor = h44_para._p
    for text, style in SECTION_433:
        anchor.addprevious(make_para(text, style))
    print(f"Inserted {len(SECTION_433)} paragraphs (4.3.3 section)")

    doc.save(DOCX_PATH)
    print(f"\nSaved: {DOCX_PATH}")


if __name__ == '__main__':
    main()
