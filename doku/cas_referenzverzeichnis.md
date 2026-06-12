# CAS AISE – Referenzverzeichnis und Modulübersicht

**CAS Künstliche Intelligenz für Softwareentwicklung (AISE)**  
FHNW, Hochschule für Informatik (HSI), 12 ECTS  
Studienjahr 2026, Dozierendenleitung: Prof. Dr. Samuel Fricker  
Erstellungsdatum: 2026-06-07 | Erstellt von: Iwo Kuhn

---

## Zweck dieses Dokuments

Strukturierte Übersicht aller bearbeiteten Modulunterlagen des CAS AISE mit:
- Kernthemen des jeweiligen Moduls/Tags
- Relevanz für die **Abschlussarbeit** und den **HK-Tracker App**
- Vollständigem Quellenverzeichnis aller explizit zitierten Referenzen

**HK-Tracker App Kontext:** Webapplikation zur Verwaltung von Handlungskompetenzen (HK) von IT-Lernenden (Informatik EFZ / ICT-Fachmann). Erfasst Lernziele auf Basis der Bloom-Taxonomie, verwaltet Ausbildungsplatz-Rotationen (Gantt-Ansicht), ermöglicht Dokumentenverwaltung. Technischer Stack: React/TypeScript-Frontend + ASP.NET Core-Backend. Geplant: Azure OpenAI-Integration für automatisierte Kompetenzbewertung.

---

## Administration

### CAS-Reglement

**Dokument:** `Reglement KI für Softwareentwicklung_signed.pdf`  
Unterzeichnet von: Prof. Dr. Doris Agotai (Direktorin HSI FHNW)

**Eckdaten:**
- Umfang: 12 ECTS, ein Semester
- Studiengebühren: CHF 7'900
- Benotung: Schweizer Skala 1–6, Bestehen ab Note 4.0
- Leistungsnachweis: einzige Prüfungsleistung ist die Projektarbeit (Abschlussarbeit)

**Relevanz für Abschlussarbeit:** Das Reglement definiert den formalen Rahmen. Benotung erfolgt ausschliesslich über die Abschlussarbeit – kein Modulabschluss, kein Zwischentest. Die Arbeit muss daher alle Lernziele des CAS sichtbar abdecken.

---

### Abschlussarbeit – Vorgaben

**Dokument:** `Abschlussarbeit CAS AISE 2026.docx` + `Abschlussarbeit CAS AISE VORLAGE 260504SFR.docx`

**Formales:**
- Umfang: 40–60 Seiten
- Individuelle Arbeit, Betreuung durch CAS-Dozierenden
- Abgabe: 16. August 2026
- Präsentationen: 27.–28. August 2026
- APA-Literaturverzeichnis obligatorisch

**Obligatorische Kapitelstruktur:**

| Kapitel | Inhalt |
|---------|--------|
| **Einleitung** | Problembeschreibung, organisatorische Einbettung, KI-bezogene Ziele, Stakeholder-Analyse |
| **Planung** | Wertstromanalyse (Value Stream), geplanter KI-Einsatz, Benefits-Kalkulation, Einführungsvorgehen |
| **Umsetzung** | Tooling-Entscheide, Demonstration/Proof of Concept, Stakeholder-Einbezug, Pilotnutzung, Messung (DORA-Metriken oder ähnlich) |
| **Diskussion** | Ergebnisse, wissenschaftlicher Beitrag, nächste Schritte |

**Relevanz für HK-Tracker:** Die Abschlussarbeit beschreibt die Integration von KI (Azure OpenAI) in den HK-Tracker als konkretes Praxisprojekt. Der Wertström führt von der manuellen Kompetenzeingabe durch Berufsbildner bis zur KI-gestützten Bewertung von Lernenden. Stakeholder: Lernende, Berufsbildner, Ausbildungsverantwortliche, ggf. Schulen.

---

## Tag 01 – KI in der Softwareentwicklung (23.04.2026)

**Dozent:** Prof. Dr. Samuel Fricker (FHNW)  
**Dokumente:**
- `01 CAS AISE KI in der Softwareentwicklung.pdf`
- `02 CAS AISE Hands-On.pdf`
- `03 SDD Aufgabenblatt.pdf`

### Kernthemen

**Specification-Driven Development (SDD):**
KI-gestützte, spezifikationsgetriebene Code-Generierung. Drei Reifestufen:
1. **Spec-First** – Spezifikation schreiben, dann Code generieren
2. **Spec-Anchored** – Spezifikation als Anker für iterative KI-Unterstützung
3. **Spec-as-Source** – Spezifikation ist die einzige persistente Quelle; Code ist ein Artefakt

Werkzeuge im Übungsrahmen: Python/Flask, PlantUML, Render.com (Hosting), GitHub Actions (CI/CD).

**DORA Metrics 2025:**
Vier Kernmetriken für Software-Delivery-Performance:
- Lead Time for Changes
- Deployment Frequency
- Change Failure Rate
- Time to Restore Service

DORA 2025 Report behandelt insbesondere: AI Adoption in Teams, AI Capabilities Model, Value Stream Management (Kapitel S. 73).

