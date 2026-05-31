# UI-Design-Diskussion: Ausbildungsplatz-Kompetenzabdeckung
## Handlungskompetenz-Tracker – CAS AI Software Engineering

**Autor:** Iwo Kuhn, Corporate IT FHNW  
**Datum:** Mai/Juni 2026  
**Kontext:** Design-Entscheidungsprozess für die Funktion «Kompetenzabdeckung Ausbildungsplätze» im Rahmen der CAS-Arbeit

---

## 1. Ausgangslage

### 1.1 Bestehende Implementierung

Als Startpunkt existierte eine einfache **Matrix-Ansicht auf Bereichsebene** (A–H):

- 12 Ausbildungsplätze (Zeilen) × 8 Handlungskompetenzbereiche (Spalten) = **96 Zellen**
- Drei Zustände pro Zelle: `○ Nicht zugeordnet` / `◐ Sekundär` / `● Primär`
- Datenbasis: Extrahiert aus dem XLSX «ICT Kompetenzen an den Ausbildungsplätzen» der CIT FHNW
- Interaktion: Klick auf Zelle rotiert durch die drei Zustände, Auto-Save via PUT-Endpoint

**Einschränkung:** Die Zuordnung geschah auf Ebene der Kompetenzbereiche (A, B, C…), nicht auf Ebene der einzelnen Handlungskompetenzen (a1, a2, a3…). Dies war zu grob für eine sinnvolle Ausbildungssteuerung.

### 1.2 Datenquelle

Das XLSX enthält die Abdeckung bereits auf Handlungskompetenz-Ebene:
- `X` = volle Abdeckung (Primär)
- `(X)` = teilweise Abdeckung (Sekundär)
- Leer = keine Abdeckung

Die Extraktion für die erste Version verwendete nur die **Bereichs-Kopfzeilen**, nicht die darunterliegenden Handlungskompetenzen.

---

## 2. Problemstellung und Designfragen

### 2.1 Bedürfnis nach mehr Granularität

Der Wunsch war, die Zuordnung **eine Stufe tiefer** zu ermöglichen — auf Ebene der Handlungskompetenzen (a1, a2, a3…). Dies entspricht der fachlichen Realität: Ein Ausbildungsplatz wie «Software Engineering (SWE)» deckt nicht den gesamten Bereich G ab, sondern gezielt bestimmte Handlungskompetenzen.

### 2.2 Frage: Dedizierter Assistent?

**Frage:** Wäre es sinnvoll, einen dedizierten KI-Assistenten mit spezifischen Skills beizuziehen?

**Entscheidung: Nein.** Begründung:
- Die Aufgabe ist klar genug umgrenzt
- Ein neuer Agent müsste Kontext (XLSX-Struktur, Datenmodell, React-Setup) kalt neu ableiten
- Der vorhandene Gesprächskontext enthält bereits alle relevanten Informationen
- Direkter Ansatz ist effizienter

### 2.3 Abwägung der Granularitäts-Optionen

| Ebene | Zellen in Matrix | Beurteilung |
|-------|-----------------|-------------|
| Bereichsebene A–H (Ist-Zustand) | 12 × 8 = **96** | Übersichtlich, aber zu grob |
| Handlungskompetenz-Ebene a1, a2… | 12 × ~43 = **~516** | Fachlich korrekt, als flache Matrix nicht lesbar |

**Schlussfolgerung:** Die HK-Ebene ist fachlich richtig, erfordert aber ein anderes UI-Konzept als eine flache Matrix.

---

## 3. UI-Optionen

Drei Varianten wurden evaluiert:

### Option A – Expandierbare Matrix
Gleiche Tabelle wie heute, Klick auf Bereich-Header klappt Unterzeilen mit Handlungskompetenzen auf.

**Problem:** Bei 43 Unterzeilen wird die Tabelle zu breit und unübersichtlich.

### Option B – Detailansicht pro AP *(empfohlen)*
Klick auf einen AP öffnet eine dedizierte Seite mit Akkordeon-Struktur:
- Bereichs-Ebene als aufklappbare Blöcke
- Handlungskompetenzen als Zeilen mit ○/◐/● Toggle

**Vorteil:** Kompakt, kein Quervergleich nötig, konsistent mit bestehender Lernenden-Ansicht.

### Option C – Zwei Ebenen getrennt
Matrix auf Bereichsebene bleibt für den Überblick; zusätzlich pro AP ein «Detailieren»-Button.

**Vorteil:** Flexibel, bestehende Funktionalität bleibt erhalten.

