"""
Enriches Kapitel 2.4 'Vorgehen zur Einführung und Validierung':
- Adds SDD methodology intro BEFORE existing Phase 1/2/3 bullets
- Documents 3-layer design process (Mockup / Verbal / Claude Code)
- FHNW Styleguide as design standard
- Conversational optimization loops
- Adds R54 (FHNW Styleguide) + R55 (Axisbits) to Literaturverzeichnis
"""
import sys
from xml.sax.saxutils import escape as xml_escape
from docx import Document
from docx.oxml.ns import qn
from lxml import etree

DOCX_PATH = r'doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'

LB  = 'Aufzhlungszeichen'
LB2 = 'Aufzhlungszeichen2'
NRM = 'Standard'


def make_para(text, style_id):
    return etree.fromstring(
        f'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:pPr><w:pStyle w:val="{style_id}"/></w:pPr>'
        f'<w:r><w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r>'
        f'</w:p>'
    )


def insert_before(ref_para, items):
    """Insert paragraphs BEFORE ref_para in forward order (addprevious, no reverse)."""
    ref_p = ref_para._p
    for text, style in items:
        ref_p.addprevious(make_para(text, style))


def insert_after(ref_para, items):
    """Insert paragraphs AFTER ref_para in forward order (addnext + reversed)."""
    ref_p = ref_para._p
    for text, style in reversed(items):
        ref_p.addnext(make_para(text, style))