**DevOps-Lifecycle:**
Code → Plan → Build → Test → Deploy → Operate → Monitor (vollständiger Loop mit KI-Unterstützung an allen Stationen)

**CAS-Curriculum-Übersicht:**
Alle Dozierenden des CAS: Fernando Bentes (Claude Code), Daniel Burns (SE Practice + Testing/QA), Stefan Hackstein (Team Integration), Reto Eichholzer (Requirements Engineering), Andrea Kennel (Data Engineering), Sebastian Graf (Deployment/Betrieb), Christopher Scherb & Norbert Seyff (Cybersecurity, SW Evolution), Eva Polini (Ethics/Law), Andreas Lorenz (Erfahrungsbericht).

### Relevanz für HK-Tracker

| Thema | Warum relevant |
|-------|---------------|
| **SDD** | Der HK-Tracker könnte nach dem SDD-Prinzip weiterentwickelt werden: Kompetenzprofile als Spec, KI generiert daraus Bewertungsvorschläge. Für die Abschlussarbeit ist SDD als methodischer Rahmen für die Azure-OpenAI-Integration beschreibbar. |
| **DORA Metrics** | Messrahmen für den Kapitel "Messung" in der Abschlussarbeit. Lead Time (Zeit vom Lernziel-Eintrag bis zur KI-Auswertung), Deployment Frequency des HK-Trackers selbst. |
| **DevOps-Lifecycle** | Vollständiges Konzept für den geplanten Azure-Deployment-Prozess des HK-Trackers (GitHub → Build → Test → Azure App Service). |

---

## Tag 02 – Claude Code & Agent Harnesses (24.04.2026)

**Dozent:** Fernando Bentes (FHNW / Gastdozent)  
**Dokumente:**
- `fhnw-4-layer-architecture.html`
- `Take_Homes_Tag_2.pdf`

### Kernthemen

**RARIX 4-Layer-Architektur (Claude Code Agent Harness):**

Die vollständige Referenzarchitektur für professionelle Claude-Code-Nutzung:

| Layer | Inhalt |
|-------|--------|
| **Core** | Session-Lifecycle, Effort-Config, Context Management |
| **Instruction** | CLAUDE.md, Memory-System, Brain Vault, Rules |
| **Extension** | 235 Hooks, 12 MCP-Server, 155 Commands, Skills |
| **Orchestration** | Worktrees, 67 SQLite-Tabellen, Dispatch-System, Task-DAG, Heartbeats |

Leitprinzip: **"Prompts suggest, hooks guarantee."**

**Model Context Protocol (MCP):**
Standardisiertes Protokoll für Context-Injection in Claude Code. Ermöglicht Anbindung externer Datenquellen (z. B. Jira, GitHub, Datenbanken) als lebendigen Kontext für den Agenten.

**Agent Harnesses:**
Orchestrierte Multi-Agenten-Systeme mit Skills, Hooks und Commands. Playwright-MCP für UI-Testing-Automatisierung. Knowledge Graphs für SW-Qualitätssicherung.

**Take-Homes Tag 2:**
- Agent Harnesses als primäres Qualitätssicherungswerkzeug
- Hooks & Harnesses garantieren Coding Standards (pre-commit, pre-push)
- Lokaler Agent Harness als Alternative zu Cloud-Deployments

### Relevanz für HK-Tracker

| Thema | Warum relevant |
|-------|---------------|
| **RARIX 4-Layer** | Direkt anwendbar für den Kapitel "Tooling" der Abschlussarbeit: Claude Code wurde für die HK-Tracker-Entwicklung eingesetzt. Die 4-Layer-Architektur beschreibt, wie Agentic AI in den Entwicklungs-Workflow integriert wurde. |
| **MCP** | Azure OpenAI könnte über ein MCP-Server-Interface in den HK-Tracker integriert werden – Kompetenzprofile als kontextualisierter Input. |
| **Hooks & Harnesses** | Qualitätssicherung der TypeScript/React-Codebasis: ESLint-Hooks, Test-Harnesses als Garantie für Code-Qualität bei KI-generiertem Code. |
| **Playwright MCP** | Automatisiertes End-to-End-Testing des HK-Trackers (Browser-Automation). Relevant für Regressionstest-Absicherung bei KI-gestützter Weiterentwicklung. |

---

## Tag 03 – KI-gestütztes Management & Sicherer KI-Einsatz (30.04.2026)

**Dozent:** Prof. Dr. Samuel Fricker (FHNW)  
**Dokumente:**
- `KI-gestütztes Management im SE.pdf` (15-seitiges Skript)
- `aise-safer-use.pdf`
- `aise-ki-im-team.pdf` (nicht lesbar via Tool)
- `aise-warmup.pdf` (nicht lesbar via Tool)

### Kernthemen

#### KI-gestütztes Management im SE

**Engineering Management Komponenten:**
Project Management, HR, Teamarbeit, Budgetierung, Risikomanagement, Ethik