---

## 4. Entwurf des Benutzers (Mockup-Review)

### 4.1 Beschreibung Mockup

Der Benutzer brachte einen eigenen visuellen Entwurf ein, der auf zwei PNG-Screens basiert:

**Screen 1 – Übersichtsansicht (Ausbildungsplatz gewählt)**

- Header: AP-Name als Dropdown (analog Lernenden-Dropdown), z.B. «Software Engineering ▾»
- Sidebar:
  - Navigation: Übersicht
  - **AUSBILDUNGSPLÄTZE VERWALTEN** mit Einträgen pro Bildungsplan/Fachrichtung inkl. %-Badge
  - Administration: Lernende / Lernende Aufnehmen / Ausbildungsplätze verwalten
- Hauptinhalt: Kacheln pro Bildungsplan mit Fortschrittsbalken
  - «Informatiker/in Plattformentwicklung – 13.5 / 33»
  - «Informatiker/in Applikationsentwicklung – 11.5 / 25»
  - «ICT-Fachmann/frau – 8 / 15»

**Screen 2 – Bildungsplan-Detailansicht (SWE + Informatiker/in)**

- Kopfbereich: SWE-Badge + «Bildungsplan Informatiker/in» + Zusammenfassung rechts oben
- Akkordeon-Bereiche:
  - Bereichs-Header: Buchstabe + Name + Fachrichtungen kursiv + Zähler (x/total) + +/× Toggle
  - Aufgeklappter Bereich A zeigt Handlungskompetenzen a1–a7 je mit ○/◐/●
  - Nicht aufgeklappte Bereiche B–H mit + Symbol
- Zähler: z.B. «4.5 / 7» (initial)

### 4.2 Stärken des Entwurfs

- **Konsistenz:** Identische visuelle Sprache wie die Lernenden-Ansicht (Akkordeon, ○/◐/●)
- **Hierarchie:** AP → Bildungsplan → Bereich → HK — jede Ebene hat eine dedizierte Ansicht
- **Kontext:** Fachrichtungen kursiv in Bereichs-Header zeigen Relevanz ohne Platzbedarf
- **Zusammenfassung:** Abdeckungs-Stats pro Fachrichtung rechts oben geben Sofortüberblick
- **AP-Dropdown:** Analog zum Lernenden-Dropdown — keine neue Bedienlogik nötig

---

## 5. Klärungen und Designentscheide

### 5.1 Zählmethode

**Frage:** Wie wird Abdeckung berechnet? Zählt Sekundär (◐) halb (→ 4.5/7)?

**Entscheid:** **Nur Primär (●) zählt als abgedeckt.**
- ◐ (Sekundär) bleibt sichtbar als «wird gestreift», beeinflusst den Zähler nicht
- Zähler zeigen damit ganzzahlige Werte (5/7 statt 4.5/7)
- Klarer, kein Interpretationsspielraum

**Begründung:** Primäre Abdeckung bedeutet, dass die Handlungskompetenz am Ausbildungsplatz systematisch gefördert wird. Sekundäre Abdeckung ist wertvoll als Information, aber nicht als Erfüllungskriterium.

### 5.2 Benennung der Sidebar-Sektionen

**Problem:** Zwei AP-bezogene Einträge in der Sidebar könnten zu Verwechslungen führen.

**Entscheid:**

| Sidebar-Eintrag | Bedeutung | Zielgruppe |
|----------------|-----------|------------|
| **Kompetenzabdeckung Ausbildungsplätze** | Fachliche Sicht: Welche Kompetenzen kann ein AP abdecken? | Berufsbildner/in |
| **Erlangte Kompetenzen** *(analog, Lernenden-Seite)* | Lernfortschritt: Welche Kompetenzen hat ein/e Lernende/r erreicht? | Lernende/r |
| **Ausbildungsplätze verwalten** | Stammdaten: AP konfigurieren, anlegen | Administrator |

Gleiche visuelle Sprache, klar unterschiedliche Semantik:
- *Abdeckung* = Kapazität des Ausbildungsplatzes (was kann erworben werden)
- *Erlangt* = Leistung der lernenden Person (was wurde tatsächlich erworben)

### 5.3 Bildungsplan-unabhängiges Mapping

**Frage:** Ist ein AP an einen bestimmten Bildungsplan gebunden, oder kann er Kompetenzen bildungsplan-übergreifend abdecken?

**Entscheid:** **Der AP ist Bildungsplan-unabhängig.**

