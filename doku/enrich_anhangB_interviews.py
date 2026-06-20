"""
Enriches Anhang B with a full stakeholder interview catalog
based on empathetic RE methodology (Eichholzer, CAS AI-SE Tag 04).

Personas from thesis 1.4.1:
  1. Heinz / Viktor — Lernende (Informatik EFZ / ICT-Fachmann EFZ)
  2. Michi — Praxisbildner Softwareentwicklung
  3. KUI  — Ausbildungsverantwortliche

Also updates the TODO in 1.4 to reference Anhang B.
"""
import sys
from xml.sax.saxutils import escape as xml_escape
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree

DOCX_PATH = r'doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx'

# Style IDs (deutsche Word-Installation)
NRM  = 'Standard'
H2   = 'berschrift2'
H3   = 'berschrift3'
LB   = 'Aufzhlungszeichen'
LB2  = 'Aufzhlungszeichen2'


def make_para(text, style_id, bold=False, italic=False):
    """Create a paragraph XML element."""
    b_tag  = '<w:b/>' if bold else ''
    i_tag  = '<w:i/>' if italic else ''
    rpr    = f'<w:rPr>{b_tag}{i_tag}</w:rPr>' if (bold or italic) else ''
    return etree.fromstring(
        f'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:pPr><w:pStyle w:val="{style_id}"/></w:pPr>'
        f'<w:r>{rpr}<w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r>'
        f'</w:p>'
    )


def insert_after(ref_para, items):
    """Insert (text, style) tuples AFTER ref_para in forward order."""
    ref_p = ref_para._p
    for text, style in reversed(items):
        kw = {}
        if isinstance(style, tuple):
            style, *flags = style
            kw['bold']   = 'bold'   in flags
            kw['italic'] = 'italic' in flags
        ref_p.addnext(make_para(text, style, **kw))


def fix_para_text(para, old_fragment, new_text):
    """Replace text content of a paragraph (handles split runs)."""
    t_elems = list(para._p.iter(qn('w:t')))
    combined = ''.join((t.text or '') for t in t_elems)
    if old_fragment not in combined:
        return False
    t_elems[0].text = new_text
    for t in t_elems[1:]:
        t.text = ''
    return True


# =========================================================================
# CONTENT
# =========================================================================