**Skill Management & Fachkräftemangel:**
- Fachkräftemangel in der IT als strukturelles Problem
- GenAI als Werkzeug für Upskilling und Reskilling
- Abrahamsson et al. Studie (Fokusgruppen April–Sept 2023, 15 Teilnehmer): Framework für GenAI-Forschungsagenda im SE

**Agile Frameworks Übersicht:**
Scrum, Extreme Programming (XP), Kanban, SAFe (Scaled Agile Framework), Nexus, Disciplined Agile

**Holzmann Delphi-Studie 2023:**
Relevanteste KI-Anwendungen aus Sicht von Projektmanagern (Delphi-Konsens):
Scheduling, Milestone-Planung, Work Breakdown Structure (WBS), Budgetierung

**Software Product Management:**
- Porter's Five Forces: Wettbewerbsanalyse für Softwareprodukte
- ISPMA Framework (International Software Product Management Association) als Referenzmodell

**Requirements Abstraction Model (RAM) – Gorschek & Wohlin (2006):**
Hierarchische Requirements-Ebenen:
- Business Goals → System Goals → System Requirements → Constraints
- Prozessschritte: Triage → Specify → Place → Work-up → Prioritize → Initiate

#### Sicherer KI-Einsatz im Arbeitsalltag

**Geeignete KI-Anwendungsfälle:**
- Textreformulierung und -zusammenfassung
- Ideenentwicklung (Prinzip: erst selbst Ideen generieren, dann KI)
- Rechercheunterstützung
- Automatisierungsskripte

**Problematische KI-Anwendungsfälle:**
- Komplexe, variablenreiche Aufgaben (Verifikationsproblem)
- Schwer verifizierbare Ergebnisse
- Sensible Daten (personenbezogen, vertraulich)
- Autonome Entscheidungen ohne menschliche Prüfung

**Kognitive Auswirkungen von KI-Nutzung (Kropp et al., 2026):**
- +11–39 % mehr Fehler bei Aufgaben mit intensivem KI-Einsatz
- +33 % erhöhte Entscheidungsmüdigkeit (Decision Fatigue)
- +39 % erhöhte Kündigungsabsicht (Resignation Intent)
- Delegation repetitiver Aufgaben an KI: -15 % Burnout
- Monitoring von KI-Outputs: +12 % mentale Erschöpfung

**KI und Kreativität (Doshi & Hauser, 2024):**
GenAI steigert individuelle Kreativität, reduziert aber die Diversität der Outputs (Konvergenzeffekt auf ähnliche Ideen).

**AI Brain Fry / AI Slop:**
Risiken bei exzessivem KI-Einsatz: kognitive Überlastung, Produktions von KI-Slop (minderwertigen Masseninhalten).

### Relevanz für HK-Tracker

| Thema | Warum relevant |
|-------|---------------|
| **RAM (Gorschek & Wohlin)** | Strukturiert die Requirements-Hierarchie für den HK-Tracker: Business Goal (HK-Förderung), System Goal (digitale Kompetenzdokumentation), System Requirements (Bloom-Bewertung, Rotationsplanung), Constraints (Datenschutz, FHNW-Infrastruktur). |
| **Holzmann Delphi 2023** | Legitimiert den Einsatz von KI für Scheduling und Planung – direkt anwendbar auf die Rotationsplanungs-Funktion des HK-Trackers. |
| **Skill Management** | Kernthema des HK-Trackers selbst: Digitalisierung von Kompetenzentwicklung als Gegenmassnahme zum Fachkräftemangel. Der HK-Tracker ist ein Werkzeug für strukturiertes Skill Management in der IT-Berufsbildung. |
| **Sichere KI-Nutzung** | Direkt relevant für die Azure-OpenAI-Integration: Abschlussarbeit muss KI-Grenzen (sensible Lernendendaten, Datenschutz) klar definieren. |
| **Decision Fatigue** | Berufsbildner haben begrenzte Aufmerksamkeit – der HK-Tracker muss KI-Bewertungsvorschläge so präsentieren, dass kognitive Last minimiert wird. |
| **ISPMA Framework** | Nutzbar als Produktmanagement-Referenzrahmen für die langfristige Roadmap des HK-Trackers. |

---

## Tag 04 – Requirements Engineering (07.05.2026)

**Dozent:** Reto Eichholzer (FHNW / Gastdozent)  
**Dokumente:**
- `transcript.md` (Simulations-Interview)
- `aise_re_presentation.pdf` (nicht lesbar via Tool)

### Kernthemen

**Empathisches Requirements-Elicitation:**
Simuliertes Interview mit einem Service-Techniker "Dave" (8 Jahre Erfahrung). Demonstration von:
- Klärungsorientierte Frageführung (Was? Wann? Wie?)
- De-Eskalation bei emotionalem Kundenkonflikt
- Trennung von Symptom-Beschreibung und Ursachenanalyse
- Strukturierte Beobachtungstabelle als RE-Artefakt

**Interview-Qualitätskriterien:**
- Originalaussagen unverändert bewahren
- Neutrale Zusammenfassungen (kein Urteil)
- Offene Fragen explizit dokumentieren
- Root Cause Analysis vor Lösungsversprechen

