"""
Erstellt den ersten groben Entwurf (Stichwort-Niveau) der CAS-Abschlussarbeit als Word-Dokument.
HK-Tracker App – CAS AI in Software Engineering 2026, FHNW
Autor: Iwo Kuhn
"""

from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

OUTPUT_PATH = r"C:\Projekte\IT-Lehre Handlungskompetenzen\doku\HKTracker_CAS_Abschlussarbeit_Entwurf_v01.docx"

doc = Document()

# ─── Seitenränder ────────────────────────────────────────────────────────────
section = doc.sections[0]
section.top_margin    = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin   = Cm(3.0)
section.right_margin  = Cm(2.5)

# ─── Hilfsfunktionen ─────────────────────────────────────────────────────────

def add_heading(doc, text, level):
    """Heading mit korrektem Style."""
    p = doc.add_heading(text, level=level)
    return p

def add_italic_hint(doc, text):
    """Kursiver Hinweistext (grau) – was dieser Abschnitt gemäss Vorgabe enthalten soll."""
    p = doc.add_paragraph()
    run = p.add_run(f"[Vorgabe] {text}")
    run.italic = True
    run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
    run.font.size = Pt(10)
    return p

def add_todo(doc, text):
    """Grauer TODO-Hinweis."""
    p = doc.add_paragraph()
    run = p.add_run(f"[TODO: {text}]")
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    run.font.size = Pt(10)
    run.italic = True
    return p

def add_bullet(doc, text, italic_ref=None):
    """Bullet-Point, optional mit kursiver Referenz am Ende."""
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(text)
    if italic_ref:
        ref_run = p.add_run(f"  {italic_ref}")
        ref_run.italic = True
        ref_run.font.color.rgb = RGBColor(0x44, 0x44, 0x88)
        ref_run.font.size = Pt(10)
    return p

def add_bullet2(doc, text):
    """Eingerückter Bullet (Level 2)."""
    p = doc.add_paragraph(style='List Bullet 2')
    p.add_run(text)
    return p

def add_ref(doc, text):
    """Kursiver Referenzhinweis-Absatz."""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.italic = True
    run.font.color.rgb = RGBColor(0x44, 0x44, 0x88)
    run.font.size = Pt(10)
    return p

def add_section_break(doc):
    doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# TITELBLATT
# ═══════════════════════════════════════════════════════════════════════════════

# Titelseite
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p_title.add_run("\n\n\nHK-Tracker: KI-gestützte Verwaltung von Handlungskompetenzen in der IT-Berufsbildung")
run.bold = True
run.font.size = Pt(20)

p_subtitle = doc.add_paragraph()
p_subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run2 = p_subtitle.add_run("Abschlussarbeit\nCertificate of Advanced Studies (CAS) – KI für Softwareentwicklung (AI in Software Engineering)")
run2.font.size = Pt(14)

doc.add_paragraph()
doc.add_paragraph()

def add_centered_kv(doc, key, value):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run(f"{key}: ")
    r1.bold = True
    r1.font.size = Pt(12)
    r2 = p.add_run(value)
    r2.font.size = Pt(12)
    return p

add_centered_kv(doc, "Autor", "Iwo Kuhn")
add_centered_kv(doc, "Institution", "Fachhochschule Nordwestschweiz (FHNW), Hochschule für Informatik (HSI)")
add_centered_kv(doc, "Funktion", "Berufsbildner, FHNW Windisch")
add_centered_kv(doc, "Betreuer", "Prof. Dr. Samuel Fricker, FHNW")
add_centered_kv(doc, "Abgabe", "16. August 2026")
add_centered_kv(doc, "Ort / Datum", "Windisch, 2026")
add_centered_kv(doc, "Vertraulichkeitsstufe", "Öffentlich")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# EHRENWÖRTLICHE ERKLÄRUNG
# ═══════════════════════════════════════════════════════════════════════════════

add_heading(doc, "Ehrenwörtliche Erklärung", 1)
doc.add_paragraph(
    "Ich versichere, dass ich die vorliegende Arbeit selbstständig und ohne Benutzung anderer als der "
    "im Literaturverzeichnis angegebenen Quellen und Hilfsmittel angefertigt habe."
)
doc.add_paragraph(
    "Die wörtlich oder inhaltlich den im Literaturverzeichnis aufgeführten Quellen und Hilfsmitteln "
    "entnommenen Stellen sind in der Arbeit als Zitat bzw. Paraphrase kenntlich gemacht."
)
add_todo(doc, "Datum und Unterschrift einfügen vor Abgabe")
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# ABSTRACT / MANAGEMENT SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

add_heading(doc, "Management Summary / Abstract", 1)
add_italic_hint(doc,
    "Prägnante, aussagekräftige und vollständige Information für nicht involvierte Fachpersonen "
    "über Ausgangslage, Ziel, Vorgehen und Ergebnisse. Ca. 200 Wörter. "
    "Bewertungskriterium: Management/Executive Summary (Bewertungsraster Kriterium 3).")

doc.add_paragraph("Stichworte / Struktur für den Abstract:")

add_bullet(doc, "PROBLEM: Manuelle Dokumentation von Handlungskompetenzen (HK) in der IT-Berufsbildung ist zeitaufwendig, fehleranfällig und inkonsistent; kein digitales Werkzeug für Bloom-taxonomie-basierte Kompetenzbewertung im FHNW-Kontext vorhanden.")
add_bullet(doc, "LÖSUNG: HK-Tracker – Webapplikation (React/TypeScript + ASP.NET Core 8 + SQL Server + Azure) mit geplanter Azure-OpenAI-Integration für automatisierte Kompetenzbewertung.")
add_bullet(doc, "METHODE: Specification-Driven Development (SDD), Agile Entwicklung, arc42-Architekturdokumentation, DORA-Metriken als Messrahmen.")
add_bullet(doc, "ERGEBNISSE (Ist-Zustand): Funktionsfähige App mit Kompetenz-Tracking (Bloom K1–K6), Rotationsplanung (Gantt-Ansicht), Ausbildungsplatz-Abdeckungsanalyse, Dokumentenverwaltung.")
add_bullet(doc, "KI-ASPEKT: Azure OpenAI für automatisierte Bloom-Stufenerkennung; Embedding-basierte Ähnlichkeitssuche für Kompetenznachweise; Claude Code als KI-gestütztes Entwicklungswerkzeug.")
add_bullet(doc, "AUSBLICK: MSAL-Authentifizierung, SharePoint-Integration, Multi-User-Fähigkeit, Live-Deployment Azure App Service.")
add_bullet(doc, "WISSENSCHAFTLICHER BEITRAG: Übertragbares Modell für KI-gestützte Kompetenzdokumentation in Berufsbildungsorganisationen; Beitrag zu GenAI-Forschungsagenda im SE.")
add_todo(doc, "Abstract als Fliesstext ausformulieren (ca. 200 Wörter), auf Basis dieser Stichworte")
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# INHALTSVERZEICHNIS (Platzhalter)
# ═══════════════════════════════════════════════════════════════════════════════

add_heading(doc, "Inhaltsverzeichnis", 1)
add_todo(doc, "Automatisches Inhaltsverzeichnis in Word einfügen: Verweise > Inhaltsverzeichnis")
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# KAPITEL 1: EINLEITUNG
# ═══════════════════════════════════════════════════════════════════════════════

add_heading(doc, "1  Einleitung", 1)
add_italic_hint(doc,
    "Pflichtkapitel gemäss Vorgabe. Enthält: Problembeschreibung, organisatorische Einbettung, "
    "KI-bezogene Unternehmens- und Projektziele, Stakeholder- und Kontextanalyse. "
    "Bewertungsrelevanz: Zielformulierung (15%), Einbettung in Strategie/Unternehmensziele (50%-Block).")

# 1.1
add_heading(doc, "1.1  Ausgangslage und Problemstellung", 2)
add_italic_hint(doc,
    "Problembeschreibung: Warum besteht das Problem? Welche Schmerzen haben die Stakeholder? "
    "Klare Abgrenzung: Was wird adressiert, was nicht?")

add_bullet(doc, "Fachkräftemangel IT-Berufsbildung Schweiz: strukturelles Problem, wachsender Bedarf an qualifiziertem Nachwuchs",
           "vgl. [R10] Nguyen-Duc et al. 2025 (GenAI Research Agenda) / Tag 03 Fachkräftemangel")
