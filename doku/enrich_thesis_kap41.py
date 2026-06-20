"""
Enriches Kapitel 4.1 "Erreichte Ergebnisse und Zielerreichung".

Strategy:
  - Remove [Vorgabe] and existing bullet placeholders (paras 498-515)
  - Insert new structured content with H3 sub-sections
  - Final TODO marker for pilot results (August 2026)
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


NEW_CONTENT = [
    # --- Intro ---
    ('Der HK-Tracker hat bis zum Abgabezeitpunkt alle Entwicklungsziele der Phase 1 '
     'vollständig erreicht. Eine funktionsfähige Webapplikation steht für den internen '
     'Betrieb bereit; die KI-Integration (Phase 2) ist architekturseitig abgeschlossen '
     'und wartet auf die betriebliche Freigabe durch die FHNW IT (Azure OpenAI API-Key, '
     'MSAL-Authentifizierung). Die nachfolgenden Abschnitte dokumentieren die Ergebnisse '
     'nach Stand der Abgabe (20. Juni 2026).', NRM),

    # --- 4.1.1 ---
    ('4.1.1  Funktionsfähige Webapplikation (Phase 1, abgeschlossen)', H3),

    ('Alle vier Kernmodule der Phase 1 sind implementiert, in Betrieb genommen und durch '
     'konversationelle Optimierung im Browser verfeinert worden '
     '(SDD-Methodik, vgl. Kap. 2.4 und ADR-006, Anhang C):', NRM),

    ('HK-Tracking (Bloom-Taxonomie K1–K6): manuelle Erfassung pro Lernenden und '
     'Handlungskompetenz; farbkodierte Fortschrittsanzeige nach Bloom-Stufe ✓', LB),
    ('Rotationsplanung (Gantt-Ansicht): Visualisierung aller Lernenden-Rotationen '
     'über Ausbildungsplätze; responsiv, für alle Bildschirmgrössen optimiert ✓', LB),
    ('Ausbildungsplatz-Abdeckungsanalyse: Auswertung, welche APs welche HKs abdecken; '
     'Lückenidentifikation für BBG Art. 20-Pflichten des Berufsbildners ✓', LB),
    ('Dokumentenverwaltung + KI-Vorbeurteilung: Upload, Kategorisierung, '
     'Metadatenpflege; KI-Bewertungs-UI vollständig implementiert (Aktivierung '
     'ausstehend, vgl. 4.1.3) ✓', LB),

    ('Das Frontend (React 19 + TypeScript strict + Tailwind CSS / FHNW-Design-Tokens) '
     'und das Backend (ASP.NET Core 8, Clean Architecture: HK.Domain / HK.Application / '
     'HK.Infrastructure / HK.API) kommunizieren über eine REST-API mit EF Core 8 und '
     'SQL Server Express. Alle Datenbankmigrationen sind idempotent; '
     'das Deployment auf Azure App Service + Azure SQL Database ist architektonisch '
     'vorbereitet (ADR-002, ADR-005, Anhang C).', NRM),

    # --- 4.1.2 ---
    ('4.1.2  Validierung der SDD-Methodik (Claude Code als Entwicklungspartner)', H3),

    ('Der wichtigste nicht-technische Befund dieser Arbeit ist die Validierung des '
     'SDD-Ansatzes: Eine Vollstack-Webapplikation (React 19 + ASP.NET Core 8) wurde '
     'von einer Person ohne aktive Programmierkenntnisse vollständig entwickelt — '
     'ausschliesslich durch konversationellen Einsatz von Claude Code '
     '(vgl. Kap. 2.4, ADR-006, Anhang C).', NRM),

    ('Entwicklungszeitraum Phase 1: März–Juni 2026 (ca. 4 Monate, Teilzeit neben '
     'Berufsbildungsverantwortung)', LB),
    ('Toolkosten Claude Pro: CHF ~20/Monat (vollständig von FHNW erstattet)', LB),
    ('Iterationen pro Feature: 3–15 konversationelle Optimierungsschritte im Browser', LB),
    ('Qualitätssicherung: TypeScript strict mode + ESLint pre-commit — '
     'kein manuelles Code-Review erforderlich', LB),
    ('Projektkontinuität: CLAUDE.md + persistentes Memory-System sicherte Kontext '
     'über mehr als 20 Entwicklungssitzungen', LB),

    ('Dies bestätigt die zentrale These dieser Arbeit: KI ist in diesem Projekt '
     'kein Effizienzsteigerungs-Werkzeug, sondern eine Existenzvoraussetzung — '
     '«sine qua non» (vgl. Kap. 2.2, KI 1). Der 3-Schritt-SDD-Prozess '
     '(Spezifikation → KI-Implementierung → konversationelle Optimierung) '
     'erwies sich als reproduzierbar und auf alle Funktionsmodule übertragbar.', NRM),

    # --- 4.1.3 ---
    ('4.1.3  KI-Architektur (Phase 2, code-complete — Livegang ausstehend)', H3),

    ('Die KI-Evaluation (KI 5, Dokumentenbeurteilung) ist vollständig implementiert '
     'und datenschutzkonform spezifiziert. Drei Architekturentscheide sind '
     'abgeschlossen und in Anhang C dokumentiert (ADR-003, ADR-007):', NRM),

    ('AiEvaluationService.cs (HK.API): GPT-4o-Aufruf über Azure OpenAI SDK; '
     'System-Prompt für Bloom-Erkennung auf Stufe K1–K6; strukturierte '
     'JSON-Antwort mit Begründungstext', LB),
    ('Merge-Strategie (ADR-007, Accepted): KI befüllt ausschliesslich leere Felder — '
     'Feedback-Loop-Risiko nach Glickman & Sharot (2025, [R51]) '
     'technisch mitigiert', LB),
    ('Datenschutz by Design: Azure OpenAI FHNW-Tenant, EU Data Boundary, '
     'kein Training auf Kundendaten (FHNW Datenschutzrichtlinie §6 [R53])', LB),
    ('Transparenz-UI: Mouseover-Tooltip «KI-Vorschlag — betrieben im Azure-Tenant '
     'der FHNW» (EU AI Act Transparenzpflicht [R52])', LB),
    ('Konservativer System-Prompt: bei Unsicherheit niedrigere Bloom-Stufe — '
     'verhindert systematische Über-Bewertung', LB),

    ('Ausstehend bis Livegang (Phase 2): Azure OpenAI API-Key (FHNW IT-Freigabe), '
     'MSAL-Authentifizierung (Azure AD Tenant-Registrierung), '
     'Deployment Azure App Service.', NRM),

    # --- 4.1.4 ---
    ('4.1.4  Zielerreichung — Stand 20. Juni 2026', H3),

    ('Die folgende Übersicht bewertet den Zielerreichungsgrad zum Zeitpunkt '
     'der Abgabe (✓ = vollständig; ◑ = code-complete, Livegang ausstehend; '
     '○ = in Planung):', NRM),

    ('Projektziel Phase 1 — Funktionsfähige Webapplikation: ✓', LB),
    ('KI-Projektziel 1 — Bloom-Erkennung via Azure OpenAI (KI 5): '
     'Code-complete ◑ / Livegang ausstehend (API-Key)', LB),
    ('KI-Projektziel 2 — Human-in-the-Loop Merge-Strategie: '
     'Vollständig implementiert ✓', LB),
    ('KI-Projektziel 3 — Embedding-Ähnlichkeitssuche (KI 3): '
     'Architekturentscheid getroffen (Azure Cognitive Search), '
     'Implementierung Phase 2 ○', LB),
    ('Dokumentationsziel — ADRs, arc42, Anhang A–C: ✓', LB),
    ('Pilotbetrieb Phase 3 — Early Adopters, Feedback, Auswertung: '
     'geplant Juli–August 2026 ○', LB),

    # --- TODO marker ---
    ('[TODO AUGUST 2026: Pilotphase-Ergebnisse hier einfügen — '
     'tatsächliche Nutzerzahlen ([X] Lernende, [Y] APs), '
     'qualitatives Feedback Berufsbildner, '
     'Bloom-Erkennungsqualität GPT-4o vs. manuell (Konfusionsmatrix), '
     'MSAL-Authentifizierung Status, '
     'Azure App Service Deployment Status]', NRM),
]


def main():
    doc = Document(DOCX_PATH)
    paras = doc.paragraphs

    # Find heading 4.1 and heading 4.2 as boundaries
    h41_para = None
    h42_para = None
    for p in paras:
        t = p.text.strip()
        s = p.style.name
        if ('berschrift2' in s or 'Heading 2' in s) and '4.1' in t and 'Erreichte' in t:
            h41_para = p
        if ('berschrift2' in s or 'Heading 2' in s) and '4.2' in t and h41_para:
            h42_para = p
            break

    if not h41_para:
        print("ERROR: 4.1 heading not found"); sys.exit(1)
    if not h42_para:
        print("ERROR: 4.2 heading not found"); sys.exit(1)

    print(f"4.1 heading: {h41_para.text}")
    print(f"4.2 heading: {h42_para.text}")

    # Collect paras between 4.1 heading and 4.2 heading (exclusive)
    body_el = h41_para._p.getparent()
    all_elems = list(body_el)
    idx_41 = all_elems.index(h41_para._p)
    idx_42 = all_elems.index(h42_para._p)

    to_remove = all_elems[idx_41 + 1 : idx_42]
    print(f"Removing {len(to_remove)} existing paragraphs between 4.1 and 4.2")
    for el in to_remove:
        body_el.remove(el)

    # Insert new content before 4.2 heading
    anchor = h42_para._p
    for text, style in NEW_CONTENT:
        anchor.addprevious(make_para(text, style))

    print(f"Inserted {len(NEW_CONTENT)} paragraphs")

    doc.save(DOCX_PATH)
    print(f"\nSaved: {DOCX_PATH}")


if __name__ == '__main__':
    main()