**Ungelöste RE-Fragen als Qualitätsmerkmal:**
Bewusstes Dokumentieren ungelöster Fragen (Zeitpunkt, Spezifizierung, Garantiefragen) als Zeichen professioneller RE-Praxis.

### Relevanz für HK-Tracker

| Thema | Warum relevant |
|-------|---------------|
| **Empathisches Interview** | Methodik für die Stakeholder-Analyse der Abschlussarbeit: Interviews mit Berufsbildnern und Lernenden zur Validierung des HK-Tracker-Konzepts. |
| **Strukturierte Beobachtungstabelle** | Vorlage für die Dokumentation von Nutzerfeedback während der Pilotnutzungsphase (Kapitel "Umsetzung" der Abschlussarbeit). |
| **RE Qualitätsprinzipien** | Checkliste für Requirements des HK-Trackers: Sind alle Anforderungen spezifiziert, platziert, priorisiert (RAM-Prozess)? |

---

## Tag 05 – KI-gestützte Dokumentation & Refactoring (08.05.2026)

**Dozent:** Fernando Bentes / Gastdozent Daniel Burns (FHNW)  
**Dokumente:**
- `mealie-two-parts.md` (69 KB Workshop-Anleitung)
- `presentation.html` (58 KB Slides)

### Kernthemen

**Mealie-Übung – AI-augmented Documentation & Refactoring:**

**Teil 1 – Dokumentation und Refactoring:**
Praktische Übung an der Open-Source-Rezeptapp Mealie (Python/FastAPI-Backend + Nuxt-Frontend).

Schritte:
1. Repository-Analyse mit KI: `SYSTEM_OVERVIEW.md` generieren (Core Analysis, System Design, Legacy Assessment)
2. Import-Graph mit `grimp` erstellen (Abhängigkeitsanalyse, DOT-Format)
3. arc42-Architekturdokumentation mit KI: Kapitel 1 (Ziele), 3 (Kontext), 5 (Building Blocks), 9 (ADR-Index)
4. LikeC4-DSL für C4-Architekturdiagramme
5. Architecture Decision Records (ADR) mit MADR v4-Format
6. Regression-Net aufbauen (Snapshot-Tests, HTTP-Fixtures) vor dem Refactoring
7. Layering Smell beheben mit KI-Unterstützung

**Teil 2 – LLM Gateway (LiteLLM):**
Ersetzen direkter Provider-SDK-Aufrufe durch LiteLLM-Gateway:
- Fallback zwischen Providern (OpenAI, Anthropic, Azure)
- Rate-Limit-Handling
- Provider-Abstraktion als Architekturprinzip

**Skills-System:**
Wiederverwendbare Prompt-Vorlagen (`SKILL.md`-Dateien) aus `thommann/skills`:
- `system-overview` Skill
- `arc42` Skill
- `document-decision` Skill
- `likec4-dsl` Skill

Prinzip: `CLAUDE.md` → symlink auf `AGENTS.md` (Single Source of Truth für alle KI-Tools).

**arc42-Dokumentationsstruktur:**
12-Kapitel-Standard für Software-Architekturdokumentation. Relevante Kapitel für KI-Projekte: 1 (Ziele/Qualitätsattribute), 3 (Systemkontext), 5 (Building Blocks), 9 (Architekturentscheide).

**MADR (Markdown Any Decision Records) v4:**
Standardformat für Architecture Decision Records (ADRs). Trennung von Kontext, Entscheidung, Konsequenzen.

### Relevanz für HK-Tracker

| Thema | Warum relevant |
|-------|---------------|
| **arc42** | Vollständiges Dokumentationsframework für die Architektur-Dokumentation des HK-Trackers in der Abschlussarbeit (Kapitel "Umsetzung"). |
| **LiteLLM Gateway** | Direkt anwendbar für die Azure-OpenAI-Integration: LiteLLM als Abstraktion zwischen HK-Tracker-Backend und verschiedenen LLM-Providern (Azure OpenAI, Anthropic). Fallback-Mechanismus erhöht Resilienz. |
| **Regression-Net vor Refactoring** | Sicherheitsnetz für die geplante KI-Erweiterung des HK-Trackers: HTTP-Snapshot-Tests absichern bestehende API-Endpunkte. |
| **ADRs (MADR v4)** | Dokumentiert Architekturentscheide im HK-Tracker (z. B. "Warum Azure OpenAI?", "Warum ASP.NET Core Backend?") – erhöht Nachvollziehbarkeit für Abschlussarbeit. |
| **AGENTS.md / CLAUDE.md** | Best Practice für KI-gesteuertes Development: Single Source of Truth für alle Agent-Anweisungen. Direkt übernehmbar für HK-Tracker-Repository. |

---

## Tag 06 – Data Engineering & KI-Produktmanagement (21.05.2026)