add_bullet(doc, "Manuelle HK-Dokumentation: Berufsbildner führen Kompetenznachweise in Word/Excel; kein standardisiertes digitales Werkzeug")
add_bullet(doc, "Inkonsistente Bloom-Bewertung: subjektive Einschätzungen, keine KI-Unterstützung für Taxonomie-Erkennung")
add_bullet(doc, "Fehlende Übersicht: Ausbildungsplatz-Abdeckung nicht automatisiert auswertbar → Rotationslücken unerkannt")
add_bullet(doc, "Zeitaufwand Berufsbildner: geschätzt X Stunden/Lernenden/Jahr für Dokumentation",
           "vgl. [R15] Google SRE – Toil-Konzept: Automatisierung manueller Repetitivarbeit")
add_bullet(doc, "FHNW-spezifisch: ca. X Lernende (Informatik EFZ + ICT-Fachmann EFZ) an Y Ausbildungsplätzen")
add_todo(doc, "Konkrete Zahlen einfügen: Anzahl Lernende, Ausbildungsplätze, geschätzter Zeitaufwand")
add_bullet(doc, "Abgrenzung: HK-Tracker fokussiert auf interne FHNW-Berufsbildung; kein Schulnoten-System, keine HR-Integration (Phase 1)")

add_section_break(doc)

# 1.2
add_heading(doc, "1.2  Organisatorische Einbettung", 2)
add_italic_hint(doc,
    "Organisatorische Einbettung, zentrale Randbedingungen und Abgrenzungen: "
    "In welchem Kontext läuft das Projekt? Welche Constraints gelten?")

add_bullet(doc, "Organisation: FHNW Hochschule für Informatik (HSI), Berufsbildungsabteilung, Standort Windisch")
add_bullet(doc, "Berufsbildner als Primärnutzer: verantwortlich für Kompetenzbeurteilung, Rotationsplanung, Lernenden-Begleitung")
add_bullet(doc, "Ausbildungsberufe: Informatiker EFZ (3-/4-jährig) + ICT-Fachmann EFZ (3-jährig)")
add_bullet(doc, "Regulatorischer Rahmen: Bildungsplan EFZ (SBBK), Handlungskompetenzen als gesetzliches Lernziel-Konzept")
add_bullet(doc, "Technische Rahmenbedingungen: FHNW Azure-Tenant, Active Directory (MSAL), bestehende Microsoft-Infrastruktur")
add_bullet(doc, "Datenschutz: Lernendendaten = personenbezogene Daten; DSG (Schweiz) + DSGVO-kompatible Verarbeitung zwingend")
add_bullet(doc, "Aktueller Stack: React/TypeScript (Frontend) + ASP.NET Core 8 (Backend) + SQL Server + Azure App Service",
           "vgl. [R18] NIST SP 800-145 Cloud-Definition (alle 5 Kriterien erfüllt)")
add_bullet(doc, "Entwicklungsrahmen: Solo-Entwickler (Iwo Kuhn), Agile/iterativ, Claude Code als KI-Entwicklungsassistent",
           "vgl. Tag 02 RARIX 4-Layer-Architektur (Claude Code Agent Harness)")
add_todo(doc, "Organigramm FHNW Berufsbildung als Abbildung einfügen (Anhang A)")

add_section_break(doc)

# 1.3
add_heading(doc, "1.3  KI-bezogene Unternehmens- und Projektziele", 2)
add_italic_hint(doc,
    "Unternehmens- und Projektziele mit KI-Fokus. Was soll KI konkret leisten? "
    "Einbettung in Strategie (Bewertungskriterium: Ziele-Einbettung in Strategie).")

add_bullet(doc, "Übergeordnetes Ziel: Reduktion des manuellen Dokumentationsaufwands für Berufsbildner durch KI-gestützte Kompetenzbewertung")
add_bullet(doc, "KI-Projektziel 1: Automatische Erkennung der Bloom-Taxonomiestufe (K1–K6) aus Freitexteingaben der Lernenden",
           "vgl. [R01] Bahi et al. 2024 (GenAI für Agile SE)")
add_bullet(doc, "KI-Projektziel 2: Embedding-basierte Ähnlichkeitssuche – ähnliche Kompetenznachweise finden und vorschlagen",
           "vgl. Tag 06 Kennel: Vektordatenbanken/Embeddings")
add_bullet(doc, "KI-Projektziel 3: Azure OpenAI (GPT-4o) als Backend-Service für Bewertungsvorschläge; Mensch trifft finale Entscheidung",
           "vgl. Tag 06 Prinzip: 'KI darf helfen, Mensch entscheidet'")
add_bullet(doc, "KI-Projektziel 4: SDD-Prinzip (Specification-Driven Development) für Weiterentwicklung der App: Kompetenzprofile als Spec",
           "vgl. [R23] Fowler SDD-Tools / Tag 01 SDD-Konzept")
add_bullet(doc, "Strategische Einbettung FHNW: Digitalisierung der Berufsbildungsadministration; KI als Upskilling-Werkzeug für Berufsbildner",
           "vgl. [R10] Abrahamsson et al. 2025 / Tag 03 Skill Management")
add_bullet(doc, "ISPMA-Produktstrategie: HK-Tracker als internes Produkt mit Potenzial zur Übertragung auf andere Hochschulen",
           "vgl. [R19] ISPMA Body of Knowledge / Tag 03")
add_todo(doc, "SMART-Ziele ausformulieren mit messbaren KPIs (Zeitersparnis in Stunden/Lernenden/Jahr)")

add_section_break(doc)

# 1.4
add_heading(doc, "1.4  Stakeholder- und Kontextanalyse", 2)
add_italic_hint(doc,
    "Stakeholder- und Kontextanalyse: Wer ist betroffen? Welche Interessen/Anforderungen? "
    "Systemkontext: Was gehört dazu, was nicht? Methodik: RAM nach Gorschek & Wohlin.")

add_bullet(doc, "Stakeholder 1 – Lernende (Informatik EFZ / ICT-Fachmann EFZ):",
           "vgl. [R05] Gorschek & Wohlin 2006 RAM-Modell")
add_bullet2(doc, "Interesse: transparente Kompetenzdokumentation, Fortschrittsüberblick")
add_bullet2(doc, "Einfluss: mittel; Input durch Lernenden-Einträge (Freitexte)")
add_bullet2(doc, "Risiko: zu komplexe Oberfläche, geringe Akzeptanz")

add_bullet(doc, "Stakeholder 2 – Berufsbildner (Primärnutzer):")
add_bullet2(doc, "Interesse: Zeitersparnis, KI-Vorschläge als Unterstützung (nicht Ersatz), einfache Bedienung")
add_bullet2(doc, "Einfluss: hoch; definiert Anforderungen, validiert KI-Output")
add_bullet2(doc, "Risiko: Decision Fatigue durch zu viele KI-Vorschläge", )
add_ref(doc, "  vgl. [R07] Kropp et al. 2026 – +33% Decision Fatigue bei intensivem KI-Einsatz")

add_bullet(doc, "Stakeholder 3 – Ausbildungsverantwortliche (Management FHNW):")
add_bullet2(doc, "Interesse: Compliance mit Bildungsplan EFZ, Reportings, Ressourcenplanung")
add_bullet2(doc, "Einfluss: mittel; Budgetentscheidung für Live-Deployment")
add_bullet2(doc, "Risiko: Datenschutzbedenken, Abhängigkeit von Azure-OpenAI")

add_bullet(doc, "Stakeholder 4 – FHNW IT-Abteilung:")
add_bullet2(doc, "Interesse: Sicherheit, MSAL-Integration, Compliance mit FHNW-Infrastruktur")
add_bullet2(doc, "Einfluss: hoch für Deployment-Entscheid")

add_bullet(doc, "Systemkontext (arc42 Kapitel 3):",
           "vgl. Tag 05 arc42-Dokumentationsframework")
add_bullet2(doc, "IN SCOPE: HK-Erfassung, Bloom-Bewertung, Rotationsplanung, Ausbildungsplatz-Abdeckung, Dokumentenverwaltung, KI-Bewertungsvorschläge")
add_bullet2(doc, "OUT OF SCOPE: Schulnoten-System, HR-Personalakte, Lohn-System, externe Schulen (Phase 1)")

add_bullet(doc, "Requirements Abstraction Model (RAM) angewendet:",
           "vgl. [R05] Gorschek & Wohlin 2006")
