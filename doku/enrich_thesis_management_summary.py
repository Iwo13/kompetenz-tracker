"""
Replaces the Management Summary placeholder (paras 18-27) with
a ~230-word flowing abstract in three paragraphs.

Key messages (user-defined):
  1. Transparent linkage: Bildungsplan → Ausbildungsplätze → Lernende
  2. AI as sine qua non: non-programmer creates professional app via Claude Code
  3. Transferable to further vocational training programs at FHNW
"""
import sys
from xml.sax.saxutils import escape as xml_escape
from docx import Document
from docx.oxml.ns import qn
from lxml import etree

DOCX_PATH = r'doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'

NRM = 'Standard'


def make_para(text, style_id):
    return etree.fromstring(
        f'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:pPr><w:pStyle w:val="{style_id}"/></w:pPr>'
        f'<w:r><w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r>'
        f'</w:p>'
    )


ABSTRACT = [
    # Paragraph 1: Problem
    ('Die manuelle Dokumentation von Handlungskompetenzen (HK) in der IT-Berufsbildung '
     'ist fragmentiert, zeitaufwendig und für alle Beteiligten intransparent. '
     'Lernende kennen ihren Ausbildungsstand kaum, Berufsbildner arbeiten ohne '
     'systematische Übersicht, und Ausbildungsverantwortliche können Kompetenzlücken '
     'nicht gezielt erkennen und schliessen.'),

    # Paragraph 2: Solution — the central connection + personas + Lerndokumentation
    ('Der HK-Tracker schliesst diese Lücke als webbasierte Applikation '
     '(React 19, ASP.NET Core 8, Azure OpenAI / GPT-4o), die erstmals eine '
     'strukturierte, transparente Verknüpfung zwischen den Vorgaben des Bildungsplans '
     'Informatiker/in EFZ [R50], den Ausbildungsplätzen der Abteilung und den '
     'Lernenden herstellt. '
     'Berufsbildner erfassen Kompetenzen nach der Bloom-Taxonomie (K1–K6), '
     'identifizieren Lücken in der Ausbildungsplatz-Abdeckung und können gezielt '
     'Aufgaben zuweisen. '
     'Lernende erhalten erstmals eine vollständige, übersichtliche Sicht auf Inhalt '
     'und Stand ihrer Ausbildung — und erfüllen dabei gleichzeitig die gesetzlich '
     'vorgeschriebene Lerndokumentation (Bildungsplan Kap. 3, SBFI-Ausbildungsverordnung). '
     'Ausbildungsverantwortliche gewinnen eine aggregierte Sicht auf alle Lernenden '
     'und können die Ausbildungsqualität abteilungsweit sichern.'),

    # Paragraph 3: AI development insight + transferability
    ('Ein zentrales Ergebnis aus KI-Entwicklungsperspektive: Der HK-Tracker wurde '
     'von einem Nicht-Programmierer ausschliesslich mithilfe von Claude Code '
     '(Specification-Driven Development) realisiert — sine qua non, '
     'denn ohne KI als Entwicklungspartner wäre dieses Projekt nicht umsetzbar '
     'gewesen. Dies demonstriert exemplarisch das transformative Potenzial '
     'generativer KI als Enabler für Fachpersonen ohne Programmierhintergrund. '
     'Das lehrberuf-agnostische Datenmodell erlaubt die Übertragung des HK-Trackers '
     'auf weitere Berufsbildungen an der FHNW — ein neuer Lehrberuf erfordert '
     'ausschliesslich eine strukturierte JSON-Datei, ohne Code-Anpassungen.'),
]


def main():
    doc = Document(DOCX_PATH)
    paras = doc.paragraphs

    # Find Management Summary heading and next Heading 1
    ms_heading = None
    next_h1 = None

    for p in paras:
        s = p.style.name
        t = p.text.strip()
        if ms_heading is None:
            if ('berschrift1' in s or 'Heading 1' in s) and 'Management' in t and 'Summary' in t:
                ms_heading = p
        else:
            if ('berschrift1' in s or 'Heading 1' in s):
                next_h1 = p
                break

    if not ms_heading:
        print("ERROR: Management Summary heading not found"); sys.exit(1)
    if not next_h1:
        print("ERROR: next Heading 1 not found after Management Summary"); sys.exit(1)

    print(f"MS heading:  {ms_heading.text}")
    print(f"Next H1:     {next_h1.text[:60]}")

    # Remove all paragraphs between MS heading and next H1
    body_el = ms_heading._p.getparent()
    all_elems = list(body_el)
    idx_ms = all_elems.index(ms_heading._p)
    idx_h1 = all_elems.index(next_h1._p)

    to_remove = all_elems[idx_ms + 1 : idx_h1]
    print(f"Removing {len(to_remove)} placeholder paragraphs")
    for el in to_remove:
        body_el.remove(el)

    # Insert abstract paragraphs before next H1
    anchor = next_h1._p
    for text in ABSTRACT:
        anchor.addprevious(make_para(text, NRM))

    print(f"Inserted {len(ABSTRACT)} abstract paragraphs")

    doc.save(DOCX_PATH)
    print(f"\nSaved: {DOCX_PATH}")
    print(f"\nAbstract word count (approx): "
          f"{sum(len(t.split()) for t in ABSTRACT)} words")


if __name__ == '__main__':
    main()