BLOCK_ANHANG_B = [

    # --- B.1 Methodik ---
    ('B.1  Interviewmethodik (empathisches Requirements Engineering)', H2),
    (
        'Die Stakeholder-Interviews folgen dem empathischen RE-Ansatz nach Eichholzer '
        '(CAS AI-SE, Tag 04): offene Fragen, keine Tool-Demos während des Gesprächs, '
        'Fokus auf tatsächliches Verhalten statt hypothetische Präferenzen. '
        'Leitprinzip: «Was machst du, wenn...» — nicht «Würdest du...».',
        NRM
    ),
    ('Rahmenbedingungen:', LB),
    ('Dauer: 30–45 Min. pro Interview, 1:1-Setting (kein Gruppenformat)', LB2),
    ('Aufnahme nur mit explizitem Einverständnis; alternativ handschriftliches Protokoll', LB2),
    ('Keine Bildschirmsharing/Demo des HK-Trackers vor dem Interview (kein Priming)', LB2),
    ('Interviewer hört zu, fragt nach — keine eigenen Meinungen einbringen', LB2),
    ('4-Phasen-Struktur:', LB),
    ('Phase 1 Warm-Up (5 Min.): Vertrauen aufbauen, Kontext erfassen', LB2),
    ('Phase 2 IST-Prozess (10–15 Min.): «Zeig mir, wie du das heute machst»', LB2),
    ('Phase 3 Pain Points (10–15 Min.): Frustrationen, Engpässe, Workarounds', LB2),
    ('Phase 4 Validierung (5–10 Min.): Hypothesen des Entwicklers prüfen (HK-Tracker-Konzept)', LB2),

    # --- B.2 Interviewplan ---
    ('B.2  Interviewplan', H2),
    (
        'Geplante Interviews im Rahmen der Pilotphase (vgl. Kap. 2.4, Phase 3). '
        'Reale Namen werden erst nach Einverständniserklärung eingetragen.',
        NRM
    ),
    ('Interview 1 — Persona Heinz: Lernender Informatik EFZ AppDev, 1. Lehrjahr | Datum: [eintragen] | Status: geplant', LB),
    ('Interview 2 — Persona Viktor: Lernender ICT-Fachmann EFZ, 2. Lehrjahr | Datum: [eintragen] | Status: geplant', LB),
    ('Interview 3 — Persona Michi: Praxisbildner Softwareentwicklung | Datum: [eintragen] | Status: geplant', LB),
    ('Interview 4 — Persona KUI: Ausbildungsverantwortliche Management FHNW | Datum: [eintragen] | Status: geplant', LB),

    # --- B.3 Fragenkatalog ---
    ('B.3  Fragenkatalog', H2),

    # ---- LERNENDE ----
    ('B.3.1  Lernende (Persona Heinz / Viktor)', H3),
    ('Ziel: Verstehen wie Lernende heute Leistungen dokumentieren, welche Transparenzlücken bestehen, und ob eine KI-gestützte Kompetenzbewertung akzeptiert wird.', NRM),

    ('Einstieg & Warm-Up', (LB, 'bold')),
    ('Erzähl mir von deiner Woche hier am Ausbildungsplatz — was hast du zuletzt gebaut oder gelernt?', LB2),
    ('Wie lange bist du schon bei FHNW in der Ausbildung, und welchen Ausbildungsplatz hast du gerade?', LB2),

    ('IST-Prozess: Kompetenzdokumentation heute', (LB, 'bold')),
    ('Wie dokumentierst du aktuell, was du an einem Ausbildungsplatz gelernt hast?', LB2),
    ('Zeig mir, wie du das machen würdest — wenn du jetzt eine Aufgabe abgeschlossen hättest. (Beobachten, nicht erklären lassen)', LB2),
    ('Wie oft machst du das ungefähr — täglich, wöchentlich, gar nicht?', LB2),
    ('Was passiert mit deiner Dokumentation danach — liest die jemand?', LB2),

    ('Pain Points: Frustrationen', (LB, 'bold')),
    ('Was nervt dich am meisten an der Art, wie du heute Leistungen dokumentierst?', LB2),
    ('Hast du schon mal das Gefühl gehabt: «Ich weiss nicht, ob das, was ich gemacht habe, gut genug war»? Erzähl mir davon.', LB2),
    ('Wie erfährst du, welche Kompetenzen du in deiner Lehrzeit noch sammeln musst?', LB2),
    ('Gab es Situationen, wo du das Gefühl hattest, deine Arbeit wurde nicht richtig gesehen oder bewertet?', LB2),
    ('Wie schwierig ist es für dich, den Überblick zu behalten, welche Handlungskompetenzen du schon erreicht hast?', LB2),

    ('Bedürfnisse & Idealzustand', (LB, 'bold')),
    ('Wenn du dir eine App für deine Ausbildung wünschen könntest — welches eine Problem würde sie lösen?', LB2),
    ('Was wäre für dich das Zeichen, dass deine Lehrzeit wirklich gut läuft?', LB2),
    ('Wie wichtig ist es für dich zu wissen, an welchem Ausbildungsplatz du noch welche Kompetenzen sammeln kannst?', LB2),

    ('Validierung: HK-Tracker-Konzept', (LB, 'bold')),
    ('Wenn eine App dir vorschlagen würde, auf welcher Stufe (Erinnern / Verstehen / Anwenden / Analysieren / Entwickeln / Beurteilen) deine Arbeit ist — würdest du das nutzen?', LB2),
    ('Was wäre wichtig, damit du dem KI-Vorschlag vertraust?', LB2),
    ('Wie würdest du dich fühlen, wenn dein Lehrlingsbetreuer genau sieht, welche Kompetenzen du schon hast und welche nicht?', LB2),
    ('Stell dir vor, eine App zeigt dir genau, welche Kompetenzen dir bis zur Lehrabschlussprüfung noch fehlen — was würdest du damit machen?', LB2),

    # ---- BERUFSBILDNER ----
    ('B.3.2  Berufsbildner / Praxisbildner (Persona Michi)', H3),
    ('Ziel: Verstehen wie Berufsbildner heute Bloom-Bewertungen vergeben, wie viel Zeit die Berufsbildungsarbeit beansprucht, und welche Bedingungen für KI-Akzeptanz erfüllt sein müssen.', NRM),

    ('Einstieg & Warm-Up', (LB, 'bold')),
    ('Beschreib mir einen typischen Tag, an dem du sowohl deine eigene IT-Arbeit machst als auch Lernende betreust.', LB2),
    ('Wie viel Prozent deiner Arbeitszeit geht für die Berufsbildung drauf — grob geschätzt?', LB2),

    ('IST-Prozess: Kompetenzbewertung heute', (LB, 'bold')),
    ('Zeig mir, wie du heute eine Kompetenz eines Lernenden dokumentierst — von der Beobachtung bis zum Eintrag.', LB2),
    ('Welche Werkzeuge verwendest du dafür (Word, Excel, Teams, etc.)? Warum genau diese?', LB2),
    ('Wann entscheidest du, ob eine Kompetenz K3 (Anwenden) oder K4 (Analysieren) ist — wie gehst du da vor?', LB2),
    ('Wie planst du, welcher Lernende als nächstes an welchen Ausbildungsplatz rotiert?', LB2),

    ('Pain Points: Frustrationen & Engpässe', (LB, 'bold')),
    ('Was kostet dich am meisten Zeit bei der ganzen Berufsbildungsarbeit — neben der eigentlichen Facharbeit?', LB2),
    ('Wann hast du zuletzt gedacht: «Das ist mir jetzt zu aufwendig, ich lasse das bleiben»? Was war das?', LB2),
    ('Wie sicher bist du, wenn du eine Bloom-Stufe vergibst? Gibt es Situationen, wo du dir nicht sicher bist?', LB2),
    ('Wie erfährst du heute, ob ein Lernender auf Kurs liegt oder ob Kompetenzen fehlen?', LB2),
    ('Gibt es Kompetenzen oder Handlungsbereiche, die systematisch unter dokumentiert sind — einfach weil es zu aufwendig ist?', LB2),

    ('KI-Akzeptanz & Tool-Anforderungen', (LB, 'bold')),
    ('Wenn eine KI für jeden Lernenden-Eintrag einen Bloom-Vorschlag mit Begründung liefert — was müsste erfüllt sein, damit du dem vertraust?', LB2),
    ('Was wäre für dich ein absolutes No-Go bei einem solchen Tool?', LB2),
    ('Wie viele Klicks / Minuten darf ein Eintrag maximal brauchen, damit du das Tool wirklich konsequent nutzt?', LB2),
    ('Wäre es für dich nützlich zu sehen, welche Kompetenzen an deinem Ausbildungsplatz noch kein Lernender nachgewiesen hat?', LB2),

    ('Datenschutz & KI-Transparenz', (LB, 'bold')),
    ('Wie siehst du das: Lernenden-Texte werden zur KI-Analyse an Azure OpenAI (im FHNW-Tenant) gesendet — was geht dir dabei durch den Kopf?', LB2),
    ('Was müsste transparent gemacht werden, damit Lernende und du damit einverstanden seid?', LB2),
    ('Gibt es Informationen über Lernende, die du nicht an ein externes System senden würdest? (Namen, Noten, persönliche Angaben?)', LB2),

    # ---- AUSBILDUNGSVERANTWORTLICHE ----
    ('B.3.3  Ausbildungsverantwortliche (Persona KUI)', H3),
    ('Ziel: Verstehen welche Management-Übersichten fehlen, welche Compliance-Anforderungen nicht verhandelbar sind, und was nötig ist, um das System intern zu empfehlen.', NRM),

    ('Einstieg & Warm-Up', (LB, 'bold')),
    ('Wie erhältst du heute einen Überblick über den Ausbildungsstand aller Lernenden — was schaust du dir wann an?', LB2),
    ('Welche Berichte oder Dokumente musst du regelmässig erstellen, einreichen oder vorlegen?', LB2),

    ('IST-Prozess & Pain Points', (LB, 'bold')),
    ('Welche Information fehlt dir für die Gesamtübersicht, die du heute nur mit grossem Aufwand bekommst?', LB2),
    ('Wann hattest du zuletzt das Gefühl: «Wenn es ein Problem bei einem Lernenden gibt, erfahre ich das zu spät»?', LB2),
    ('Wie rechtfertigst du den Ressourcenaufwand für Berufsbildung gegenüber dem Management?', LB2),
    ('Wie schwierig ist es heute, Aussagen zu machen wie: «X% der Lernenden haben Handlungskompetenz HK4 erreicht»?', LB2),

    ('Compliance, Datenschutz & Audit', (LB, 'bold')),
    ('Welche datenschutzrechtlichen Anforderungen (DSG, interne FHNW-Richtlinien) sind für dich bei einem digitalen System nicht verhandelbar?', LB2),
    ('Wie wichtig ist es für dich, dass das System einen Audit-Trail führt — wer hat wann welche Bewertung gemacht?', LB2),
    ('Was muss für das System dokumentiert sein, damit es bei einem externen Audit (SBFI, Kantonsbehörde) standhält?', LB2),

    ('Tool-Akzeptanz & Empfehlung', (LB, 'bold')),
    ('Was müsste das System können, damit du es in einer Leitungssitzung empfehlen würdest?', LB2),
    ('Wer müsste sonst noch überzeugt werden, bevor das System produktiv eingesetzt werden kann?', LB2),
    ('Welche Risiken siehst du bei der Einführung eines KI-gestützten Beurteilungssystems in der Berufsbildung?', LB2),
    ('Was wäre für dich der wichtigste Nutzen — Zeitersparnis, Qualitätserhöhung oder Transparenz?', LB2),

    # --- B.4 Protokollvorlage ---
    ('B.4  Protokollvorlage (pro Interview)', H2),
    ('Datum / Uhrzeit / Ort: ___________________________________________', LB),
    ('Interviewpartner (Rolle / Persona): ______________________________', LB),
    ('Interviewer: Iwo Kuhn', LB),
    ('Einverständnis Tonaufnahme: ☐ Ja  ☐ Nein — Protokoll handschriftlich / getippt', LB),
    ('Dauer: _________ Min.', LB),
    ('Kontext-Beobachtungen (Umgebung, Stimmung, Auffälligkeiten):', LB),
    ('[Platzhalter]', LB2),
    ('Key Quotes (direkte Zitate, wörtlich):', LB),
    ('[Platzhalter]', LB2),
    ('Key Insights (3–5 wichtigste Erkenntnisse):', LB),
    ('[Platzhalter]', LB2),
    ('Offene Folgefragen / nächste Schritte:', LB),
    ('[Platzhalter]', LB2),
    ('Validierung Persona-Hypothese: ☐ bestätigt  ☐ teilweise  ☐ widerlegt', LB),
    ('Anpassungsbedarf HK-Tracker (Features / UX / Datenschutz):', LB),
    ('[Platzhalter]', LB2),
]