add_bullet2(doc, "Business Goal: Qualitätsvolle IT-Berufsbildung durch effiziente HK-Dokumentation")
add_bullet2(doc, "System Goal: Digitale, KI-gestützte Kompetenzverwaltungsplattform")
add_bullet2(doc, "System Requirements: Bloom-Bewertung K1–K6, Rotationsplanung Gantt, Azure-OpenAI-API")
add_bullet2(doc, "Constraints: DSG Datenschutz, FHNW Azure-Tenant, Browser-Kompatibilität")

add_todo(doc, "Stakeholder-Interviews durchführen (RE-Methodik Tag 04 Eichholzer); Interviewprotokoll in Anhang B")
add_todo(doc, "Systemkontextdiagramm erstellen (arc42 Kapitel 3) und als Abbildung einfügen")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# KAPITEL 2: PLANUNG
# ═══════════════════════════════════════════════════════════════════════════════

add_heading(doc, "2  Planung", 1)
add_italic_hint(doc,
    "Pflichtkapitel. Enthält: Wertstromanalyse, geplanter KI-Einsatz, erwartete Benefits, "
    "Vorgehen zur Einführung und Validierung, Beitrag der Arbeit. "
    "Höchste Gewichtung im Bewertungsraster (50%): Auswahl KI-Ansatz, Integration in Unternehmenskontext, Umsetzung, Validierung, Ethik/Nachhaltigkeit.")

# 2.1
add_heading(doc, "2.1  Wertstromanalyse (Value Stream)", 2)
add_italic_hint(doc,
    "Wertstromanalyse: aktuellen Prozess (Ist) und KI-optimierten Prozess (Soll) beschreiben. "
    "Value Stream Management gemäss DORA 2025 Report S. 73.")

add_bullet(doc, "Methode: Value Stream Mapping (VSM); Ist-Zustand vs. Soll-Zustand",
           "vgl. [R17] DORA 2025 Report – Value Stream Management S. 73")

doc.add_paragraph().add_run("IST-Wertstrom (manuell, heute):").bold = True
add_bullet2(doc, "Lernender erbringt Leistung am Ausbildungsplatz")
add_bullet2(doc, "Berufsbildner beobachtet / erhält mündlichen Bericht")
add_bullet2(doc, "Berufsbildner erfasst Kompetenznachweis in Word/Excel (manuell, ca. 15–30 Min.)")
add_bullet2(doc, "Bloom-Stufe wird subjektiv geschätzt (K1–K6)")
add_bullet2(doc, "Rotationsplanung in separater Excel-Tabelle (kein Abgleich mit HK-Status)")
add_bullet2(doc, "Ausbildungsplatz-Abdeckung: manuelle Auswertung, fehleranfällig")
add_bullet2(doc, "Gesamtaufwand Berufsbildner: geschätzt [X Std./Lernenden/Jahr]")
add_todo(doc, "Ist-Prozess durch Interview mit einem Berufsbildner validieren und Zeit-Messungen ergänzen")

doc.add_paragraph().add_run("SOLL-Wertstrom (KI-gestützt, nach Einführung HK-Tracker):").bold = True
add_bullet2(doc, "Lernender erfasst Kompetenznachweis direkt im HK-Tracker (Freitext)")
add_bullet2(doc, "Azure OpenAI analysiert Freitext → schlägt Bloom-Stufe vor (K1–K6)")
add_bullet2(doc, "Berufsbildner reviewt KI-Vorschlag, klickt Bestätigung (< 2 Min.)")
add_bullet2(doc, "Rotationsplanung synchronisiert automatisch mit HK-Status")
add_bullet2(doc, "Ausbildungsplatz-Abdeckung: automatisch berechnet und visualisiert")
add_bullet2(doc, "Zeitersparnis Berufsbildner: Ziel > 50% Reduktion Dokumentationsaufwand  vgl. [R15] Google SRE – Toil-Elimination")

add_bullet(doc, "Engpässe (Bottlenecks) im Ist-Zustand: manuelle Bloom-Kategorisierung, fehlende Systemintegration")
add_bullet(doc, "KI-Interventionspunkt: Azure OpenAI an genau diesem Engpass-Schritt einsetzen")
add_todo(doc, "VSM-Diagramm (Ist und Soll) als Abbildung erstellen")

add_section_break(doc)

# 2.2
add_heading(doc, "2.2  Geplanter KI-Einsatz", 2)
add_italic_hint(doc,
    "Welche KI wird für welche Software-Engineering-Aufgaben eingesetzt? "
    "Bewertungskriterium: Auswahl des KI-basierten Ansatzes.")

add_bullet(doc, "KI 1: Azure OpenAI (GPT-4o) – Bloom-Taxonomie-Erkennung",
           "vgl. [R10] Abrahamsson et al. 2025; Tag 08 Agentic AI Sicherheitsregeln")
add_bullet2(doc, "Input: Freitext-Kompetenznachweis des Lernenden")
add_bullet2(doc, "Output: Bloom-Stufe K1–K6 + Begründung + Konfidenzwert")
add_bullet2(doc, "Prompt-Design: Few-Shot mit Bloom-Beispielen aus Bildungsplan EFZ")
add_bullet2(doc, "Menschliche Kontrolle: Berufsbildner muss KI-Vorschlag explizit bestätigen")

add_bullet(doc, "KI 2: Embedding-basierte Ähnlichkeitssuche (Azure OpenAI Embeddings + Vektordatenbank)",
           "vgl. Tag 06 Kennel Vektordatenbanken; Tag 05 LiteLLM Gateway")
add_bullet2(doc, "Use Case: Ähnliche Kompetenznachweise aus Vergangenheit abrufen")
add_bullet2(doc, "Technologie: Azure Cognitive Search oder pgvector (PostgreSQL)")
add_bullet2(doc, "Ziel: Konsistenz in Bewertungen über verschiedene Berufsbildner/Jahrgänge")

add_bullet(doc, "KI 3: Claude Code (Anthropic) als KI-gestütztes Entwicklungswerkzeug",
           "vgl. Tag 02 RARIX 4-Layer / Tag 01 SDD")
add_bullet2(doc, "Einsatz: Spezifikationsgetriebene Weiterentwicklung (SDD-Prinzip)")
add_bullet2(doc, "Qualitätssicherung: Hooks & Harnesses (ESLint, Tests)")
add_bullet2(doc, "Dokumentation: arc42-Architektur, ADRs via MADR v4")

add_bullet(doc, "LiteLLM Gateway als Abstraktionsschicht (Provider-unabhängig)",
           "vgl. Tag 05 LiteLLM Teil 2")
add_bullet2(doc, "Vorteil: Fallback zwischen Azure OpenAI / Anthropic / anderen Providern")
add_bullet2(doc, "Rate-Limit-Handling, Usage-Tracking")

add_bullet(doc, "Nicht eingesetzte KI-Alternativen (Begründung):")
add_bullet2(doc, "OpenAI direkt (statt Azure): Datenschutzbedenken, kein FHNW-Tenant")
add_bullet2(doc, "On-Premise LLM: Performance nicht ausreichend für Echtzeitbewertung")
add_todo(doc, "ADR erstellen: 'Warum Azure OpenAI?' (MADR v4 Format) → Anhang C")

add_section_break(doc)

# 2.3
add_heading(doc, "2.3  Erwartete Benefits", 2)
add_italic_hint(doc,
    "Erwartete Benefits und Benefits-Kalkulation: Zeitersparnis, Qualitätssteigerung. "
    "Quantitative und qualitative Benefits beschreiben.")

add_bullet(doc, "Quantitativer Benefit 1: Zeitersparnis Berufsbildner")
add_bullet2(doc, "Ist: ca. [X] Min. pro Kompetenznachweis (manuelle Bloom-Bewertung)")
add_bullet2(doc, "Soll: ca. [Y] Min. (KI-Vorschlag bestätigen)")
add_bullet2(doc, "Hochrechnung: [X Lernende] × [Z Nachweise/Jahr] = [Stunden/Jahr gespart]")
add_todo(doc, "Basislinie messen: aktuellen Zeitaufwand durch Beobachtung/Interview erfassen")

add_bullet(doc, "Quantitativer Benefit 2: Konsistenz der Bloom-Bewertungen")
add_bullet2(doc, "Messgrösse: Inter-Rater-Reliabilität vor/nach KI-Einführung")
add_bullet2(doc, "Ziel: Abweichung < 0.5 Bloom-Stufen zwischen verschiedenen Berufsbildnern")

