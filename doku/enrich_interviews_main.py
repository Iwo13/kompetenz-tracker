"""
enrich_interviews_main.py
Integriert die Interview-Erkenntnisse in die Hauptthesis an drei Stellen:
  1. Kap. 2.4.1 – Traceability-Tabelle (Interview → Anforderung)
  2. Kap. 3.4   – Synthese der durchgeführten Interviews
  3. Kap. 4.4   – Interview-basierte Weiterentwicklung (Ausblick)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DOC = r"doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx"
doc = Document(DOC)
paras = doc.paragraphs

# ── Idempotenz-Schutz ──────────────────────────────────────────────
GUARD_241 = "Anforderungsherleitung aus Stakeholder-Interviews"
GUARD_34  = "Durchgeführte Stakeholder-Interviews"
GUARD_44  = "Interview-basierte Weiterentwicklung"

def already_present(guard):
    return any(guard in p.text for p in paras)

# ── Hilfsfunktionen ────────────────────────────────────────────────
def make_para(style_name, text='', bold=False):
    """Erstellt einen neuen Paragraph (nicht im Dokument eingefügt)."""
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    pStyle = OxmlElement('w:pStyle')
    pStyle.set(qn('w:val'), style_name)
    pPr.append(pStyle)
    p.append(pPr)
    if text:
        r = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        if bold:
            b = OxmlElement('w:b')
            rPr.append(b)
        r.append(rPr)
        t = OxmlElement('w:t')
        t.text = text
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r.append(t)
        p.append(r)
    return p

def make_list_para(text, level='ListParagraph'):
    """Erstellt einen Aufzählungsparagraph."""
    return make_para(level, text)

def find_para(search_text):
    """Findet den ersten Paragraph der den gesuchten Text enthält."""
    for p in paras:
        if search_text in p.text:
            return p
    return None

def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def bold_cell(cell, text):
    p = cell.paragraphs[0]
    p.clear()
    run = p.add_run(text)
    run.bold = True

def fill_cell(cell, text):
    p = cell.paragraphs[0]
    p.clear()
    p.add_run(text)


# ════════════════════════════════════════════════════════════════════
# 1. KAP. 2.4.1 — Traceability-Paragraph + Tabelle
# ════════════════════════════════════════════════════════════════════
if already_present(GUARD_241):
    print("[2.4.1] bereits vorhanden — übersprungen")
else:
    ref = find_para("Rollenkürzel: BB")
    if not ref:
        print("[2.4.1] FEHLER: Rollenkürzel-Paragraph nicht gefunden")
    else:
        # Traceability-Einführungstext
        intro_text = (
            "Anforderungsherleitung aus Stakeholder-Interviews: "
            "Die Anforderungen wurden in einem empathischen Requirements-Engineering-Prozess "
            "(vgl. Anhang B, Methodik nach Eichholzer) aus vier strukturierten Stakeholder-Interviews "
            "empirisch hergeleitet. Tabelle 1 zeigt die direkten Bezüge zwischen den "
            "Interview-Erkenntnissen und den abgeleiteten Anforderungen. Phase-2-Anforderungen "
            "(W1–W4) sind explizit als zurückgestellt markiert."
        )
        intro_p = make_para('Normal', intro_text)

        # Traceability-Tabelle erstellen (temporär am Ende des Dokuments)
        tbl = doc.add_table(rows=4, cols=4)
        tbl.style = 'Table Grid'

        HEADER_BG = 'BDD7EE'   # Blau-grau (FHNW-nah)
        L_BG      = 'EBF3FB'   # Hellblau Lernende
        PB_BG     = 'EDF7EE'   # Hellgrün Praxisbildner
        AV_BG     = 'FFF2CC'   # Hellgelb AV

        # Header
        headers = ['Persona / Interviewpartner',
                   'Schlüsselerkenntnis (Interview)',
                   'Anforderung(en)',
                   'Phase']
        for i, h in enumerate(headers):
            set_cell_bg(tbl.rows[0].cells[i], HEADER_BG)
            bold_cell(tbl.rows[0].cells[i], h)

        # Zeile 2: Lernende
        row = tbl.rows[1]
        set_cell_bg(row.cells[0], L_BG)
        set_cell_bg(row.cells[1], L_BG)
        set_cell_bg(row.cells[2], L_BG)
        set_cell_bg(row.cells[3], L_BG)
        fill_cell(row.cells[0],
            'Heinz/Viktor – Lernende\n(Altin, Lorin)')
        fill_cell(row.cells[1],
            'Kein HK-Überblick seit Jahren; '
            'KI-Vorschlag willkommen wenn optional; '
            'Push-Erinnerungen als Hauptwunsch; '
            'nur fachliche Doku (keine Reflexion)')
        fill_cell(row.cells[2],
            'F03, F04, F07, F08, F09, F10, F11;\n'
            'W2 (Kompetenzkarte)\n'
            'Push-Benachrichtigungen → Phase 2')
        fill_cell(row.cells[3], 'Phase 1 / 2')

        # Zeile 3: Praxisbildner
        row = tbl.rows[2]
        for c in row.cells:
            set_cell_bg(c, PB_BG)
        fill_cell(row.cells[0],
            'Michi – Praxisbildner\n(Tobias Dummann)')
        fill_cell(row.cells[1],
            'Kein aktives Tracking («gar nicht»); '
            'KI von Text → Zahl, nie umgekehrt; '
            '«bequem und elegant» als Adoption-Bedingung; '
            'Praxisbildner schreibt Texte selbst')
        fill_cell(row.cells[2],
            'F08 (KI Bloom), F09 (Bestätigen),\n'
            'F12 (manuelle Beurteilung);\n'
            'ADR-007 (Merge-Strategie Text→Zahl)')
        fill_cell(row.cells[3], 'Phase 1 / 2')

        # Zeile 4: AV
        row = tbl.rows[3]
        for c in row.cells:
            set_cell_bg(c, AV_BG)
        fill_cell(row.cells[0],
            'KUI – Ausbildungsverantwortliche\n(Iwo Kuhn)')
        fill_cell(row.cells[1],
            '«Keine Chance auf Überblick» (quant. Aussagen heute unmöglich); '
            'Transparenz → Qualitätserhöhung als Hauptnutzen; '
            'Zugriffstrennung nicht verhandelbar (DSG)')
        fill_cell(row.cells[2],
            'F03 (Übersicht), F22/F23 (RBAC);\n'
            'AV-Aggregat-Dashboard → Phase 2\n'
            'Bildungsbericht-Export → Phase 2')
        fill_cell(row.cells[3], 'Phase 1 / 2')

        # Tabelle nach Intro-Paragraph einfügen:
        # Reihenfolge (addnext = LIFO → zuerst Tabelle, dann Intro-Text)
        ref._p.addnext(tbl._tbl)
        ref._p.addnext(intro_p)

        print("[2.4.1] Traceability-Paragraph + Tabelle eingefügt")


# ════════════════════════════════════════════════════════════════════
# 2. KAP. 3.4 — Synthese der durchgeführten Interviews
# ════════════════════════════════════════════════════════════════════
if already_present(GUARD_34):
    print("[3.4]   bereits vorhanden — übersprungen")
else:
    # Einfügepunkt: direkt VOR dem 3.5-Heading
    ref35 = find_para("3.5  Messung")
    if not ref35:
        print("[3.4] FEHLER: 3.5-Heading nicht gefunden")
    else:
        # Neue Inhalte (werden per addprevious in VORWÄRTS-Reihenfolge eingefügt)
        elements = []

        def add_el(style, text='', bold=False):
            elements.append(make_para(style, text, bold))

        # Titel-Bullet
        elements.append(make_para(
            'ListBullet',
            'Durchgeführte Stakeholder-Interviews — Ergebnisübersicht (26. Juni 2026):'))

        # 4 Sub-Bullets
        elements.append(make_para(
            'ListBullet2',
            'Altin (Lernende, Persona Heinz/Viktor, 17 Min.): '
            'Kein HK-Überblick seit 2 Jahren — Bewusstsein entstand erst durch das Interview. '
            'Hauptwunsch: Push-Erinnerungen («damit nichts vergessen geht»). '
            'KI-Vorschlag akzeptiert, Datenschutz (lokale KI) zentrale Bedingung. '
            'Persona KUI teilweise bestätigt — weniger frustriert als erwartet.'))

        elements.append(make_para(
            'ListBullet2',
            'Lorin (Lernende, Persona Heinz/Viktor, 20 Min.): '
            'Kaum eigenständige Dokumentation («ich kann, ich mache einfach momentan nicht»). '
            'Checkbox-System für alle HK gewünscht (zweischneidig: Klarheit vs. Stress). '
            'KI sehr willkommen, wenn optional und sachlich-direkt. '
            'Informelles Wissen (Shortcuts, Praxistricks) nicht im Bildungsplan abgebildet — Raum dafür fehlt.'))

        elements.append(make_para(
            'ListBullet2',
            'Tobias (Praxisbildner, Persona Michi, 17 Min.): '
            '«Jetzt wirst du wahrscheinlich nicht gerne hören, aber gar nicht» (kein aktives Tracking). '
            'Faustregel statt Bloom: «Wie lange kann der Lernende alleine am Service Desk stehen?» '
            'KI-Anforderung präzise: von Text → Zahl schliessen, nie umgekehrt — '
            'wohlwollend geschriebene Texte dürfen nicht zu tiefen Bewertungen führen. '
            'Adoption-Bedingung: «bequem und elegant», sonst kein Einsatz.'))

        elements.append(make_para(
            'ListBullet2',
            'Iwo Kuhn (Berufsbildner/AV, Persona KUI, schriftlich): '
            '«Keine Chance [auf Überblick], höchstens als sehr grobe Schätzung ohne Basis» '
            '(zu quantitativen HK-Aussagen). '
            'DSG-Konformität bereits gegeben; nicht verhandelbar: Zugriffstrennung '
            '(Lernende sehen keine Daten anderer). '
            'Wichtigster Nutzen: Transparenz, die zur Qualitätserhöhung führt.'))

        # Synthese-Paragraph
        elements.append(make_para(
            'Normal',
            'Übergreifende Erkenntnis: Alle vier Interviewpartner bestätigten, dass kein strukturiertes '
            'digitales Tracking der Handlungskompetenzen existiert — weder auf Lernenden- noch auf '
            'Praxisbildner- oder AV-Seite. Die Interviews validierten die definierten Personas '
            'teilweise (nicht vollständig): Alle Beteiligten erwiesen sich als pragmatischer und '
            'weniger frustriert als in den Persona-Hypothesen angenommen. Die konkreten Erkenntnisse '
            'flossen direkt in den Anforderungskatalog (vgl. Kap. 2.4.1, Traceability-Tabelle) '
            'und in die Priorisierung Phase 1 vs. Phase 2 ein.'))

        # Vor 3.5-Heading einfügen — addprevious in VORWÄRTS-Reihenfolge
        for el in elements:
            ref35._p.addprevious(el)

        print("[3.4]   Interview-Synthese eingefügt")


# ════════════════════════════════════════════════════════════════════
# 3. KAP. 4.4 — Interview-basierte Weiterentwicklung
# ════════════════════════════════════════════════════════════════════
if already_present(GUARD_44):
    print("[4.4]   bereits vorhanden — übersprungen")
else:
    # Einfügepunkt: nach dem letzten Forschungsempfehlungs-Bullet
    ref_last = find_para("Validierung GenAI-Forschungsagenda")
    if not ref_last:
        # Fallback: suche letztes Bullet unter 4.4
        ref_last = find_para("A/B-Test: KI-Vorschlag vs.")
    if not ref_last:
        print("[4.4] FEHLER: Einfügepunkt nicht gefunden")
    else:
        elements = []

        # Neuer Hauptpunkt
        elements.append(make_para(
            'ListBullet',
            'Interview-basierte Weiterentwicklung (aus Benutzerforschung Juni 2026):'))

        elements.append(make_para(
            'ListBullet2',
            'Push-Benachrichtigungen für Lernende: konfigurierbare Erinnerungen '
            '(wöchentlich / alle 2 Wochen) direkt in der App — '
            'Hauptwunsch beider Lernenden-Interviews (Altin: «damit nichts vergessen geht»).'))

        elements.append(make_para(
            'ListBullet2',
            'AV-Übersichts-Dashboard: aggregierter HK-Fortschritt aller Lernenden auf einen Blick '
            'für den Ausbildungsverantwortlichen — '
            'zentrales Bedürfnis aus dem BB-Interview '
            '(Iwo: «Keine Chance auf Überblick, höchstens grobe Schätzung»).'))

        elements.append(make_para(
            'ListBullet2',
            'Reflexionspflicht bei KI-Vorschlag: KI-Bewertung erst bestätigbar, '
            'wenn ein eigener Kommentar (Mindestlänge) erfasst ist — '
            'pädagogisches Gegensteuer zum Risiko unreflektierter KI-Übernahme '
            '(BB-Interview: «Lernende speichern, ohne eigene Gedanken»).'))

        elements.append(make_para(
            'ListBullet2',
            'Raum für informelle Lernmomente: Freitext-Tags für Praxistricks, Shortcuts '
            'und Wissen ausserhalb des Bildungsplans — '
            'Bedürfnis aus dem Lernenden-Interview '
            '(Lorin: informelles Wissen ist wertvoll, wird aber nicht erfasst).'))

        elements.append(make_para(
            'ListBullet2',
            'Rotationsplanung mit Interessenprofil: Lernende können Präferenzen für '
            'nächste Ausbildungsplätze hinterlegen; Rotationsplanung berücksichtigt '
            'Kompetenzlücken und Interessen — '
            'Tobias: Informationsdilemma (viele Infos gewünscht vs. unvoreingenommenes Kennenlernen); '
            'beide Lernende: Ausbildungsplatz-Wahl bewusst auf Basis von Kompetenzlücken.'))

        # Nach ref_last einfügen (addnext LIFO → zuerst letztes Element)
        for el in reversed(elements):
            ref_last._p.addnext(el)

        print("[4.4]   Weiterentwicklungs-Bullets eingefügt")


# ── Speichern ────────────────────────────────────────────────────────
doc.save(DOC)
print(f"\nGespeichert: {DOC}")