- Ein AP wie SWE hat eine eigene, fixe Liste von Handlungskompetenzen (HK-IDs), die er abdeckt
- Diese HK-IDs können aus jedem Bildungsplan stammen (Informatiker AE, PLT, ICT-Fachmann)
- Die Übersichts-Kacheln zeigen die **Schnittmenge** pro Bildungsplan: «Wie gut passt dieser AP für Bildungsplan X?»
- Praktische Konsequenz: Ein Lernender ICT-Fachmann an SWE sieht nur die für ihn relevante Schnittmenge

**Architektonische Implikation:**

```
Datenstruktur (alt):  AP → Bereiche (A-H) → primary/secondary
Datenstruktur (neu):  AP → HK-Liste [{hk_id, coverage}]
                      HK-ID kann aus beliebigem Bildungsplan stammen
```

---

## 6. Finale UI-Definition

### 6.1 Navigation und Struktur

```
Berufsbildner-Sidebar:
├── NAVIGATION
│   └── Übersicht
├── KOMPETENZABDECKUNG AUSBILDUNGSPLÄTZE
│   ├── [AP-Auswahl via Dropdown oben, analog Lernenden-Dropdown]
│   ├── Informatiker/in
│   │   ├── - Applikationsentwicklung  [xx%]
│   │   └── - Plattformentwicklung     [xx%]
│   └── ICT-Fachmann                   [xx%]
└── ADMINISTRATION
    ├── Lernende
    ├── Lernende Aufnehmen
    └── Ausbildungsplätze verwalten
```

### 6.2 Screen-Flows

**Flow 1: AP auswählen**
- Header-Dropdown (identisch zu Lernenden-Dropdown) → AP wählen
- Übersichtsseite zeigt Kacheln pro Bildungsplan mit Abdeckungs-Score

**Flow 2: Bildungsplan-Detail**
- Klick auf Kachel → Akkordeon mit Bereichen A–H
- Bereichs-Header: «A Begleiten von ICT-Projekten – *Applikationsentwicklung / Plattformentwicklung* – 5/7 ×»
- Aufgeklappt: Handlungskompetenzen a1–a7 mit Toggle ○/◐/●
- Auto-Save bei Klick (kein Speichern-Button)

**Flow 3: Neuen AP erfassen**
- Via AP-Dropdown: «+ Neuen Ausbildungsplatz erfassen» (analog «+ Lernende/n erfassen»)

### 6.3 Zähl- und Anzeigelogik

| Symbol | Bedeutung | Zählt als abgedeckt |
|--------|-----------|---------------------|
| ● | Primär – wird systematisch gefördert | **Ja** |
| ◐ | Sekundär – wird gestreift/begleitend behandelt | Nein |
| ○ | Nicht abgedeckt | Nein |

Score-Berechnung: `Anzahl ● / Gesamtzahl HK im Bereich`

### 6.4 Designprinzipien

- **Konsistenz vor Originalität:** Dieselbe visuelle Sprache wie die Lernenden-Erfassung
- **Auto-Save:** Kein expliziter Speichern-Button; Änderung wird sofort persistiert
- **Eckige Ecken:** Konsequent FHNW Corporate Identity (kein border-radius)
- **Farbkodierung:** ● = FHNW-Gelb (#FDE70E), ◐ = Hellgelb (#FFF48D), ○ = Grau
- **Schrift:** Inter (Google Fonts), FHNW-konform

---

## 7. Abgrenzung zur Lernenden-Ansicht

| Aspekt | Lernenden-Ansicht | AP-Abdeckungsansicht |
|--------|------------------|----------------------|
| **Zweck** | Fortschritt dokumentieren | Lehrkapazität konfigurieren |
| **Akteur** | Lernende/r (eigene Bewertung) | Berufsbildner/in (Systemkonfiguration) |
| **Daten** | Erreichte Kompetenzstufe (K0–K6) | Abdeckung (●/◐/○) |
| **Persistenz** | GoalEntry in DB (pro Lernende/r) | AP-HK-Mapping in JSON/DB |
| **Sidebar** | «Erlangte Kompetenzen» | «Kompetenzabdeckung Ausbildungsplätze» |
| **Zugriff** | Lernende/r + Berufsbildner/in | Nur Berufsbildner/in |

---

*Dieses Dokument fasst den iterativen Design-Diskussionsprozess zwischen Iwo Kuhn und Claude (Anthropic) im Rahmen der CAS AI Software Engineering Arbeit zusammen. Die Umsetzung erfolgt im nächsten Entwicklungsschritt.*