add_bullet(doc, "Qualitativer Benefit 1: Bessere Rotationsplanung")
add_bullet2(doc, "Lernende werden gezielter in Ausbildungsplätze rotiert (Lücken sichtbar)")
add_bullet2(doc, "Reduktion von «vergessenen» Handlungskompetenzen")

add_bullet(doc, "Qualitativer Benefit 2: Upskilling Berufsbildner")
add_bullet2(doc, "Berufsbildner lernen durch KI-Begründungen mehr über Bloom-Taxonomie  vgl. [R10] Tag 03: GenAI für Upskilling/Reskilling")

add_bullet(doc, "Risikobenefit: Reduktion Burnout-Risiko durch Automatisierung von Toil",
           "vgl. [R07] Kropp et al. 2026 – Delegation repetitiver Aufgaben: -15% Burnout")

add_bullet(doc, "Negative Benefits (Risiken):")
add_bullet2(doc, "Decision Fatigue durch übermässige KI-Vorschläge  vgl. [R07] Kropp et al. 2026 – +33% Decision Fatigue")
add_bullet2(doc, "AI Slop: KI generiert minderwertige Bewertungen wenn Freitext zu kurz")
add_bullet2(doc, "Kreativitätskonvergenz: alle Lernenden erhalten ähnliche Bloom-Einschätzungen  vgl. [R02] Doshi & Hauser 2024")

add_section_break(doc)

# 2.4
add_heading(doc, "2.4  Vorgehen zur Einführung und Validierung", 2)
add_italic_hint(doc,
    "Vorgehen zur Einführung und Validierung: Wie wird die KI eingeführt und validiert? "
    "Agiles Vorgehen, Pilotnutzung, Messpunkte.")

add_bullet(doc, "Phase 1 (abgeschlossen): Grundfunktionen ohne KI",
           "vgl. [R17] DORA 2025 – Incremental Delivery")
add_bullet2(doc, "Kompetenz-Tracking, Bloom-Bewertung manuell")
add_bullet2(doc, "Rotationsplanung (Gantt)")
add_bullet2(doc, "Ausbildungsplatz-Abdeckungsanalyse")

add_bullet(doc, "Phase 2 (geplant, Juni–August 2026): Azure-OpenAI-Integration")
add_bullet2(doc, "Backend: ASP.NET Core Service für LLM-Aufrufe (via LiteLLM oder Azure SDK)")
add_bullet2(doc, "Frontend: KI-Vorschlag-UI mit Bestätigungspflicht")
add_bullet2(doc, "Security: Managed Identity (kein API-Key im Code), MSAL-Authentifizierung")
add_bullet2(doc, "Regression-Net aufbauen vor Integration (HTTP-Snapshot-Tests)  vgl. Tag 05 Burns – Regression-Net vor Refactoring")

add_bullet(doc, "Phase 3 (Pilotnutzung): Erste echte Lernende")
add_bullet2(doc, "Zielgruppe: 1–2 Lernende + 1 Berufsbildner als Early Adopters")
add_bullet2(doc, "Dauer: 4–6 Wochen Pilotbetrieb")
add_bullet2(doc, "Datenerhebung: Zeiterfassung, Benutzer-Feedback (strukturiertes Interview)  vgl. Tag 04 Eichholzer – Empathisches RE-Interview")

add_bullet(doc, "Validierungsstrategie:")
add_bullet2(doc, "Qualitativ: Interview-Feedback Berufsbildner ('Was funktioniert gut? Was fehlt?')")
add_bullet2(doc, "Quantitativ: DORA-Metriken (Lead Time, Deployment Frequency)  vgl. [R17] DORA 2025 / Tag 08 Graf DORA Metrics")
add_bullet2(doc, "Inhaltlich: Bloom-Treffer-Quote – KI-Vorschlag vs. Berufsbildner-Entscheid")

add_bullet(doc, "Einführungsprinzipien (12-Factor App, Cloud-native):",
           "vgl. Tag 08 Graf – 12-Factor App / NIST SP 800-145")
add_bullet2(doc, "Konfiguration via Environment Variables (kein Hardcoding)")
add_bullet2(doc, "Health Checks, Logging, Observability")
add_bullet2(doc, "IaC (Bicep/ARM) für Azure-Infrastruktur")

add_todo(doc, "Zeitplan als Gantt-Diagramm erstellen: Phase 2 + Phase 3 mit Meilensteinen bis 16.8.2026")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# KAPITEL 3: UMSETZUNG
# ═══════════════════════════════════════════════════════════════════════════════

add_heading(doc, "3  Umsetzung", 1)
add_italic_hint(doc,
    "Pflichtkapitel. Enthält: Tooling und Infrastruktur, Beispielbasierte Demonstration, "
    "Einbezug der Stakeholder, Pilotnutzung, Messung und Beobachtung der Benefits und Effekte. "
    "Bewertungsrelevanz: Umsetzung KI-Ansatz, Validierung.")

# 3.1
add_heading(doc, "3.1  Tooling und Infrastruktur", 2)
add_italic_hint(doc,
    "Tooling-Entscheide: Welche Werkzeuge wurden gewählt und warum? "
    "Infrastruktur: Cloud-Architektur, IaC. "
    "Bewertungsrelevanz: Auswahl KI-Ansatz, Integration in Unternehmenskontext.")

add_bullet(doc, "Frontend: React 18 + TypeScript + Vite")
add_bullet2(doc, "Begründung: Moderne SPA, starke Typisierung, schnelle Iterationen")
add_bullet2(doc, "UI-Bibliothek: Tailwind CSS + shadcn/ui (FHNW CI-konform)")

add_bullet(doc, "Backend: ASP.NET Core 8 Web API")
add_bullet2(doc, "Begründung: FHNW .NET-Stack, Azure-Integration nativ, starke Typisierung")
add_bullet2(doc, "Datenbank: SQL Server (Azure SQL Database)")

add_bullet(doc, "KI-Tooling: Azure OpenAI Service (GPT-4o Deployment)")
add_bullet2(doc, "Entscheidung für Azure: FHNW-Tenant, Datenschutz (EU Data Boundary), keine Datenweitergabe an OpenAI Training  vgl. Tag 08 Sicherheitsregeln Agentic AI")
add_bullet2(doc, "LiteLLM Gateway: Provider-Abstraktion, Fallback, Rate-Limit-Handling  vgl. Tag 05 LiteLLM")

add_bullet(doc, "Entwicklungswerkzeug: Claude Code (Anthropic) als KI-Assistent",
           "vgl. Tag 02 RARIX 4-Layer / Tag 01 SDD-Prinzip")
add_bullet2(doc, "SDD-Ansatz: Spezifikation als Grundlage für KI-Code-Generierung")
add_bullet2(doc, "Hooks: ESLint pre-commit, TypeScript strict mode")
add_bullet2(doc, "CLAUDE.md + Memory-System als Projektkontext")

add_bullet(doc, "Deployment: Azure App Service")
add_bullet2(doc, "CI/CD: GitHub Actions (Build → Test → Deploy)")
add_bullet2(doc, "IaC: Bicep-Templates (geplant)")
add_bullet2(doc, "Monitoring: Azure Application Insights")

add_bullet(doc, "Architektur-Dokumentation: arc42 (12-Kapitel-Standard)",
           "vgl. Tag 05 arc42-Framework")
add_bullet2(doc, "ADRs mit MADR v4-Format (geplant)")
add_bullet2(doc, "Systemkontextdiagramm, Building Block View")

add_todo(doc, "ADR-Index erstellen (arc42 Kapitel 9): alle Architekturentscheide auflisten")
add_todo(doc, "Vollständige arc42-Dokumentation als Anhang D")

add_section_break(doc)

# 3.2
add_heading(doc, "3.2  Architektur (arc42-Struktur)", 2)
add_italic_hint(doc,
    "Beispielbasierte Demonstration (auch als 3.2 Demonstration/Proof of Concept). "
    "arc42-Struktur: Kontext, Building Blocks, ADRs.")

add_bullet(doc, "Systemkontext (arc42 Kapitel 3):")
add_bullet2(doc, "Externe Systeme: Azure OpenAI API, Azure SQL, FHNW Azure AD (MSAL), SharePoint (geplant)")
add_bullet2(doc, "Nutzer-Rollen: Lernender, Berufsbildner, Admin")