**Dozent:** Andrea Kennel (FHNW) + Prof. Dr. Samuel Fricker (FHNW)  
**Dokumente:**
- `AI4KM-ticket-anleitung.md` + `SKILL.md` (AI4KM Classroom Simulation)
- `AI4KM Classroom Simulation v2.2.docx-3.pdf`
- `01_fhnw_cas_aise_de_Einführung_v01.pdf` (Kennel, Data Engineering)
- `02_fhnw_cas_aise_de_Teil2_v01.pdf` (Kennel, Data Engineering)
- `Drehbuch_CAS_AISE_DE_v03.pdf`
- Übungsdateien: `Uebung1.txt`, `Uebung2.txt`
- Vektoren-Unterlagen: `Vektoren_U01_v01.pdf`, `Vektoren_U02_v01.pdf`
- Retrospektiven: `gesamtprotokoll_retrospektiven.pdf`, `retrospektive_1_Ergebnisse.pdf`

### Kernthemen

**AI4KM Classroom Simulation – KI-gestütztes Produktmanagement:**
Praxisübung zur KI-gestützten Ticketverwaltung anhand von OsmAnd-App-Reviews (Google Play).

Ticket-Workflow:
- Rohes Nutzerfeedback → strukturiertes Ticket (Intake/Support-Rolle)
- Taxonomie: Bug, Feature Request, UX/Usability, Question/Support, Duplicate, Out of Scope
- Komponenten: Navigation, Routing, Maps/Tiles, Offline Mode, Search, POI/Places, UI, Account/Sync, Permissions, Performance
- Owner: Support / Engineering / Management (klare Trennung)
- GitHub-Duplicate-Abgleich (OsmAnd GitHub Issues)
- Auto-Close-Regel für wartende Tickets (1 Runde ohne Antwort)

KI-Prinzip in der Simulation: **"KI darf später helfen, aber Menschen prüfen und entscheiden."**

**Data Engineering (Kennel):**
Einführung in Data Engineering für KI-Projekte:
- Vektordatenbanken (Embeddings, Ähnlichkeitssuche)
- Übungen zu Vektoren (Uebung1.txt, Uebung2.txt)

**Retrospektiven:**
Kurs-Retrospektiven dokumentiert in `gesamtprotokoll_retrospektiven.pdf`.

### Relevanz für HK-Tracker

| Thema | Warum relevant |
|-------|---------------|
| **AI4KM Ticket-Workflow** | Direkt übertragbar auf HK-Tracker: Feedback von Berufsbildnern und Lernenden strukturiert erfassen. Taxonomie anpassbar (Bug, Feature Request, Usability). KI unterstützt Kategorisierung, Mensch trifft Entscheid. |
| **Vektordatenbanken** | Kern-Technologie für die KI-Kompetenzbewertung: Kompetenzprofile und Bloom-Kriterien als Embeddings, Ähnlichkeitssuche findet passende Kompetenznachweise. |
| **Trennung Support/Engineering/Management** | Governance-Modell für den HK-Tracker-Betrieb: Klare Rollenverteilung zwischen Berufsbildner (Support-Ebene), Entwickler (Engineering) und Ausbildungsverantwortlichen (Management). |
| **Retrospektiven-Dokumentation** | Vorlage für Pilotphase-Reflexion im Kapitel "Diskussion" der Abschlussarbeit. |

---

## Tag 07 – KI für Testing & SW-Qualität (22.05.2026)

**Dozent:** Daniel Burns (FHNW / Gastdozent)  
**Dokumente:**
- `02-workshop-slides.html` (Workshop-Slides)
- Forschungspapiere (PDFs, nicht per Tool lesbar):
  - Alegroth (2016): Maintenance of Automated Test Suites in Industry
  - Alian (2016): Test Case Reduction Techniques – Survey
  - Elbaum (2014): Regression Testing in CI Environments
  - Martensson (2025): So much More than Test Cases
  - Yoo & Harman (2012): Regression Testing Minimisation, Selection, Prioritisation

### Kernthemen

**Automatisierte Test-Suites (Alegroth, 2016):**
Industriestudie über Wartung automatisierter Testsuiten. Schlüsselerkenntnisse: Testpflege ist teuer, KI kann Wartungsaufwand reduzieren durch automatische Test-Update-Vorschläge.

**Test Case Reduction (Alian, 2016):**
Survey über Techniken zur Reduzierung von Testfällen ohne Qualitätsverlust. Relevante Techniken: Redundanzentfernung, Clustering, Coverage-basierte Selektion.

**Regression Testing in CI (Elbaum, 2014):**
Techniken für effizientes Regression-Testing in Continuous-Integration-Umgebungen. Fokus: Minimierung der Testausführungszeit bei maximaler Fehlerdeckung.

**Beyond Test Cases (Martensson, 2025):**
Moderne Perspektive auf SW-Qualität: Testing ist mehr als Testfälle – Observability, Monitoring, und kontinuierliche Qualitätsmessung im Betrieb.

**Regression Testing Survey (Yoo & Harman, 2012):**
Umfassender Survey über Minimierung, Selektion und Priorisierung von Regressionstests. Standardreferenz im Bereich Test-Optimierung.

