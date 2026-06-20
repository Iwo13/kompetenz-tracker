"""
Enriches KI5 section with:
1. Datenschutzentscheid (4 Massnahmen) → FHNW DSG + Danner EU AI Act
2. Transparency Mouseover → EU AI Act + DSG + Glickman
3. Human-AI Feedback Loop risk + countermeasures → Glickman + Danner
4. Adds references R51, R52, R53 to Literaturverzeichnis

python-docx conventions:
- addnext + reversed(items) for insert-after → forward order
- List Bullet 2 = 'Aufzhlungszeichen2'
"""
import sys
from xml.sax.saxutils import escape as xml_escape
from docx import Document
from docx.oxml.ns import qn
from lxml import etree
import copy

DOCX_PATH = r'doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'


def make_xml_para(text: str, style_id: str) -> etree._Element:
    """Create a bare <w:p> element with given text and style."""
    p = etree.fromstring(
        f'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'  <w:pPr><w:pStyle w:val="{style_id}"/></w:pPr>'
        f'  <w:r><w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r>'
        f'</w:p>'
    )
    return p


def insert_after(ref_para, items):
    """Insert paragraphs after ref_para in forward order (addnext + reversed)."""
    ref_p = ref_para._p
    for text, style in reversed(items):
        ref_p.addnext(make_xml_para(text, style))


def fix_para_text(para, old_fragment, new_fragment):
    """Robust text replacement across split runs."""
    t_elems = list(para._p.iter(qn('w:t')))
    combined = ''.join((t.text or '') for t in t_elems)
    if old_fragment not in combined:
        return False
    t_elems[0].text = combined.replace(old_fragment, new_fragment, 1)
    for t in t_elems[1:]:
        t.text = ''
    return True