add_bullet(doc, "Building Blocks (arc42 Kapitel 5):")
add_bullet2(doc, "Frontend SPA (React): Views – Kompetenztracking, Rotationsplanung, AP-Abdeckung, Lernreise, Dokumente")
add_bullet2(doc, "Backend API (ASP.NET Core): Controller – Competencies, Rotations, Workplaces, AI-Bewertung")
add_bullet2(doc, "Datenbank: SQL Server – HK-Schema (Lernende, Kompetenzen, Bewertungen, Rotationen)")
add_bullet2(doc, "KI-Service (geplant): LLM Gateway → Azure OpenAI")

add_bullet(doc, "Wichtigste Architecture Decision Records (ADRs):")
add_bullet2(doc, "ADR-001: Warum React statt Angular/Vue?")
add_bullet2(doc, "ADR-002: Warum ASP.NET Core statt Node.js/Python?")
add_bullet2(doc, "ADR-003: Warum Azure OpenAI statt direktem OpenAI?")
add_bullet2(doc, "ADR-004: Warum LiteLLM als Gateway?")
add_bullet2(doc, "ADR-005: Warum SQL Server statt PostgreSQL?")

add_bullet(doc, "Qualitätsattribute (arc42 Kapitel 1):")
add_bullet2(doc, "Sicherheit: MSAL-Auth, Least Privilege für KI-Agenten  vgl. Tag 08 – Never trust the agent")
add_bullet2(doc, "Datenschutz: DSG-konform, Lernendendaten in FHNW Azure-Tenant")
add_bullet2(doc, "Usability: Decision Fatigue minimieren (max. 1 KI-Aktion pro Bewertungs-Workflow)  vgl. [R07] Kropp et al. 2026")
add_bullet2(doc, "Wartbarkeit: SDD + arc42 + ADRs für Nachvollziehbarkeit")

add_todo(doc, "arc42-Architekturdiagramm (C4 oder UML) als Abbildung 3.2 einfügen")

add_section_break(doc)

# 3.3
add_heading(doc, "3.3  Demonstration / Proof of Concept", 2)
add_italic_hint(doc,
    "Beispielbasierte Demonstration: Screenshots, Workflows, Demo-Szenarien. "
    "Beweis, dass die Umsetzung funktioniert.")

add_bullet(doc, "Demo-Szenario 1: Lernender erfasst Kompetenznachweis")
add_bullet2(doc, "Screenshot: Eingabemaske mit Freitext-Feld")
add_bullet2(doc, "Screenshot: KI-Vorschlag (Bloom K3 – Anwenden) mit Begründung")
add_bullet2(doc, "Screenshot: Berufsbildner bestätigt oder korrigiert")

add_bullet(doc, "Demo-Szenario 2: Rotationsplanung Gantt-Ansicht")
add_bullet2(doc, "Screenshot: Gantt-Diagramm mit Ausbildungsplatz-Timeline")
add_bullet2(doc, "Screenshot: Lückenanalyse – fehlende HKs farblich markiert")

add_bullet(doc, "Demo-Szenario 3: Ausbildungsplatz-Abdeckungsmatrix")
add_bullet2(doc, "Screenshot: Matrix Ausbildungsplätze × Handlungskompetenzen")
add_bullet2(doc, "Screenshot: Prozentwert Abdeckung je HK-Bereich")

add_bullet(doc, "Demo-Szenario 4 (geplant): KI-Ähnlichkeitssuche")
add_bullet2(doc, "Mockup: «Ähnliche Kompetenznachweise» aus Embedding-Suche")

add_todo(doc, "Aktuelle Screenshots der App einfügen (aus /doku/screenshot_*.png)")
add_todo(doc, "Screencast-Video als QR-Code-Link im Anhang E")

add_section_break(doc)

# 3.4
add_heading(doc, "3.4  Einbezug der Stakeholder (inkl. Schulung)", 2)
add_italic_hint(doc,
    "Einbezug der Stakeholder, inklusive Schulung. Wie wurden Stakeholder eingebunden? "
    "RE-Methodik, Feedback-Loops, Schulungskonzept.")

add_bullet(doc, "Stakeholder-Einbezug bisher:")
add_bullet2(doc, "Informelle Gespräche mit Berufsbildner-Kollegen (Requirements-Elicitation)")
add_bullet2(doc, "Feedback-Runde zu UI/UX (AP-Kompetenzabdeckung, Modal vs. Seite)  vgl. /doku/UI-Design-Diskussion-AP-Kompetenzabdeckung.md")
add_bullet2(doc, "Konzept-Review durch Betreuer Prof. Dr. Samuel Fricker")

add_bullet(doc, "Geplanter Stakeholder-Einbezug (Phase 3 Pilot):")
add_bullet2(doc, "Strukturierte Interviews mit 2 Berufsbildnern (RE-Methodik Eichholzer)  vgl. Tag 04 – Empathisches Requirements-Interview")
add_bullet2(doc, "Usability-Test mit 2 Lernenden (Think-Aloud-Protokoll)")
add_bullet2(doc, "Feedback-Kategorisierung mit AI4KM-Ticket-Workflow  vgl. Tag 06 AI4KM Simulation")

add_bullet(doc, "Schulungskonzept:")
add_bullet2(doc, "Berufsbildner: 30-Min. Einführung (Screencast + Live-Demo)")
add_bullet2(doc, "Lernende: Kurze Onboarding-Seite direkt in der App")
add_bullet2(doc, "Prinzip: KI-Vorschläge erklären sich selbst durch Begründungstext")

add_bullet(doc, "Governance-Modell (AI4KM-inspiriert):")
add_bullet2(doc, "Support-Ebene: Berufsbildner (Feedback, KI-Korrekturen)")
add_bullet2(doc, "Engineering-Ebene: Iwo Kuhn (Entwicklung, Bugfixes)")
add_bullet2(doc, "Management-Ebene: Ausbildungsverantwortliche (Strategische Entscheide, Budget)")

add_section_break(doc)

# 3.5
add_heading(doc, "3.5  Messung und Beobachtung der Benefits und Effekte", 2)
add_italic_hint(doc,
    "Messung und Beobachtung der Benefits und Effekte. "
    "DORA-Metriken oder vergleichbares Messframework anwenden.")

add_bullet(doc, "Messrahmen: DORA Metrics (DevOps Research and Assessment)",
           "vgl. [R17] DORA 2025 Report / Tag 08 Graf DORA Metrics")

add_bullet(doc, "DORA Metrik 1: Lead Time for Changes")
add_bullet2(doc, "Definition im HK-Kontext: Zeit von Lernenden-Eintrag bis KI-Bewertung fertiggestellt")
add_bullet2(doc, "Messung: Timestamp Eingabe vs. Timestamp Berufsbildner-Bestätigung")
add_bullet2(doc, "Zielwert: < 5 Minuten (vs. Ist: ~20–30 Min. manuell)")

add_bullet(doc, "DORA Metrik 2: Deployment Frequency")
add_bullet2(doc, "Definition: Wie oft wird die HK-Tracker-App deployed?")
add_bullet2(doc, "Messung: GitHub Actions Deployment-Logs")
add_bullet2(doc, "Zielwert: mind. 1×/Woche (Continuous Delivery)")

add_bullet(doc, "DORA Metrik 3: Change Failure Rate")
add_bullet2(doc, "Definition: Anteil deployments mit Produktionsfehler")
add_bullet2(doc, "Messung: Azure Application Insights Error Tracking")

add_bullet(doc, "DORA Metrik 4: Time to Restore Service")
add_bullet2(doc, "Definition: Wiederherstellungszeit nach Ausfall")
add_bullet2(doc, "Relevant wenn: Azure OpenAI unavailable → Fallback auf manuelle Bewertung")

add_bullet(doc, "Zusätzliche KI-spezifische Metriken:")
add_bullet2(doc, "KI-Trefferquote: Anteil KI-Bloom-Vorschläge, die Berufsbildner unverändert akzeptiert")
add_bullet2(doc, "Zeitersparnis: Vergleich Ist vs. Soll (Stoppuhr-Messung im Pilotbetrieb)")
add_bullet2(doc, "Decision Fatigue Proxy: Anzahl KI-Vorschläge die abgebrochen werden (Abandon Rate)")

add_bullet(doc, "Testing-Strategie (Qualitätssicherung):",
           "vgl. Tag 07 Burns / [R11] Yoo & Harman 2012 / [R03] Elbaum et al. 2014")