def main():
    doc = Document(DOCX_PATH)
    paras = doc.paragraphs

    # --- Find anchors ---
    phase1_para = None    # "Phase 1 (abgeschlossen)" bullet in 2.4
    vorgabe_24  = None    # [Vorgabe] paragraph in 2.4
    r53_para    = None    # R53 in Literaturverzeichnis

    in_24 = False
    for i, para in enumerate(paras):
        t = para.text.strip()
        if '2.4' in t and 'Vorgehen' in t:
            in_24 = True
        if in_24 and '[Vorgabe]' in t and 'Einführung' in t:
            vorgabe_24 = para
        if in_24 and 'Phase 1' in t and 'abgeschlossen' in t and phase1_para is None:
            phase1_para = para
        if in_24 and (t.startswith('2.5') or t.startswith('3 ')):
            in_24 = False
        if '[R53]' in t:
            r53_para = para

    if phase1_para is None:
        print("ERROR: 'Phase 1 (abgeschlossen)' not found in 2.4"); sys.exit(1)
    print(f"Anchor 2.4 Phase1: {phase1_para.text[:80]}")
    if r53_para:
        print(f"Anchor R53: {r53_para.text[:80]}")

    # -------------------------------------------------------------------------
    # 1. Insert methodology content BEFORE "Phase 1 (abgeschlossen)" bullet
    # -------------------------------------------------------------------------
    if 'SDD' not in ''.join(p.text for p in paras[paras.index(phase1_para)-5:paras.index(phase1_para)]):

        new_content = [
            # Intro paragraph
            (
                'Das Entwicklungsvorgehen des HK-Trackers folgt dem Prinzip der '
                'Spezifikationsgetriebenen Entwicklung (SDD, vgl. Tag 01 CAS AI-SE) kombiniert '
                'mit agilen Iterationszyklen nach dem 7-Phasen-Modell der Softwareentwicklung '
                '[R55]. Da der Projektverantwortliche über kein aktives Programmier-Knowhow '
                'verfügt, übernahm Claude Code (Anthropic, KI 1) die vollständige '
                'Implementierung — jedes Feature durchlief dabei einen klaren Dreischritt:',
                NRM
            ),
            # Layer 1
            (
                'Schritt 1 – Spezifikation: Bevor eine einzige Zeile Code generiert wurde, '
                'existierte eine vollständige Anforderungsbeschreibung — entweder als '
                'PPTX-Mockup oder als präzise verbale Spezifikation im Gespräch mit Claude Code.',
                LB
            ),
            (
                'PPTX-Mockups (Anhang A.4): Für alle strukturierten Screens '
                '(Übersichtsseite, Kompetenz-Tracking, AP-Abdeckungsmatrix, Rotationsverwaltung) '
                'erstellte der Projektverantwortliche 21 Folien in PowerPoint. '
                'Designgrundlage war der FHNW Styleguide V5 [R54]: Primärfarben FHNW Navy '
                '(#002B5C) und FHNW Yellow (#FFD700), Schriftart Inter (Google Fonts), '
                'Bootstrap-basiertes Komponentensystem. Diese Mockups dienten Claude Code '
                'als verbindliche visuelle Spezifikation — analog zu UX-Wireframes in '
                'professionellen Entwicklungsteams.',
                LB2
            ),
            (
                'Verbale Spezifikation: Für komplexe interaktive Features ohne visuelle '
                'Vorlage (z. B. Rotationsplanung Gantt mit Drag & Drop) wurden Anforderungen '
                'im Dialog mit Claude Code präzisiert: «Ich brauche ein Gantt-Diagramm, wo '
                'ich Rotationen verschieben und in der Länge anpassen kann, mit '
                'Konflikterkennung bei Doppelbelegungen.» Claude Code entwarf daraufhin '
                'eigenständig das visuelle Design, das Koordinatensystem und die '
                'Interaktionslogik.',
                LB2
            ),
            # Layer 2
            (
                'Schritt 2 – Implementierung durch Claude Code: Basierend auf der Spezifikation '
                'generierte Claude Code vollständigen, produktionsreifen Code (TypeScript/React '
                'Frontend + C#/ASP.NET Core Backend) inklusive Typsystem, Tests und '
                'Architekturdokumentation.',
                LB
            ),
            # Layer 3
            (
                'Schritt 3 – Evaluation & Konversationelle Optimierung: Der '
                'Projektverantwortliche evaluierte jedes Feature direkt im Browser. '
                'Verbesserungen wurden im Gespräch kommuniziert und sofort umgesetzt — '
                'typischerweise 3–15 Iterationen pro Feature. Dieser Prozess ersetzte '
                'formelle Code Reviews durch direkte UX-Feedback-Schleifen: «Das Badge '
                'ist zu klein», «Die Sidebar braucht mehr Abstand», «Der Heute-Button '
                'fehlt» → Claude Code passt an → Iwo evaluiert → nächste Runde.',
                LB
            ),
            (
                'Konversationelle Optimierung am Beispiel Gantt-Diagramm: Das '
                'Rotationsplanungs-Gantt durchlief ca. 15 Feedback-Runden: Farb-Kontrast '
                'der Balken, Breite der Drag-Handles, Scroll-Synchronisation von Header '
                'und Body, AP-Badge-Position im Header, Lehrzeit-Beschränkung '
                '(Balken nicht über Lehrbeginn/-ende ziehbar), Heute-Button, '
                'zweite AP-zentrierte Gegenansicht. Das Endresultat ist das Produkt '
                'aus KI-generiertem Design-Entwurf und iterativer menschlicher Bewertung '
                '— keines von beidem allein hätte das Ergebnis erzeugt.',
                LB2
            ),
            # Separator
            (
                'Die nachfolgenden Phasen beschreiben die Einführungs- und '
                'Validierungsstrategie für den produktiven Einsatz:',
                NRM
            ),
        ]

        insert_before(phase1_para, new_content)
        print(f"OK: Inserted {len(new_content)} methodology paragraphs before Phase 1 bullet in 2.4")
    else:
        print("SKIP: SDD content already present in 2.4")

    # -------------------------------------------------------------------------
    # 2. Add R54, R55 to Literaturverzeichnis (after R53)
    # -------------------------------------------------------------------------
    if r53_para is not None:
        new_refs = [
            (
                '[R54] FHNW – Fachhochschule Nordwestschweiz (2026). FHNW Styleguide V5. '
                'web.fhnw.ch/fhnw-styleguide-v5/ (abgerufen Juni 2026).',
                LB
            ),
            (
                '[R55] Axisbits (2024). Die 7 Phasen der Softwareentwicklung. '
                'axisbits.ch/blog/phasen-der-softwareentwicklung (abgerufen Juni 2026).',
                LB
            ),
        ]
        insert_after(r53_para, new_refs)
        print("OK: Inserted R54, R55 after R53 in Literaturverzeichnis")
    else:
        print("WARNING: R53 not found — R54/R55 NOT inserted")

    doc.save(DOCX_PATH)
    print(f"\nSaved: {DOCX_PATH}")


if __name__ == '__main__':
    main()