**KI für Testing – Kernprinzipien:**
- Automatisierte Testgenerierung (KI generiert Testfälle aus Spezifikation)
- Regressionstest-Priorisierung (KI identifiziert risikoreichste Tests)
- Testpflege-Automatisierung (KI aktualisiert Tests bei Code-Änderungen)
- Knowledge Graph für SW-Qualitätssicherung (aus Tag 02)

### Relevanz für HK-Tracker

| Thema | Warum relevant |
|-------|---------------|
| **Automatisierte Tests** | HK-Tracker benötigt Testabdeckung für API-Endpunkte (ASP.NET Core) und UI-Komponenten (React). KI-gestützte Testgenerierung kann Entwicklungsgeschwindigkeit erhöhen. |
| **Regression Testing CI** | GitHub Actions Pipeline für HK-Tracker: Regressionstests bei jedem Push sichern Stabilität der Kompetenzbewertungs-Logik. |
| **Test Priorisierung** | Bei begrenzten Ressourcen (Solo-Entwickler): KI priorisiert die wichtigsten Tests (Bloom-Bewertungslogik, Rotationsplanung) für maximale Sicherheitsabdeckung. |
| **Beyond Test Cases** | Monitoring und Observability des HK-Trackers im Azure-Betrieb (Application Insights) – passt zu "Messung" in Kapitel 3 der Abschlussarbeit. |

---

## Tag 08 – DevOps, Deployment & Betrieb (05.06.2026)

**Dozent:** Prof. Dr. Sebastian Graf (FHNW)  
**Dokumente:**
- `00 -Admin.pdf` (28 Seiten, vollständig gelesen)
- Tutorial-PDFs 01–04 (nicht per Tool lesbar)

### Kernthemen

**DevOps-Grundprinzipien:**
- Developer vs. Operations-Konflikt als historisches Problem: "Break the Silos"
- DevOps als kulturelle + technische Transformation
- Shift Left: Qualitätssicherung früh in den Entwicklungszyklus verlagern

**DORA Metrics (Vertiefung):**
Vier Metriken als objektive Messgrössen für DevOps-Maturity:
- **Lead Time for Changes**: Zeitspanne von Code-Commit bis Production
- **Deployment Frequency**: Wie oft wird deployed?
- **Change Failure Rate**: Anteil der Deployments, die Probleme verursachen
- **Time to Restore Service**: Wiederherstellungszeit nach Incidents

**Cloud Computing (NIST SP 800-145):**
Fünf essentielle NIST-Kriterien für Cloud:
1. On-demand Self-service
2. Broad Network Access
3. Resource Pooling
4. Rapid Elasticity
5. Measured Service

**12-Factor App:**
Best Practices für Cloud-native Applikationen (Konfiguration, Logging, Prozesse, Dependencies etc.).

**Infrastructure as Code (IaC):**
"Software eats Infrastructure" – Infrastruktur wird wie Code behandelt: versioniert, getestet, automatisiert deployed.

**Kubernetes:**
Container-Orchestrierung für skalierbare, selbstheilende Deployments.

**Agentic AI in der Infrastruktur – Sicherheitsregeln:**
Kritische Sicherheitsgrundsätze bei Einsatz von KI-Agenten in Infrastrukturtasks:
1. **Never trust the agent** – Agenten haben minimale Berechtigungen (Principle of Least Privilege)
2. **Temporary credentials only** – Keine dauerhaften Zugangsdaten für Agenten
3. **Disposable infrastructure** – Infrastruktur ist ephemer; Agenten können nichts "bleibend" beschädigen
4. **Infrastructure as Code** – Alle Infrastruktur-Änderungen über IaC, niemals manuell durch Agenten
5. **No unsupervised access** – Produktions-Deployments erfordern menschliche Freigabe

**Site Reliability Engineering (SRE):**
Google-Philosophie: Operations-Arbeit (Toil) auf <50 % halten, Rest für Engineering investieren. Erreichbarkeits-Ziele (SLOs, SLAs) als Managementinstrument.

### Relevanz für HK-Tracker

| Thema | Warum relevant |
|-------|---------------|
| **DORA Metrics** | Messrahmen für den HK-Tracker-Betrieb: Deployment Frequency und Lead Time messbar machen via GitHub Actions. Direkt für Abschlussarbeit "Messung"-Kapitel nutzbar. |
| **12-Factor App** | HK-Tracker-Backend (ASP.NET Core) sollte 12-Factor-konform konfiguriert sein für Azure App Service Deployment (Environment Variables statt config files, Health Checks). |
| **NIST Cloud-Definition** | Legitimiert Azure als Deployment-Ziel für den HK-Tracker (alle 5 NIST-Kriterien erfüllt). Nutzbar in Abschlussarbeit Kapitel "Planung". |
| **IaC** | Bicep/ARM-Templates für Azure-Infrastruktur des HK-Trackers (App Service, SQL Server, Azure OpenAI) – reproduzierbares, versioniertes Deployment. |
| **Agentic AI Sicherheitsregeln** | Direkt übertragbar auf die Azure-OpenAI-Integration im HK-Tracker: Temporäre Managed Identities, minimale API-Berechtigungen, Mensch genehmigt Kompetenzbewertungen. |
| **SRE / Toil** | Automatisierung der manuellen HK-Bewertungs-Toil durch KI – der Kernnutzen des HK-Trackers. Messung: Wie viel Zeit sparen Berufsbildner durch KI-gestützte Bewertung? |