add_bullet2(doc, "Unit Tests: Bloom-Kategorisierungs-Logik (xUnit)")
add_bullet2(doc, "Integration Tests: API-Endpunkte (HTTP-Snapshot-Tests)")
add_bullet2(doc, "E2E Tests: Playwright (geplant)")
add_bullet2(doc, "Regression-Net vor KI-Integration aufbauen")

add_todo(doc, "Messdaten aus Pilotphase ausfüllen (nach Phase 3)")
add_todo(doc, "Dashboard/Tabelle: Metriken Ist vs. Soll vs. Erreicht")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# KAPITEL 4: DISKUSSION
# ═══════════════════════════════════════════════════════════════════════════════

add_heading(doc, "4  Diskussion", 1)
add_italic_hint(doc,
    "Pflichtkapitel. Enthält: Erreichte Ergebnisse, Beitrag der Arbeit, empfohlene nächste Schritte. "
    "Bewertungsrelevanz: Beantwortung Fragestellung, Qualität Empfehlungen, eigener Beitrag.")

# 4.1
add_heading(doc, "4.1  Erreichte Ergebnisse und Zielerreichung", 2)
add_italic_hint(doc,
    "Erreichte Ergebnisse: Wurden die Ziele erreicht? Was funktioniert, was nicht? "
    "Kritische Reflexion der eigenen Arbeit.")

add_bullet(doc, "Ergebnis 1: Funktionsfähige Webapplikation (Phase 1 abgeschlossen)")
add_bullet2(doc, "HK-Tracking mit Bloom K1–K6 (manuell) ✓")
add_bullet2(doc, "Rotationsplanung Gantt-Ansicht ✓")
add_bullet2(doc, "Ausbildungsplatz-Abdeckungsanalyse ✓")
add_bullet2(doc, "Dokumentenverwaltung ✓")

add_bullet(doc, "Ergebnis 2: KI-Integration (Phase 2 – geplant/in Bearbeitung)")
add_bullet2(doc, "Azure OpenAI Bloom-Erkennung: [Status einfügen]")
add_bullet2(doc, "Embedding-Ähnlichkeitssuche: [Status einfügen]")

add_bullet(doc, "Zielerreichung KI-Aspekt:")
add_bullet2(doc, "KI-Projektziel 1 (Bloom-Erkennung): [Status bei Abgabe]")
add_bullet2(doc, "KI-Projektziel 2 (Embedding-Suche): [Status bei Abgabe]")
add_bullet2(doc, "KI-Projektziel 3 (Azure OpenAI live): [Status bei Abgabe]")

add_bullet(doc, "Kritische Selbstbewertung:")
add_bullet2(doc, "Solo-Entwickler-Risiko: begrenzte Kapazität für Testing + Entwicklung gleichzeitig")
add_bullet2(doc, "Pilotphase zeitlich knapp vor Abgabe (16.8.2026)")
add_bullet2(doc, "Offene Punkte: MSAL, SharePoint-Integration, Multi-User")

add_todo(doc, "Diesen Abschnitt nach Phase 2+3 mit tatsächlichen Ergebnissen ergänzen")

add_section_break(doc)

# 4.2
add_heading(doc, "4.2  Wissenschaftlicher Beitrag", 2)
add_italic_hint(doc,
    "Beitrag der Arbeit: Was ist der wissenschaftliche/praktische Beitrag? "
    "Bewertungskriterium: Klarheit und Signifikanz des eigenen Beitrags, Transferierbarkeit.")

add_bullet(doc, "Praktischer Beitrag 1: Funktionsfähiger HK-Tracker als Open-Source-Prototyp für FHNW")
add_bullet(doc, "Praktischer Beitrag 2: Übertragbares Muster – KI-gestützte Kompetenzbewertung in der Berufsbildung")
add_bullet2(doc, "Anwendbar auf andere Hochschulen, Lehrberufe, Bildungsorganisationen  vgl. Bewertungskriterium: Transferierbarkeit auf andere Unternehmen")

add_bullet(doc, "Wissenschaftlicher Beitrag 1: Beitrag zur GenAI-Forschungsagenda im SE",
           "vgl. [R10] Nguyen-Duc / Abrahamsson et al. 2025")
add_bullet2(doc, "Konkrete Fallstudie: KI in Bildungs-Softwareentwicklung (Solo-Entwickler, Agentic Development)")
add_bullet2(doc, "Validierung SDD-Prinzip in Nicht-Enterprise-Kontext")

add_bullet(doc, "Wissenschaftlicher Beitrag 2: Anwendung DORA Metrics auf KI-Projekt ausserhalb Tech-Konzern",
           "vgl. [R17] DORA 2025 – primär für grosse Softwareunternehmen konzipiert")

add_bullet(doc, "Wissenschaftlicher Beitrag 3: Verifikation Kropp et al. Decision Fatigue in Bildungskontext",
           "vgl. [R07] Kropp et al. 2026 – erste Berufsbildungsanwendung?")

add_bullet(doc, "Beitrag zur CAS-Lernziel-Abdeckung:")
add_bullet2(doc, "KI in SE: Azure OpenAI, Claude Code, SDD (Tags 01–02)")
add_bullet2(doc, "Management: Wertstrom, Benefits, Stakeholder (Tags 03–04)")
add_bullet2(doc, "Architektur: arc42, ADRs, LiteLLM (Tag 05)")
add_bullet2(doc, "DevOps: DORA, Cloud, IaC (Tags 07–08)")

add_section_break(doc)

# 4.3
add_heading(doc, "4.3  Grenzen und Risiken", 2)
add_italic_hint(doc,
    "Kritische Reflexion: Grenzen der Arbeit, Risiken, ethische Überlegungen. "
    "Bewertungskriterium: Berücksichtigung von Ethik und Gesetzen.")

add_bullet(doc, "Datenschutz und Recht:")
add_bullet2(doc, "Lernendendaten = personenbezogen; DSG (Schweiz) Art. 5 + DSGVO-Kompatibilität  vgl. Tag 11 Eva Polini – Ethics & Law [noch ausstehend]")
add_bullet2(doc, "Azure OpenAI: Daten verlassen FHNW-Tenant nicht (EU Data Boundary) – dokumentieren")
add_bullet2(doc, "KI-Transparenz: Lernende müssen informiert werden, dass KI-Bewertung erfolgt")
add_bullet2(doc, "Keine autonomen KI-Entscheide ohne menschliche Prüfung  vgl. Tag 08 Sicherheitsregel 5: No unsupervised access")

add_bullet(doc, "Kognitive Risiken (KI-spezifisch):")
add_bullet2(doc, "Decision Fatigue Berufsbildner bei zu vielen KI-Vorschlägen  vgl. [R07] Kropp et al. 2026 – +33% Decision Fatigue")
add_bullet2(doc, "AI Slop: KI-Bewertungen könnten bei zu kurzem Input generisch werden  vgl. Tag 03 – AI Slop / AI Brain Fry")
add_bullet2(doc, "Kreativitätskonvergenz: ähnliche Bewertungen für alle Lernenden  vgl. [R02] Doshi & Hauser 2024")
add_bullet2(doc, "Verifikationsproblem: KI-Bloom-Bewertungen schwer objektiv zu prüfen  vgl. Tag 03 – Sichere KI-Nutzung")

add_bullet(doc, "Technische Risiken:")
add_bullet2(doc, "Azure-OpenAI-Abhängigkeit: Ausfall, Kosten, API-Änderungen")
add_bullet2(doc, "Modell-Halluzinationen: GPT-4o könnte falsche Bloom-Stufe begründen")
add_bullet2(doc, "Skalierbarkeit: bei vielen gleichzeitigen Benutzer Rate-Limits")

add_bullet(doc, "Methodische Grenzen:")
add_bullet2(doc, "Solo-Entwickler: keine Peer-Review der Architekturentscheide")
add_bullet2(doc, "Kleine Pilotgruppe: Validierungsergebnisse nicht statistisch signifikant")
add_bullet2(doc, "Zeitrahmen: KI-Integration und Pilotphase zeitlich komprimiert")

add_bullet(doc, "Nachhaltigkeit:")
add_bullet2(doc, "Energie-Footprint Azure OpenAI-Aufrufe: Bloom-Bewertung nur on-demand, kein Batch-Processing  vgl. Bewertungskriterium: Berücksichtigung von Nachhaltigkeit")
add_bullet2(doc, "Wartbarkeit: arc42-Dokumentation und ADRs sichern langfristige Pflegbarkeit")

