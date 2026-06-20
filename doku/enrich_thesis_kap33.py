"""
Enriches Kapitel 3.3 'Demonstration / Proof of Concept':
- Adds phase chronology (Phase 1 → 2 → 3 → 3b → 3c → 4 geplant)
- Each phase: Ziel, Design-Input (Iwo/Mockup vs. Claude), Ergebnis
- Clear attribution: Gantt = Claude-driven design; Screens with Mockup = Iwo-driven
- Inserts AFTER the [Vorgabe] paragraph, BEFORE existing Demo-Szenarien bullets
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
    ref_p = ref_para._p
    for text, style in items:
        ref_p.addprevious(make_para(text, style))


def insert_after(ref_para, items):
    ref_p = ref_para._p
    for text, style in reversed(items):
        ref_p.addnext(make_para(text, style))


def main():
    doc = Document(DOCX_PATH)
    paras = doc.paragraphs

    # --- Find anchors ---
    vorgabe_33   = None   # [Vorgabe] paragraph inside 3.3
    demo_szen1   = None   # "Demo-Szenario 1" bullet

    in_33 = False
    for i, para in enumerate(paras):
        t = para.text.strip()
        if '3.3' in t and ('Demons' in t or 'Proof' in t):
            in_33 = True
        if in_33 and '[Vorgabe]' in t and 'Demonstration' in t:
            vorgabe_33 = para
        if in_33 and 'Demo-Szenario 1' in t and demo_szen1 is None:
            demo_szen1 = para
        if in_33 and t.startswith('3.4'):
            break

    anchor = demo_szen1 if demo_szen1 else None
    if anchor is None:
        # fallback: insert after Vorgabe
        anchor = vorgabe_33
    if anchor is None:
        print("ERROR: Could not find anchor in 3.3"); sys.exit(1)

    print(f"Anchor 3.3: {anchor.text[:80]}")

    # -------------------------------------------------------------------------
    # Build phase chronology
    # -------------------------------------------------------------------------
    phase_content = [
        # --- Intro ---
        (
            'Der HK-Tracker wurde in fünf abgeschlossenen Entwicklungsphasen realisiert, '
            'die dem 7-Phasen-Modell der Softwareentwicklung [R55] folgen — jedoch in '
            'komprimierten agilen Zyklen statt sequentiell. Jede Phase startete mit einer '
            'Spezifikation (Mockup oder verbal), wurde durch Claude Code (KI 1) implementiert '
            'und durch direktes Nutzerfeedback im Browser iterativ verfeinert. '
            'Die folgende Chronologie dokumentiert Design-Entscheidungen und '
            'Verantwortlichkeiten explizit:',
            NRM
        ),

        # --- Phase 1 ---
        (
            'Phase 1 – Stack-Migration & UI-Grundgerüst (März–April 2026)',
            LB
        ),
        (
            'Ziel: Migration von Python/FastAPI + JSX auf React 19 + TypeScript + Vite + '
            'ASP.NET Core 8; Aufbau des FHNW-konformen UI-Grundgerüsts.',
            LB2
        ),
        (
            'Design-Input durch Iwo Kuhn: 21 PPTX-Mockup-Slides (Anhang A.4) definierten '
            'Farben (FHNW Navy #002B5C, FHNW Yellow #FFD700 gemäss Styleguide V5 [R54]), '
            'Typografie (Inter), Navigation (Sidebar mit Lernenden-Liste), und '
            'Seitenstruktur (Übersicht, Bereichsansicht, Rotationsplanung).',
            LB2
        ),
        (
            'Claude Code Beitrag: Vollständige Portierung JSX → TSX, Tailwind-Konfiguration '
            'mit FHNW-Design-Tokens (fhnw-navy, fhnw-yellow, fhnw-light), MSAL-Auth-Gerüst, '
            'Type-System src/types/index.ts, React Router v7, TanStack Query v5.',
            LB2
        ),
        (
            'Ergebnis: Lauffähige SPA mit Corporate Design; keine KI-Funktionalität — '
            'bewusstes Vorgehen (Grundfunktionen zuerst, KI-Integration in Phase 4).',
            LB2
        ),

        # --- Phase 2 ---
        (
            'Phase 2 – Backend-Migration zu ASP.NET Core 8 (April–Mai 2026)',
            LB
        ),
        (
            'Ziel: Python/FastAPI-Backend vollständig durch ASP.NET Core 8 Clean Architecture '
            'ersetzen; EF Core 8 + SQL Server als Persistenzschicht.',
            LB2
        ),
        (
            'Design-Input durch Iwo Kuhn: Verbale Spezifikation der Schichtenarchitektur '
            '(Domain / Application / Infrastructure / API) und Datenanforderungen; '
            'Architekturentscheid durch FHNW Enterprise Architekt (Azure + .NET Stack).',
            LB2
        ),
        (
            'Claude Code Beitrag: Vollständige Implementierung aller vier Clean-Architecture-'
            'Projekte (HK.Domain, HK.Application, HK.Infrastructure, HK.API); EF Core '
            'Migrations, snake_case JSON (SnakeCaseLower), CORS-Konfiguration, '
            'alle REST-Endpunkte (Users, Goals, Rotations, Competencies, APs).',
            LB2
        ),
        (
            'Ergebnis: Vollständiger Stack-Austausch ohne Feature-Regression; '
            'Python-Backend abgelöst; Swagger-Dokumentation automatisch generiert.',
            LB2
        ),

        # --- Phase 3 ---
        (
            'Phase 3 – Kernfunktionen: Kompetenz-Tracking & Rotationsverwaltung (Mai 2026)',
            LB
        ),
        (
            'Ziel: Vollständige manuelle Kernfunktionalität — Bloom-Bewertung, '
            'Rotationsmodalität, AP-Badge.',
            LB2
        ),
        (
            'Design-Input durch Iwo Kuhn: Mockups für Sidebar-Sektion «Ausbildungsplätze», '
            'Rotationsmodal-Layout und Bloom-Stufen-Visualisierung (K0–K6 Farbskala).',
            LB2
        ),
        (
            'Claude Code Beitrag: RotationModal, AP-Badge im Header, optimistisches Delete '
            '(State-Update vor API-Call), alle CRUD-Operationen, AppContext-Zustandsmanagement.',
            LB2
        ),
        (
            'Ergebnis: Produktiv einsetzbare Grundversion ohne KI — '
            'Berufsbildner kann Bloom-Stufen manuell vergeben und Rotationen verwalten.',
            LB2
        ),

        # --- Phase 3b ---
        (
            'Phase 3b – Rotationsplanung Gantt (Mai 2026) — Claude Code als Designer',
            LB
        ),
        (
            'Ziel: Interaktives Gantt-Diagramm für visuelle Rotationsplanung '
            'mit Drag & Drop, Konflikt-Erkennung und Lehrzeit-Beschränkung.',
            LB2
        ),
        (
            'Design-Input durch Iwo Kuhn: Keine PPTX-Vorlage — verbale Anforderung: '
            '«Ich brauche eine Gantt-Ansicht wo ich Rotationen drag-and-droppen und '
            'in der Länge anpassen kann; Doppelbelegungen sollen sichtbar sein.»',
            LB2
        ),
        (
            'Claude Code Beitrag (eigenständiges UI-Design): Entwurf des kompletten '
            'Gantt-Layouts inkl. Koordinatensystem (Semester/Monat-Zoom), '
            'Drag-Move-Handles, Resize-Handles links/rechts, Drag-from-Legend '
            '(AP-Chip auf Lernenden-Zeile), Konflikt-Erkennung (gelber Rahmen bei '
            'AP-Doppelbelegung), Lehrzeit-Beschränkung (Balken nicht über lv0/lv1 '
            'ziehbar), AP-zentrierte Gegenansicht (Toggle Lernende/Ausbildungsplätze), '
            'Heute-Button, Scroll-Synchronisation Header/Body.',
            LB2
        ),
        (
            'Konversationelle Optimierung (ca. 15 Iterationen): Farb-Kontrast der '
            'AP-Balken, Breite der Resize-Handles, Scroll-Sync nach View-Wechsel, '
            'AP-Dropdown im Header bei AP-Sicht, Badge-Darstellung für Lernenden-Spezialität '
            '(AE/PE/FI). Jede Iteration: Iwo evaluiert im Browser → Feedback → '
            'Claude Code passt an → erneute Evaluation.',
            LB2
        ),
        (
            'Ergebnis: Grösste Einzelkomponente der App — vollständig durch KI-Design '
            'und menschliches Feedback-Loop entstanden; zeigt exemplarisch das Potenzial '
            'konversationeller Softwareentwicklung.',
            LB2
        ),

        # --- Phase 3c ---
        (
            'Phase 3c – AP-Lernenden-Ansicht & Abdeckungsanalyse (Mai 2026)',
            LB
        ),
        (
            'Ziel: Dedizierte Seite pro Ausbildungsplatz mit '
            'HK-Abdeckungsanalyse für den gewählten Lernenden.',
            LB2
        ),
        (
            'Design-Input durch Iwo Kuhn: Entscheid für dedizierte Route statt '
            'Overlay (UI-Prinzip: komplexe Ansichten = eigene Seiten, nicht Modals); '
            'verbale Spezifikation des zweistufigen Accordions.',
            LB2
        ),
        (
            'Claude Code Beitrag: Route /ap-view/:apCode, APLernView.tsx, '
            'zweistufiges Accordion (Bereich → HK → Goals), Bereichs-/HK-Counter, '
            'Fortschrittsbalken, getAPLernProgress-Utility, Sidebar-Sektion '
            '«Ausbildungsplätze» mit %-Badge.',
            LB2
        ),
        (
            'Ergebnis: Transparente HK-Abdeckung pro AP und Lernenden; '
            'Kernargument B1 (Transparenz) der Arbeit konkret umgesetzt.',
            LB2
        ),

        # --- Phase 4 ---
        (
            'Phase 4 – KI-Vollintegration (geplant, Juli–August 2026)',
            LB
        ),
        (
            'Ausstehend: Azure OpenAI live schalten (Bloom-Bewertung in Produktion, '
            'KI 2 und KI 5), MSAL-Authentifizierung (Entra ID, sobald IT-Freigabe), '
            'Deployment Azure App Service. Dokumentenbeurteilung (KI 5) ist '
            'vollständig implementiert und wartet auf Azure-API-Key-Freigabe.',
            LB2
        ),
    ]

    # Insert before the "Demo-Szenario 1" bullet (so demos follow the chronology)
    insert_before(anchor, phase_content)
    print(f"OK: Inserted {len(phase_content)} paragraphs (phase chronology) before Demo-Szenarien in 3.3")

    doc.save(DOCX_PATH)
    print(f"\nSaved: {DOCX_PATH}")


if __name__ == '__main__':
    main()
