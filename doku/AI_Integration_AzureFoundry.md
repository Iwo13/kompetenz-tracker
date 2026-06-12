# AI-Integration: Azure AI Foundry – Dokumentenbewertung

## Übersicht

Lernende können Dokumente hochladen und automatisch anhand der Handlungskompetenzen (Leistungsziele) und der Bloom-Taxonomie durch eine KI bewerten lassen. Die Bewertung füllt die Felder Kurzbeschreibung, Umsetzung und Lücken aus und schlägt die 10 am stärksten nachgewiesenen Leistungsziele mit Bloom-Stufe und Kommentar vor. Der Lernende kann das Ergebnis anschliessend anpassen und manuell speichern.

---

## Architektur

```
Browser (React)
    │
    │  POST /users/{userId}/documents/{docId}/ai-evaluate
    ▼
ASP.NET Core Backend (HK.API)
    │
    │  AiEvaluationService
    │   1. Textextraktion aus Datei (PDF / DOCX / Text)
    │   2. Leistungsziele aus JSON laden (nach Lehrberuf)
    │   3. Prompt aufbauen
    │   4. Azure AI Foundry aufrufen
    │   5. JSON-Antwort parsen
    │   6. Dokument in DB aktualisieren
    ▼
Azure AI Foundry (FHNW Azure Tenant, Switzerland North)
```

Das API-Token bleibt **ausschliesslich server-seitig**. Der Browser sieht den Key nie.

---

## Konfiguration (`appsettings.json`)

```json
"AzureAi": {
  "Endpoint": "https://<resource-name>.openai.azure.com/openai/deployments/<deployment-name>/chat/completions?api-version=2024-08-01-preview",
  "ApiKey":   "<api-key-aus-azure-foundry>"
}
```

| Parameter    | Beschreibung                                                                 |
|--------------|------------------------------------------------------------------------------|
| `Endpoint`   | Vollständige URL inkl. Deployment-Name und API-Version                       |
| `ApiKey`     | API-Key aus Azure AI Foundry (Portal → Keys and Endpoint)                    |

> **Hinweis:** Ist `Endpoint` oder `ApiKey` leer, bleibt die AI-Funktion deaktiviert (400-Fehler). Die App funktioniert weiterhin vollständig im manuellen Modus.

---

## Datenbankfluss beim AI-Aufruf

1. Backend liest `Document.FileData` (bereits gespeichert beim Upload)
2. Backend liest `User.Specialty` → bestimmt die richtige Leistungsziele-Datei
3. Nach erfolgreicher AI-Antwort werden folgende Felder überschrieben:
   - `Document.Kurzbeschreibung`
   - `Document.Umsetzung`
   - `Document.Luecken`
   - Alle `DocumentGoalLinks` werden durch die 10 AI-vorgeschlagenen ersetzt (mit `BloomLevel` und `Einschaetzung`)

---

## Textextraktion

| Dateityp           | Bibliothek                 | NuGet-Paket                     |
|--------------------|----------------------------|---------------------------------|
| PDF (`.pdf`)       | UglyToad.PdfPig            | `UglyToad.PdfPig` (prerelease)  |
| Word (`.docx`)     | DocumentFormat.OpenXml     | `DocumentFormat.OpenXml` 3.*    |
| Plaintext          | UTF-8 Dekodierung          | (kein extra Paket)              |
| Andere             | Nur Dateiname als Kontext  | –                               |

Der extrahierte Text wird auf **8 000 Zeichen** begrenzt, um den Kontext des Modells nicht zu überschreiten.

---

## Prompt-Aufbau

Der Prompt enthält in dieser Reihenfolge:

1. **Dokument-Header**: Titel und Untertitel
2. **Extrahierter Inhalt** (max. 8 000 Zeichen)
3. **Bloom-Taxonomie** (K1–K6 mit Kurzdefinition)
4. **Leistungsziele** des entsprechenden Lehrberufs, Format: `ID (max Kx): Beschreibungstext`
5. **Aufgabenstellung**: JSON-Schema, das die KI ausfüllen soll

Das System-Prompt instruiert das Modell, **ausschliesslich ein JSON-Objekt** zurückzugeben (kein Markdown, kein Fliesstext). Das Feld `response_format: { type: "json_object" }` erzwingt dies zusätzlich auf API-Ebene.

---

## Leistungsziele-Dateien

Die KI-Bewertung basiert auf denselben JSON-Dateien wie die manuelle Auswahl:

| Lehrberuf                  | Datei                              |
|----------------------------|------------------------------------|
| Informatiker EFZ (App/Plattform) | `data/kompetenzen-informatiker-efz.json` |
| ICT-Fachmann EFZ           | `data/kompetenzen-ict-fachmann-efz.json` |

Der Lehrberuf wird automatisch anhand von `User.Specialty` gewählt.

---

## API-Aufruf (Azure OpenAI / AI Foundry)

```http
POST https://<endpoint>/openai/deployments/<deployment>/chat/completions?api-version=2024-08-01-preview
api-key: <ApiKey>
Content-Type: application/json

{
  "messages": [
    { "role": "system", "content": "..." },
    { "role": "user",   "content": "..." }
  ],
  "temperature": 0.3,
  "response_format": { "type": "json_object" }
}
```

**Erwartetes Antwort-JSON:**
```json
{
  "kurzbeschreibung": "...",
  "umsetzung": "...",
  "luecken": "...",
  "bewertungen": [
    { "goal_id": "a1.1", "bloom_level": 3, "kommentar": "..." },
    ...
  ]
}
```

Es werden maximal **10 Bewertungen** übernommen. Der `bloom_level` wird auf den Max-Wert des Leistungsziels begrenzt (`Math.Clamp(1, 6)`).

---

## Frontend-Verhalten

- Der Button **"✦ AI-Analyse starten"** erscheint nur, wenn das Dokument mit `Bewertungsart = "ai"` hochgeladen wurde.
- Während der Analyse: Button zeigt "⏳ AI analysiert…" und ist deaktiviert.
- Nach erfolgreicher Analyse werden alle Felder und Leistungsziele **sofort im UI sichtbar** (Accordeon bleibt offen).
- Der Lernende kann Werte anpassen und mit **"Bewertung Speichern"** auf das Kompetenzprofil übertragen.
- Bei Fehler: rote Fehlermeldung unterhalb der Toolbar.

---

## Offene Punkte / Nächste Schritte

| Thema | Status |
|-------|--------|
| Azure AI Foundry Instanz im FHNW-Tenant anlegen | Offen – IT-Admin anfragen |
| `Endpoint` und `ApiKey` in `appsettings.json` eintragen | Offen |
| Managed Identity statt API-Key (Produktion) | Geplant – nach IT-Freigabe |
| Unterstützung für Bilder / PowerPoint | Nicht implementiert |
| Mehrsprachige Dokumente | Nicht getestet |