def main():
    doc = Document(DOCX_PATH)
    paras = doc.paragraphs

    # -------------------------------------------------------------------------
    # 1. Find anchor paragraphs
    # -------------------------------------------------------------------------
    ki5_human_ctrl_para = None   # "Menschliche Kontrolle (Human-in-the-Loop)" in KI5
    ki5_header_para = None       # "KI 5: Dokumentenbeurteilung" bullet
    litverz_last_para = None     # last reference paragraph before end of Literaturverzeichnis
    litverz_r50_para = None      # R50 paragraph to insert after

    in_ki5_block = False
    for i, para in enumerate(paras):
        txt = para.text.strip()

        # KI 5 header
        if 'KI 5:' in txt and 'Dokumentenbeurteilung' in txt:
            ki5_header_para = para
            in_ki5_block = True

        # Menschliche Kontrolle sub-bullet inside KI5
        if in_ki5_block and 'Menschliche Kontrolle' in txt and 'Human-in-the-Loop' in txt:
            ki5_human_ctrl_para = para

        # Stop scanning KI5 at LiteLLM bullet
        if in_ki5_block and 'LiteLLM' in txt:
            in_ki5_block = False

        # Literaturverzeichnis: find R50
        if '[R50]' in txt:
            litverz_r50_para = para

    if ki5_human_ctrl_para is None:
        print("ERROR: Could not find 'Menschliche Kontrolle (Human-in-the-Loop)' para in KI5")
        sys.exit(1)
    if ki5_header_para is None:
        print("ERROR: Could not find KI 5 header para")
        sys.exit(1)

    print(f"Found KI5 header at: {ki5_header_para.text[:80]}")
    print(f"Found KI5 Menschliche Kontrolle at: {ki5_human_ctrl_para.text[:80]}")
    if litverz_r50_para:
        print(f"Found R50 at: {litverz_r50_para.text[:80]}")

    # -------------------------------------------------------------------------
    # 2. Extend KI5 header reference list  (add [R51]; [R52]; [R53])
    # -------------------------------------------------------------------------
    ki5_full = ki5_header_para.text
    if '[R51]' not in ki5_full:
        fixed = fix_para_text(
            ki5_header_para,
            'vgl. [R10] Abrahamsson et al. 2025',
            'vgl. [R10] Abrahamsson et al. 2025; [R51] Glickman & Sharot 2025; [R52] Danner 2026; [R53] FHNW Datenschutzrichtlinie 2024'
        )
        if fixed:
            print("OK: Extended KI5 header references to R51/R52/R53")
        else:
            # header may not have that exact text; just append
            t_elems = list(ki5_header_para._p.iter(qn('w:t')))
            if t_elems:
                t_elems[-1].text = (t_elems[-1].text or '') + '  vgl. [R51] Glickman & Sharot 2025; [R52] Danner 2026; [R53] FHNW Datenschutzrichtlinie 2024'
                print("OK: Appended R51/R52/R53 to KI5 header (no existing vgl. anchor)")

    # -------------------------------------------------------------------------
    # 3. Insert 3 new sub-bullets AFTER "Menschliche Kontrolle" paragraph
    # -------------------------------------------------------------------------
    LB2 = 'Aufzhlungszeichen2'

    new_bullets = [
        # --- Datenschutzentscheid ---
        (
            'Datenschutzentscheid – Privatsphäreschutz beim KI-Prozess: '
            'Gemäss FHNW Datenschutzrichtlinie §3c (Verhältnismässigkeit: «so wenig wie möglich, '
            'so viel wie notwendig») und Privacy by Design (Danner 2026 [R52], Folie 15) wurden vier '
            'technische Massnahmen implementiert: (1) Dokumenttitel und -beschreibung werden nicht '
            'an die KI übermittelt; (2) Word-Überschriften (Heading-Paragraphen) werden beim '
            'Extrahieren gefiltert; (3) Word-Kopfzeilen (HeaderPart) werden nie ausgelesen; '
            '(4) Der System-Prompt weist die KI explizit an, keine Personennamen zu verwenden. '
            'Begründung: Für die Bloom-Bewertung ist ausschliesslich der Fachinhalt relevant – '
            'personenbezogene Angaben sind weder notwendig noch für das Beurteilungsziel geeignet '
            '(Zweckbindungsprinzip, DSG Art. 6; FHNW Datenschutzrichtlinie [R53] §3a).',
            LB2
        ),
        # --- Transparency Mouseover ---
        (
            'Transparenz-Hinweis (Mouseover-Tooltip): Die Benutzeroberfläche zeigt beim '
            'KI-Bewertungs-Button einen Mouseover-Tooltip: «Diese Bewertung erfolgt durch '
            'GPT-Modelle, betrieben im Azure-Tenant der FHNW. Es werden nur leere Felder '
            'automatisch gefüllt.» Diese Umsetzung erfüllt drei übereinanderliegende Anforderungen: '
            '(a) EU AI Act (begrenztes Risiko, Art. 50): «KI-Systeme mit geringem Risiko erfordern '
            'Transparenzpflichten, wie die Kennzeichnung von KI-Interaktionen für Nutzer» '
            '(Danner 2026 [R52], Folie 35); (b) Informationspflichten nach DSG Art. 19 und FHNW '
            'Datenschutzrichtlinie §6: Bei Bekanntgabe von Personendaten an Dritte (Azure als '
            'Auftragsbearbeiter) sind Bearbeitungszweck und Empfänger mitzuteilen; '
            '(c) Nutzerakzeptanz und kritische Distanz: Glickman & Sharot (2025 [R51]) zeigen, '
            'dass Nutzer, die wissen, dass sie mit einer KI interagieren, stärker dazu neigen, '
            'KI-Urteile zu übernehmen – transparente Kennzeichnung ermöglicht informierte, '
            'kritische Auseinandersetzung statt blinder Deference.',
            LB2
        ),
        # --- Human-AI Feedback Loop ---
        (
            'Risiko: Human-AI Feedback Loops (Gegenmassnahmen): Glickman & Sharot (2025 [R51]) '
            'belegen in einer Nature-Studie, dass wiederholte Human-AI-Interaktionen menschliche '
            'Urteile kumulativ verzerren («Schneeballeffekt»): KI-Modelle, die auf leicht verzerrten '
            'Menschendaten trainiert sind, verstärken diese Verzerrung (53 % → 65 % in '
            'Emotionsbewertungsaufgaben), und Nutzer übernehmen die KI-Einschätzungen, ohne sich '
            'der Beeinflussung bewusst zu sein. Danner (2026 [R52], Folie 25) listet '
            '«Verstärkungseffekte durch Feedback Loops» explizit als ethische Herausforderung bei '
            'KI-Systemen. Der HK-Tracker adressiert dieses Risiko durch drei Gegenmassnahmen: '
            '(1) Merge-Strategie: KI befüllt ausschliesslich leere Felder – manuell gesetzte '
            'Bloom-Bewertungen des Berufsbildners bleiben unverändert; (2) Konservativer '
            'System-Prompt: Die KI wird angewiesen, bei Unsicherheit die niedrigere Bloom-Stufe '
            'zu bevorzugen; (3) Mandatory Human-in-the-Loop: Jede KI-Bewertung muss vom '
            'Berufsbildner explizit bestätigt werden, bevor sie gespeichert wird.',
            LB2
        ),
    ]

    insert_after(ki5_human_ctrl_para, new_bullets)
    print("OK: Inserted 3 new sub-bullets after 'Menschliche Kontrolle' in KI5")

    # -------------------------------------------------------------------------
    # 4. Add R51, R52, R53 to Literaturverzeichnis (after R50)
    # -------------------------------------------------------------------------
    LB = 'Aufzhlungszeichen'

    new_refs = [
        (
            '[R51] Glickman, M. & Sharot, T. (2025). How human–AI feedback loops alter human '
            'perceptual, emotional and social judgements. Nature Human Behaviour, 9, 345–359. '
            'https://doi.org/10.1038/s41562-024-02077-2',
            LB
        ),
        (
            '[R52] Danner, C. (2026). Rechtliche Aspekte KI. Vorlesungsfolien CAS Artificial '
            'Intelligence for Software Engineering (AI-SE), FHNW, 18. Juni 2026 (ONLAW GmbH).',
            LB
        ),
        (
            '[R53] FHNW – Fachhochschule Nordwestschweiz (2024). Richtlinie zum Datenschutz an der '
            'FHNW. Generalsekretariat, gültig ab 21. Mai 2024.',
            LB
        ),
    ]

    if litverz_r50_para is not None:
        insert_after(litverz_r50_para, new_refs)
        print("OK: Inserted R51, R52, R53 after R50 in Literaturverzeichnis")
    else:
        print("WARNING: R50 paragraph not found – references R51–R53 NOT inserted in Literaturverzeichnis")
        print("         Please add them manually.")

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------
    doc.save(DOCX_PATH)
    print(f"\nSaved: {DOCX_PATH}")


if __name__ == '__main__':
    main()