def main():
    doc = Document(DOCX_PATH)
    paras = doc.paragraphs

    # -------------------------------------------------------------------------
    # 1. Find Anhang B heading
    # -------------------------------------------------------------------------
    anhang_b_para = None
    anhang_c_para = None
    todo_14_para  = None

    for para in paras:
        t = para.text.strip()
        if 'Anhang B' in t and 'Stakeholder' in t:
            anhang_b_para = para
        if 'Anhang C' in t and ('Architecture' in t or 'ADR' in t):
            anhang_c_para = para
        if '[TODO: Stakeholder-Interviews durchführen' in t:
            todo_14_para = para

    if anhang_b_para is None:
        print("ERROR: Anhang B heading not found"); sys.exit(1)
    print(f"Found Anhang B: {anhang_b_para.text[:80]}")
    if anhang_c_para:
        print(f"Found Anhang C (insert before): {anhang_c_para.text[:60]}")
    if todo_14_para:
        print(f"Found TODO in 1.4: {todo_14_para.text[:80]}")

    # -------------------------------------------------------------------------
    # 2. Insert catalog BEFORE Anhang C (= after Anhang B content)
    #    Use Anhang C as anchor; insert_before on that
    # -------------------------------------------------------------------------
    if anhang_c_para:
        # Insert all content before Anhang C in forward order (addprevious, no reverse)
        anchor_p = anhang_c_para._p
        for item in BLOCK_ANHANG_B:
            if isinstance(item, tuple) and len(item) == 2:
                text, style = item
                if isinstance(style, tuple):
                    st = style[0]
                    bold   = 'bold'   in style[1:]
                    italic = 'italic' in style[1:]
                else:
                    st = style
                    bold = italic = False
                anchor_p.addprevious(make_para(text, st, bold=bold, italic=italic))
        print(f"OK: Inserted {len(BLOCK_ANHANG_B)} paragraphs into Anhang B")
    else:
        # Fallback: insert after Anhang B heading
        insert_after(anhang_b_para, BLOCK_ANHANG_B)
        print(f"OK: Inserted {len(BLOCK_ANHANG_B)} paragraphs after Anhang B heading (Anhang C not found)")

    # -------------------------------------------------------------------------
    # 3. Update TODO in 1.4 → reference to Anhang B
    # -------------------------------------------------------------------------
    if todo_14_para:
        new_text = (
            'Stakeholder-Interviews geplant für Pilotphase (Juli–August 2026); '
            'Fragenkatalog (3 Persona-Sets, empathische RE-Methodik nach Eichholzer) '
            'und Protokollvorlage: siehe Anhang B. Erkenntnisse fliessen in die '
            'Validierung der Personas (Kap. 1.4.1) und die Validierungsstrategie '
            '(Kap. 2.4, Phase 3) ein.'
        )
        fixed = fix_para_text(
            todo_14_para,
            '[TODO: Stakeholder-Interviews durchführen',
            new_text
        )
        if fixed:
            print("OK: Updated TODO in 1.4 → Anhang B reference")
        else:
            print("WARNING: Could not replace TODO text in 1.4")

    # -------------------------------------------------------------------------
    # Save
    # -------------------------------------------------------------------------
    doc.save(DOCX_PATH)
    print(f"\nSaved: {DOCX_PATH}")
    print(f"Interview catalog: {len([x for x in BLOCK_ANHANG_B if x[1] in (LB, LB2)])} questions/items")


if __name__ == '__main__':
    main()