add_section_break(doc)

# 4.4
add_heading(doc, "4.4  Empfohlene nächste Schritte", 2)
add_italic_hint(doc,
    "Empfohlene nächste Schritte: Was kommt nach der Abschlussarbeit? "
    "Priorisierte Roadmap.")

add_bullet(doc, "Kurzfristig (bis Ende 2026):")
add_bullet2(doc, "MSAL-Authentifizierung: FHNW Azure AD Login für alle Nutzer")
add_bullet2(doc, "Multi-User: Mehrere Berufsbildner mit Rollenkonzept (Admin, Berufsbildner, Lernender)")
add_bullet2(doc, "Azure OpenAI live: Bloom-Bewertung in Produktion schalten")

add_bullet(doc, "Mittelfristig (2027):")
add_bullet2(doc, "SharePoint-Integration: Kompetenznachweise direkt aus SharePoint-Dokumenten extrahieren")
add_bullet2(doc, "Embedding-Ähnlichkeitssuche: Vektordatenbank aufbauen (pgvector/Azure Cognitive Search)")
add_bullet2(doc, "Reporting: PDF-Berichte für Ausbildungsverantwortliche")
add_bullet2(doc, "Mobile-Optimierung: PWA für Lernende unterwegs")

add_bullet(doc, "Langfristig (2028+):")
add_bullet2(doc, "Übertragung auf andere FHNW-Departementseinheiten")
add_bullet2(doc, "Pilot: Andere Berufsbildungsorganisationen (Transferierbarkeit)")
add_bullet2(doc, "KI-Personalisierung: individualisierte Lernpfade basierend auf HK-Profil")
add_bullet2(doc, "Integration Bildungsraum Schweiz (Erfa, SBBK, Lehrbetriebe)")

add_bullet(doc, "Forschungsempfehlungen:")
add_bullet2(doc, "Langzeitstudie: Qualitätsverbesserung HK-Dokumentation über mehrere Jahrgänge")
add_bullet2(doc, "A/B-Test: KI-Vorschlag vs. kein KI-Vorschlag (Bloom-Qualität vergleichen)")
add_bullet2(doc, "Validierung GenAI-Forschungsagenda Abrahamsson in Berufsbildungskontext  vgl. [R10] Nguyen-Duc / Abrahamsson et al. 2025")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# LITERATURVERZEICHNIS
# ═══════════════════════════════════════════════════════════════════════════════

add_heading(doc, "Literatur- und Quellenverzeichnis", 1)
add_italic_hint(doc,
    "APA-Literaturverzeichnis obligatorisch (gemäss Abschlussarbeits-Vorgabe). "
    "Alle verwendeten Quellen vollständig mit APA 7 aufführen. "
    "Bewertungskriterium: Aktualität und Repräsentativität der Quellen.")

refs = [
    "[R01] Bahi, A., Gharib, J., & Gahi, Y. (2024). Integrating generative AI for advancing agile software development and mitigating project management challenges. International Journal of Advanced Computer Science and Applications, 15(3), 54–61. https://doi.org/10.14569/IJACSA.2024.0150306",
    "[R02] Doshi, A. R., & Hauser, O. P. (2024). Generative artificial intelligence enhances creativity but reduces the diversity of novel content. [Zeitschrift ausstehend; Vollreferenz aus Originaltext prüfen].",
    "[R03] Elbaum, S., Rothermel, G., & Penix, J. (2014). Techniques for improving regression testing in continuous integration development environments. Proceedings of the 22nd ACM SIGSOFT International Symposium on Foundations of Software Engineering (FSE '14). https://doi.org/10.1145/2635868.2635910",
    "[R04] Fu, M., & Tantithamthavorn, C. (2022). GPT2SP: A transformer-based agile story point estimation approach. IEEE Transactions on Software Engineering, 48(11), 4416–4433. https://doi.org/10.1109/TSE.2021.3135781",
    "[R05] Gorschek, T., & Wohlin, C. (2006). Requirements abstraction model. Requirements Engineering, 11(1), 79–101. https://doi.org/10.1007/s00766-005-0029-0",
    "[R06] Holzmann, V., Zitter, D., & Peshkess, S. (2023). The expectations of project managers from artificial intelligence: A Delphi study. International Journal of Project Management, 41(7), 102526. https://doi.org/10.1016/j.ijproman.2023.102526",
    "[R07] Kropp, M., Meier, A., Anslow, C., & Biddle, R. (2026). When using AI leads to 'Brain Fry'. Harvard Business Review. [Vollreferenz prüfen]",
    "[R08] Mahajan, G. (2026). Operationalizing generative AI in software product management: A review of managerial use-cases, governance, and ethical guardrails. EngrXiv. https://doi.org/10.31224/6204",
    "[R09] Martensson, T., Borg, M., & Engström, E. (2025). So much more than test cases: Perspectives on AI-augmented quality assurance. [Konferenz/Zeitschrift prüfen].",
    "[R10] Nguyen-Duc, A., et al. (2025). Generative artificial intelligence for software engineering—A research agenda. Software: Practice and Experience. https://doi.org/10.1002/spe.70005",
    "[R11] Yoo, S., & Harman, M. (2012). Regression testing minimisation, selection, and prioritisation: A survey. Software Testing, Verification and Reliability, 22(2), 67–120. https://doi.org/10.1002/stvr.430",
    "[R12] Alegroth, E., Feldt, R., & Regnell, B. (2016). Maintenance of automated test suites in industry: An empirical study on downtime and maintenance work. Information and Software Technology, 73, 1–19. https://doi.org/10.1016/j.infsof.2016.01.003",
    "[R13] Alian, M. H., & Daoud, M. I. (2016). Test case reduction techniques: A survey. International Journal of Computer Applications, 134(16), 12–20. https://doi.org/10.5120/ijca2016908099",
    "[R14] Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (Eds.). (2018). Site Reliability Engineering: How Google runs production systems (Kapitel: Reaching Beyond). O'Reilly Media. https://sre.google/workbook/reaching-beyond/",
    "[R15] Google SRE Team. (2016). Eliminating toil. In B. Beyer et al. (Eds.), Site Reliability Engineering. O'Reilly Media. https://sre.google/sre-book/eliminating-toil/",
    "[R16] Porter, M. E. (2008). The five competitive forces that shape strategy. Harvard Business Review, 86(1), 78–93.",
    "[R17] DORA Research Team / Google Cloud. (2025). DORA Report 2025: State of DevOps – AI-assisted Software Development. https://dora.dev/research/2025/dora-report/",
    "[R18] NIST. (2011). The NIST definition of cloud computing (NIST SP 800-145). U.S. Department of Commerce. https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-145.pdf",
    "[R19] ISPMA. (n.d.). ISPMA Body of Knowledge. https://ispma.org/bok/",
    "[R20] IREB. (n.d.). AI4RE Micro-Credential. https://cpre.ireb.org/de/concept/ai4re-micro-credential",
    "[R21] BCG. (2026, Januar). Survey on AI tools and productivity [Umfrage, 1'488 Vollzeitbeschäftigte, USA]. [URL aus BCG-Originalquelle ergänzen]",
    "[R22] Boeckeler, B. (2026, Januar). State of play: KI-unterstützte Programmierung [Keynote, OOP Konferenz 2026]. https://speakerdeck.com/birgitta410/state-of-play-ki-unterstutzte-programmierung-oop-2026-keynote",
    "[R23] Fowler, M. (n.d.). Exploring Gen AI: SDD-3 tools. Martin Fowler's Bliki. https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html",
]

for ref in refs:
    p = doc.add_paragraph(style='List Paragraph')
    run = p.add_run(ref)
    run.font.size = Pt(10)

add_todo(doc, "Vollständige APA-Referenzen prüfen (DOIs verifizieren, fehlende Zeitschriftennamen ergänzen)")
add_todo(doc, "Tags 09–14 Referenzen ergänzen sobald Unterlagen verfügbar")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# GLOSSAR
# ═══════════════════════════════════════════════════════════════════════════════

add_heading(doc, "Glossar", 1)
add_italic_hint(doc, "Alle wesentlichen Fachbegriffe präzise klären und korrekt verwenden (Bewertungskriterium).")