---

## Tag 09–14 – Module (geplant, noch ohne Unterlagen)

**Status:** Ordner existieren, sind jedoch vollständig leer (Stand: 2026-06-07).

Geplante Inhalte gemäss CAS-Lehrplan (aus Tag 01 Übersicht):
- Tag 09: Stefan Hackstein – KI-Integration im Team
- Tag 10: Christopher Scherb & Norbert Seyff – Cybersecurity & SW-Evolution
- Tag 11: Eva Polini – Ethics & Law
- Tag 12: Andreas Lorenz – Erfahrungsbericht aus der Praxis
- Tag 13–14: Abschlussarbeit-Werkstatt / Präsentationsvorbereitung

---

## Zusammenfassung: Direkter Beitrag zur Abschlussarbeit

| Abschlussarbeits-Kapitel | Relevante CAS-Module |
|--------------------------|---------------------|
| **Einleitung** – Problembeschreibung | Tag 03 (Fachkräftemangel, Skill Management), Tag 03 (ISPMA), Tag 01 (DORA Survey) |
| **Einleitung** – KI-bezogene Ziele | Tag 01 (SDD), Tag 02 (Agent Harnesses), Tag 08 (Agentic AI Safety) |
| **Einleitung** – Stakeholder-Analyse | Tag 04 (RE Interview), Tag 03 (RAM nach Gorschek & Wohlin) |
| **Planung** – Wertstromanalyse | Tag 01 (DORA 2025: Value Stream Management, S. 73) |
| **Planung** – KI-Einsatz | Tag 02 (Claude Code, MCP), Tag 05 (LiteLLM Gateway), Tag 06 (Data Engineering, Vektoren) |
| **Planung** – Einführungsvorgehen | Tag 08 (12-Factor App, IaC, Cloud-Definition), Tag 05 (arc42) |
| **Umsetzung** – Tooling | Tag 02 (RARIX 4-Layer), Tag 05 (ADRs/MADR v4), Tag 08 (IaC, Kubernetes) |
| **Umsetzung** – Messung | Tag 08 (DORA Metrics), Tag 07 (Testing/CI), Tag 01 (DORA Report 2025) |
| **Umsetzung** – Stakeholder-Einbezug | Tag 04 (RE-Methodik), Tag 06 (AI4KM Feedback-Workflow) |
| **Diskussion** – Risiken / Grenzen | Tag 03 (Brain Fry, Decision Fatigue), Tag 08 (Agentic AI Sicherheit), Tag 03 (AI Slop) |

---

## Quellenverzeichnis

Alle explizit zitierten Referenzen aus den CAS-Modulunterlagen, soweit identifizierbar. Format: APA 7.

### Wissenschaftliche Artikel

**[R01]** Bahi, A., Gharib, J., & Gahi, Y. (2024). Integrating generative AI for advancing agile software development and mitigating project management challenges. *International Journal of Advanced Computer Science and Applications*, *15*(3), 54–61. https://doi.org/10.14569/IJACSA.2024.0150306

**[R02]** Doshi, A. R., & Hauser, O. P. (2024). Generative artificial intelligence enhances creativity but reduces the diversity of novel content. *[Zeitschrift ausstehend; Vollreferenz aus Originaltext prüfen]*.

**[R03]** Elbaum, S., Rothermel, G., & Penix, J. (2014). Techniques for improving regression testing in continuous integration development environments. *Proceedings of the 22nd ACM SIGSOFT International Symposium on Foundations of Software Engineering (FSE '14)*. https://doi.org/10.1145/2635868.2635910

**[R04]** Fu, M., & Tantithamthavorn, C. (2022). GPT2SP: A transformer-based agile story point estimation approach. *IEEE Transactions on Software Engineering*, *48*(11), 4416–4433. https://doi.org/10.1109/TSE.2021.3135781

**[R05]** Gorschek, T., & Wohlin, C. (2006). Requirements abstraction model. *Requirements Engineering*, *11*(1), 79–101. https://doi.org/10.1007/s00766-005-0029-0

**[R06]** Holzmann, V., Zitter, D., & Peshkess, S. (2023). The expectations of project managers from artificial intelligence: A Delphi study. *International Journal of Project Management*, *41*(7), 102526. https://doi.org/10.1016/j.ijproman.2023.102526

**[R07]** Kropp, M., Meier, A., Anslow, C., & Biddle, R. (2026). When using AI leads to "Brain Fry". *Harvard Business Review*. [Vollreferenz aus HBR-Publikation prüfen; enthält Studie mit 1'488 Vollzeitbeschäftigten, USA]

**[R08]** Mahajan, G. (2026). Operationalizing generative AI in software product management: A review of managerial use-cases, governance, and ethical guardrails. *EngrXiv*. https://doi.org/10.31224/6204

**[R09]** Martensson, T., Borg, M., & Engström, E. (2025). So much more than test cases: Perspectives on AI-augmented quality assurance. *[Konferenz/Zeitschrift aus Originaltext prüfen]*.

**[R10]** Nguyen-Duc, A., Cabrero-Daniel, B., Przybylek, A., Arora, C., Khanna, D., Herda, T., Rafiq, U., Melegati, J., Guerra, E., Kemell, K.-K., Saari, M., Zhang, Z., Le, H., Quan, T., & Abrahamsson, P. (2025). Generative artificial intelligence for software engineering—A research agenda. *Software: Practice and Experience*. https://doi.org/10.1002/spe.70005

**[R11]** Yoo, S., & Harman, M. (2012). Regression testing minimisation, selection, and prioritisation: A survey. *Software Testing, Verification and Reliability*, *22*(2), 67–120. https://doi.org/10.1002/stvr.430

**[R12]** Alegroth, E., Feldt, R., & Regnell, B. (2016). Maintenance of automated test suites in industry: An empirical study on downtime and maintenance work. *Information and Software Technology*, *73*, 1–19. https://doi.org/10.1016/j.infsof.2016.01.003

**[R13]** Alian, M. H., & Daoud, M. I. (2016). Test case reduction techniques: A survey. *International Journal of Computer Applications*, *134*(16), 12–20. https://doi.org/10.5120/ijca2016908099

### Bücher und Buchkapitel

**[R14]** Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (Eds.). (2018). *Site Reliability Engineering: How Google runs production systems* (Kapitel: Reaching Beyond). O'Reilly Media. https://sre.google/workbook/reaching-beyond/

**[R15]** Google SRE Team. (2016). Eliminating toil. In B. Beyer, C. Jones, J. Petoff, & N. R. Murphy (Eds.), *Site Reliability Engineering*. O'Reilly Media. https://sre.google/sre-book/eliminating-toil/

**[R16]** Porter, M. E. (1979). How competitive forces shape strategy. *Harvard Business Review*, *57*(2), 137–145. [Nachgeführte Ausgabe: Porter, M. E. (2008). The five competitive forces that shape strategy. *Harvard Business Review*, *86*(1), 78–93.]

### Institutionelle Dokumente & Standards

**[R17]** DORA Research Team / Google Cloud. (2025). *DORA Report 2025: State of DevOps – AI-assisted Software Development*. https://dora.dev/research/2025/dora-report/

**[R18]** NIST (National Institute of Standards and Technology). (2011). *The NIST definition of cloud computing* (NIST Special Publication 800-145). U.S. Department of Commerce. https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-145.pdf

**[R19]** ISPMA (International Software Product Management Association). (n.d.). *ISPMA Body of Knowledge*. https://ispma.org/bok/

**[R20]** IREB (International Requirements Engineering Board). (n.d.). *AI4RE Micro-Credential*. https://cpre.ireb.org/de/concept/ai4re-micro-credential

**[R21]** BCG (Boston Consulting Group). (2026, Januar). *Survey on AI tools and productivity* [Umfrage mit 1'488 Vollzeitbeschäftigten, USA]. [Genaue Publikations-URL aus BCG-Originalquelle ergänzen]

### Konferenzvorträge & Online-Ressourcen

**[R22]** Boeckeler, B. (2026, Januar). *State of play: KI-unterstützte Programmierung* [Keynote, OOP Konferenz 2026]. https://speakerdeck.com/birgitta410/state-of-play-ki-unterstutzte-programmierung-oop-2026-keynote

**[R23]** Fowler, M. (n.d.). Exploring Gen AI: SDD-3 tools [Web-Artikel]. Martin Fowler's Bliki. https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html

---

## Glossar wichtiger Abkürzungen

| Abkürzung | Bedeutung |
|-----------|-----------|
| **ADR** | Architecture Decision Record |
| **CAS** | Certificate of Advanced Studies |
| **DORA** | DevOps Research and Assessment |
| **EFZ** | Eidgenössisches Fähigkeitszeugnis |
| **HK** | Handlungskompetenz |
| **IaC** | Infrastructure as Code |
| **ISPMA** | International Software Product Management Association |
| **MCP** | Model Context Protocol |
| **NIST** | National Institute of Standards and Technology |
| **RAM** | Requirements Abstraction Model |
| **RARIX** | 4-Layer-Architektur für Claude-Code-Agent-Harnesses (FHNW) |
| **SDD** | Specification-Driven Development |
| **SRE** | Site Reliability Engineering |
| **WBS** | Work Breakdown Structure |

---

*Dieses Dokument wurde maschinell erstellt auf Basis der CAS AISE Modulunterlagen 2026 (Tags 01–08). Tags 09–14 hatten zum Zeitpunkt der Erstellung keine Unterlagen. Quellenangaben ohne DOI/URL sind aus Modul-Bibliografien übernommen und sollten vor Abgabe der Abschlussarbeit durch Originalquellen verifiziert werden.*