glossar = [
    ("ADR", "Architecture Decision Record – dokumentiert eine Architekturentscheidung mit Kontext, Alternativen und Konsequenzen (MADR v4-Format)."),
    ("Bloom-Taxonomie", "Lernziel-Klassifikationsschema von Benjamin Bloom (1956): K1 Erinnern, K2 Verstehen, K3 Anwenden, K4 Analysieren, K5 Evaluieren, K6 Erschaffen."),
    ("CAS", "Certificate of Advanced Studies – Weiterbildungsabschluss (12 ECTS) der FHNW."),
    ("DORA", "DevOps Research and Assessment – Forschungsprogramm von Google mit 4 Kernmetriken für Software-Delivery-Performance."),
    ("EFZ", "Eidgenössisches Fähigkeitszeugnis – Schweizer Berufsausbildungsabschluss."),
    ("HK", "Handlungskompetenz – im Schweizer Bildungsplan EFZ definiertes Lernziel für Berufslernende, beschreibt eine konkrete berufliche Handlung."),
    ("IaC", "Infrastructure as Code – Infrastruktur wird wie Quellcode versioniert, getestet und automatisiert deployed (z.B. Bicep, Terraform)."),
    ("ISPMA", "International Software Product Management Association – Referenzrahmen für Software-Produktmanagement."),
    ("LiteLLM", "Open-Source-Gateway für LLM-Provider: abstrahiert Azure OpenAI, Anthropic, OpenAI u.a. hinter einer einheitlichen API."),
    ("MCP", "Model Context Protocol – Anthropic-Standard für Context-Injection in KI-Agenten."),
    ("MSAL", "Microsoft Authentication Library – Bibliothek für Azure Active Directory / Entra ID OAuth2-Authentifizierung."),
    ("NIST", "National Institute of Standards and Technology – US-Behörde; definiert u.a. Cloud-Computing-Standard SP 800-145."),
    ("RAM", "Requirements Abstraction Model nach Gorschek & Wohlin (2006) – hierarchisches Requirements-Modell: Business Goals → System Goals → Requirements → Constraints."),
    ("RARIX", "4-Layer-Architektur für professionelle Claude-Code-Nutzung (FHNW CAS AISE Tag 02)."),
    ("SDD", "Specification-Driven Development – KI-gestützte, spezifikationsgetriebene Codegenerierung (drei Reifestufen: Spec-First, Spec-Anchored, Spec-as-Source)."),
    ("SRE", "Site Reliability Engineering – Google-Philosophie: Operations-Toil < 50%, Qualitätsziele via SLOs/SLAs."),
    ("arc42", "12-Kapitel-Standard für Software-Architekturdokumentation (www.arc42.org)."),
]

for abbr, definition in glossar:
    p = doc.add_paragraph(style='List Paragraph')
    run1 = p.add_run(f"{abbr}: ")
    run1.bold = True
    run1.font.size = Pt(10)
    run2 = p.add_run(definition)
    run2.font.size = Pt(10)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# ABBILDUNGSVERZEICHNIS
# ═══════════════════════════════════════════════════════════════════════════════

add_heading(doc, "Abbildungsverzeichnis", 1)
add_todo(doc, "Automatisches Abbildungsverzeichnis in Word einfügen")
planned = [
    "Abbildung 1: FHNW Berufsbildung Organigramm",
    "Abbildung 2: Ist-Wertstrom (Value Stream Mapping)",
    "Abbildung 3: Soll-Wertstrom (KI-gestützt)",
    "Abbildung 4: arc42 Systemkontextdiagramm HK-Tracker",
    "Abbildung 5: Building Block View (Komponentendiagramm)",
    "Abbildung 6: Screenshot – Kompetenz-Tracking mit KI-Vorschlag",
    "Abbildung 7: Screenshot – Rotationsplanung Gantt-Ansicht",
    "Abbildung 8: Screenshot – Ausbildungsplatz-Abdeckungsmatrix",
    "Abbildung 9: DORA Metrics Dashboard HK-Tracker",
    "Abbildung 10: Zeitplan Phase 2+3 (Gantt)",
]
for item in planned:
    p = doc.add_paragraph(style='List Bullet')
    p.add_run(item).font.color.rgb = RGBColor(0x99, 0x99, 0x99)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# ABKÜRZUNGSVERZEICHNIS
# ═══════════════════════════════════════════════════════════════════════════════

add_heading(doc, "Abkürzungsverzeichnis", 1)
abbrevs = [
    ("ADR", "Architecture Decision Record"),
    ("API", "Application Programming Interface"),
    ("CAS", "Certificate of Advanced Studies"),
    ("CI/CD", "Continuous Integration / Continuous Delivery"),
    ("DORA", "DevOps Research and Assessment"),
    ("DSG", "Datenschutzgesetz (Schweiz)"),
    ("DSGVO", "Datenschutz-Grundverordnung (EU)"),
    ("EFZ", "Eidgenössisches Fähigkeitszeugnis"),
    ("FHNW", "Fachhochschule Nordwestschweiz"),
    ("GPT", "Generative Pre-trained Transformer"),
    ("HK", "Handlungskompetenz"),
    ("HSI", "Hochschule für Informatik (FHNW)"),
    ("IaC", "Infrastructure as Code"),
    ("ICT", "Information and Communication Technology"),
    ("ISPMA", "International Software Product Management Association"),
    ("KI / AI", "Künstliche Intelligenz / Artificial Intelligence"),
    ("LLM", "Large Language Model"),
    ("MADR", "Markdown Any Decision Records"),
    ("MCP", "Model Context Protocol"),
    ("MSAL", "Microsoft Authentication Library"),
    ("NIST", "National Institute of Standards and Technology"),
    ("PWA", "Progressive Web Application"),
    ("RAM", "Requirements Abstraction Model"),
    ("SDD", "Specification-Driven Development"),
    ("SPA", "Single Page Application"),
    ("SRE", "Site Reliability Engineering"),
    ("VSM", "Value Stream Mapping"),
]
for abbr, full in abbrevs:
    p = doc.add_paragraph(style='List Paragraph')
    r1 = p.add_run(f"{abbr}:\t")
    r1.bold = True
    r1.font.size = Pt(10)
    p.add_run(full).font.size = Pt(10)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# ANHANG A – Organigramm FHNW Berufsbildung
# ═══════════════════════════════════════════════════════════════════════════════

add_heading(doc, "Anhang A – Organigramm FHNW Berufsbildung", 1)
add_todo(doc, "Organigramm FHNW Berufsbildungsabteilung einfügen")
doc.add_paragraph("Platzhalter: Organigramm zeigt Einbettung Berufsbildner, Ausbildungsverantwortliche, Lernende in FHNW-Struktur.")

add_heading(doc, "Anhang B – Stakeholder-Interview-Protokolle", 1)
add_todo(doc, "Interview-Protokolle nach RE-Methodik (Eichholzer Tag 04) einfügen")
doc.add_paragraph("Platzhalter: Strukturierte Beobachtungstabellen aus Berufsbildner-Interviews.")

add_heading(doc, "Anhang C – Architecture Decision Records (ADRs)", 1)
add_todo(doc, "ADRs im MADR v4-Format für alle wichtigen Architekturentscheide erstellen")
doc.add_paragraph("Platzhalter: ADR-001 bis ADR-005 (React, ASP.NET Core, Azure OpenAI, LiteLLM, SQL Server).")

add_heading(doc, "Anhang D – arc42-Architekturdokumentation", 1)
add_todo(doc, "Vollständige arc42-Dokumentation mit Diagrammen einfügen")
doc.add_paragraph("Platzhalter: arc42 Kapitel 1, 3, 5, 9 vollständig ausgearbeitet.")

add_heading(doc, "Anhang E – Screenshots und Demo-Material", 1)
add_todo(doc, "Screenshots aus /doku/screenshot_*.png einfügen; ggf. Screencast-Link als QR-Code")
doc.add_paragraph("Platzhalter: Screenshots App-Oberfläche, Demo-Szenarien, Gantt-Ansicht.")

# ═══════════════════════════════════════════════════════════════════════════════
# Speichern
# ═══════════════════════════════════════════════════════════════════════════════

doc.save(OUTPUT_PATH)
print(f"Dokument erfolgreich erstellt: {OUTPUT_PATH}")

import os
size_kb = os.path.getsize(OUTPUT_PATH) / 1024
print(f"Dateigrösse: {size_kb:.1f} KB")
