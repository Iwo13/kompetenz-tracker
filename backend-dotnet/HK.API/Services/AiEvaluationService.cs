using System.Text;
using System.Text.Json;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;
using HK.Domain.Entities;
using UglyToad.PdfPig;
using WpDocument = DocumentFormat.OpenXml.Wordprocessing.Document;
using DomDocument = HK.Domain.Entities.Document;

namespace HK.API.Services;

public class AiEvaluationService(IConfiguration config, ILogger<AiEvaluationService> logger, HttpClient httpClient)
{
    private const string BloomDefinition = """
        K1 – Wissen: Fakten und Definitionen wiedergeben
        K2 – Verstehen: Sachverhalte erklären und beschreiben
        K3 – Anwenden: Wissen in neuen Situationen anwenden
        K4 – Analysieren: Strukturen erkennen, Zusammenhänge analysieren
        K5 – Synthese: Eigene Lösungen entwickeln, Neues gestalten
        K6 – Beurteilen: Qualität kritisch einschätzen, Entscheidungen begründen
        """;

    public bool IsConfigured =>
        !string.IsNullOrEmpty(config["AzureAi:Endpoint"]) &&
        !string.IsNullOrEmpty(config["AzureAi:ApiKey"]);

    public async Task<AiEvaluationResult?> EvaluateAsync(DomDocument doc, string specialty)
    {
        var docText = ExtractText(doc.FileData, doc.ContentType, doc.FileName);
        var goals   = LoadGoals(specialty);
        var prompt  = BuildPrompt(docText, goals);
        return await CallAiAsync(prompt);
    }

    // ── Textextraktion ───────────────────────────────────────────────────────────

    private string ExtractText(byte[] data, string contentType, string fileName)
    {
        try
        {
            if (contentType.Contains("pdf") || fileName.EndsWith(".pdf", StringComparison.OrdinalIgnoreCase))
                return ExtractPdf(data);

            if (contentType.Contains("wordprocessingml") || contentType.Contains("msword") ||
                fileName.EndsWith(".docx", StringComparison.OrdinalIgnoreCase))
                return ExtractDocx(data);

            if (contentType.StartsWith("text/"))
                return Encoding.UTF8.GetString(data);
        }
        catch (Exception ex)
        {
            logger.LogWarning(ex, "Textextraktion fehlgeschlagen für {FileName}", fileName);
        }
        return $"[Datei: {fileName} – Inhalt konnte nicht extrahiert werden]";
    }

    private static string ExtractPdf(byte[] data)
    {
        var sb = new StringBuilder();
        using var pdf = PdfDocument.Open(data);
        foreach (var page in pdf.GetPages())
        {
            foreach (var word in page.GetWords())
                sb.Append(word.Text).Append(' ');
            sb.AppendLine();
        }
        return sb.ToString();
    }

    private static string ExtractDocx(byte[] data)
    {
        using var stream = new MemoryStream(data);
        using var doc    = WordprocessingDocument.Open(stream, false);
        var paragraphs   = doc.MainDocumentPart?.Document?.Body?
            .Descendants<Paragraph>()
            .Where(p => !IsHeadingParagraph(p))
            .Select(p => p.InnerText) ?? [];
        return string.Join("\n", paragraphs.Where(t => !string.IsNullOrWhiteSpace(t)));
    }

    private static bool IsHeadingParagraph(Paragraph p)
    {
        var styleId = p.ParagraphProperties?.ParagraphStyleId?.Val?.Value ?? "";
        return styleId.StartsWith("Heading",    StringComparison.OrdinalIgnoreCase) ||
               styleId.StartsWith("berschrift", StringComparison.OrdinalIgnoreCase);
    }

    // ── Leistungsziele laden ─────────────────────────────────────────────────────

    private List<CompetencyGoal> LoadGoals(string specialty)
    {
        var file = specialty == "ict-fachmann"
            ? "kompetenzen-ict-fachmann-efz"
            : "kompetenzen-informatiker-efz";
        var dir  = config["DataPaths:CompetenciesDir"] ?? "../../data";
        var path = Path.GetFullPath(Path.Combine(Directory.GetCurrentDirectory(), dir, $"{file}.json"));

        if (!File.Exists(path))
        {
            logger.LogWarning("Kompetenz-Datei nicht gefunden: {Path}", path);
            return [];
        }

        var json  = File.ReadAllText(path, Encoding.UTF8);
        var root  = JsonDocument.Parse(json).RootElement;
        var goals = new List<CompetencyGoal>();

        foreach (var area in root.GetProperty("areas").EnumerateArray())
        {
            var areaSpecialty = area.TryGetProperty("specialty", out var sp) ? sp.GetString() : "both";
            if (areaSpecialty != "both" && areaSpecialty != specialty) continue;

            foreach (var sc in area.GetProperty("subComps").EnumerateArray())
            foreach (var g  in sc.GetProperty("goals").EnumerateArray())
            {
                goals.Add(new CompetencyGoal(
                    g.GetProperty("id").GetString()   ?? "",
                    g.GetProperty("text").GetString() ?? "",
                    g.GetProperty("max").GetInt32()
                ));
            }
        }

        return goals;
    }

    // ── Prompt-Aufbau ────────────────────────────────────────────────────────────

    private static string BuildPrompt(string docText, List<CompetencyGoal> goals)
    {
        const int maxTextLength = 8000;
        if (docText.Length > maxTextLength)
            docText = docText[..maxTextLength] + "\n[... Text gekürzt ...]";

        var goalLines   = string.Join("\n", goals.Select(g => $"{g.Id} (max K{g.Max}): {g.Text}"));
        var jsonExample = """
            {
              "kurzbeschreibung": "Kurze Beschreibung der geleisteten Arbeit in 3–5 Sätzen – nicht das Dokument beschreiben, sondern die erstellte Lösung, Applikation oder Umsetzung. Beginne mit der Arbeit selbst, z.B. 'Die erstellte Anwendung...', 'Im Rahmen des Projekts wurde...' oder 'Ziel war es, ...'",
              "umsetzung": "Wie wurde die Arbeit umgesetzt – Vorgehen und Methodik",
              "luecken": "Was fehlt oder könnte bei der nächsten Arbeit verbessert werden",
              "technologien": ["Python", "Django"],
              "umgebungen": ["Azure", "SQL Server"],
              "bewertungen": [
                { "goal_id": "a1.1", "bloom_level": 3, "kommentar": "Begründung in 1–2 Sätzen" }
              ]
            }
            """;

        return $"""
            ## Inhalt des Dokuments
            {docText}

            ## Bloom-Taxonomie
            {BloomDefinition}

            ## Leistungsziele
            {goalLines}

            ## Aufgabe
            Analysiere das Dokument und:
            1. Identifiziere die 10 am deutlichsten nachgewiesenen Leistungsziele.
            2. Extrahiere als "technologien" nur Programmiersprachen und Frameworks, die der Lernende nachweislich selbst aktiv eingesetzt hat (z.B. Code geschrieben, konfiguriert, debuggt). Nicht aufnehmen: Technologien, die nur im Hintergrund laufen, nur erwähnt werden oder vom System automatisch genutzt werden.
            3. Extrahiere als "umgebungen" nur Systeme und Plattformen, mit denen der Lernende direkt gearbeitet hat (z.B. bewusst eingerichtet, deployed, administriert). Nicht aufnehmen: Systeme, die nur indirekt beteiligt sind oder die der Lernende nicht selbst bedient hat.
            Bewertungsmassstab:
            - Nur Leistungsziele bewerten, für die das Dokument konkrete eigene Leistung zeigt (Analyse, Entscheidung, Reflexion des Lernenden)
            - Tools, Frameworks oder KI-Unterstützung, die der Lernende eingesetzt hat, erhöhen den Bloom-Level NICHT automatisch
            - Bei unklarer Evidenz: niedrigeren Level wählen
            Antworte AUSSCHLIESSLICH mit folgendem JSON-Objekt (kein Markdown, kein Fliesstext):
            {jsonExample}
            Wichtig: bloom_level darf den max-Wert des jeweiligen Leistungsziels nicht überschreiten.
            """;
    }

    // ── Azure AI Foundry Call ────────────────────────────────────────────────────

    private async Task<AiEvaluationResult?> CallAiAsync(string userPrompt)
    {
        var endpoint = config["AzureAi:Endpoint"]!;
        var apiKey   = config["AzureAi:ApiKey"]!;

        var requestBody = new
        {
            messages = new[]
            {
                new { role = "system", content = "Du bist ein kritischer Kompetenz-Bewerter für die Schweizer Berufsbildung (EFZ). Deine Aufgabe ist es, nur jene Kompetenzen zu bewerten, die der Lernende nachweislich SELBST erbracht hat. Wichtige Grundsätze: (1) Sei konservativ – weise einen Bloom-Level nur zu, wenn er im Dokument klar belegt ist. Im Zweifelsfall lieber eine Stufe tiefer. (2) Der Einsatz von Frameworks, Bibliotheken, KI-Tools oder Generatoren (z.B. Electron, React, GitHub Copilot, ChatGPT) ist KEIN eigenständiger Kompetenznachweis. Entscheidend ist, ob der Lernende das Warum und Wie selbst erklärt und reflektiert. (3) Verwende keine Personennamen. (4) Antworte ausschliesslich mit einem gültigen JSON-Objekt ohne weitere Erklärungen." },
                new { role = "user", content = userPrompt }
            },
            response_format = new { type = "json_object" }
        };

        var json    = JsonSerializer.Serialize(requestBody);
        var request = new HttpRequestMessage(HttpMethod.Post, endpoint)
        {
            Content = new StringContent(json, Encoding.UTF8, "application/json")
        };
        request.Headers.Add("api-key", apiKey);

        HttpResponseMessage response;
        try { response = await httpClient.SendAsync(request); }
        catch (Exception ex)
        {
            logger.LogError(ex, "HTTP-Fehler beim Azure AI Aufruf");
            return null;
        }

        var body = await response.Content.ReadAsStringAsync();
        if (!response.IsSuccessStatusCode)
        {
            logger.LogError("Azure AI Fehler {Status}: {Body}", response.StatusCode, body);
            return null;
        }

        var root    = JsonDocument.Parse(body).RootElement;
        var content = root
            .GetProperty("choices")[0]
            .GetProperty("message")
            .GetProperty("content")
            .GetString() ?? "";

        int promptTokens     = 0, completionTokens = 0, totalTokens = 0;
        if (root.TryGetProperty("usage", out var usage))
        {
            promptTokens     = usage.TryGetProperty("prompt_tokens",     out var p) ? p.GetInt32() : 0;
            completionTokens = usage.TryGetProperty("completion_tokens", out var c) ? c.GetInt32() : 0;
            totalTokens      = usage.TryGetProperty("total_tokens",      out var t) ? t.GetInt32() : 0;
        }

        return ParseAiResponse(content, promptTokens, completionTokens, totalTokens);
    }

    private AiEvaluationResult? ParseAiResponse(string content, int promptTokens, int completionTokens, int totalTokens)
    {
        try
        {
            var root = JsonDocument.Parse(content).RootElement;

            var bewertungen = new List<AiGoalBewertung>();
            if (root.TryGetProperty("bewertungen", out var arr))
            {
                foreach (var b in arr.EnumerateArray())
                {
                    var goalId    = b.GetProperty("goal_id").GetString() ?? "";
                    var bloom     = b.GetProperty("bloom_level").GetInt32();
                    var kommentar = b.TryGetProperty("kommentar", out var k) ? k.GetString() ?? "" : "";
                    if (!string.IsNullOrEmpty(goalId))
                        bewertungen.Add(new AiGoalBewertung(goalId, bloom, kommentar));
                }
            }

            var technologien = ParseStringArray(root, "technologien");
            var umgebungen   = ParseStringArray(root, "umgebungen");

            return new AiEvaluationResult(
                root.TryGetProperty("kurzbeschreibung", out var f1) ? f1.GetString() ?? "" : "",
                root.TryGetProperty("umsetzung",        out var f2) ? f2.GetString() ?? "" : "",
                root.TryGetProperty("luecken",          out var f3) ? f3.GetString() ?? "" : "",
                technologien,
                umgebungen,
                bewertungen,
                promptTokens,
                completionTokens,
                totalTokens
            );
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "AI-Antwort konnte nicht geparst werden: {Content}", content);
            return null;
        }
    }

    private static List<string> ParseStringArray(JsonElement root, string property)
    {
        if (!root.TryGetProperty(property, out var arr) || arr.ValueKind != JsonValueKind.Array)
            return [];
        return arr.EnumerateArray()
            .Select(e => e.GetString()?.Trim())
            .Where(s => !string.IsNullOrEmpty(s))
            .Select(s => s!)
            .ToList();
    }

    private record CompetencyGoal(string Id, string Text, int Max);
}

public record AiEvaluationResult(
    string Kurzbeschreibung,
    string Umsetzung,
    string Luecken,
    IEnumerable<string> Technologien,
    IEnumerable<string> Umgebungen,
    IEnumerable<AiGoalBewertung> Bewertungen,
    int PromptTokens,
    int CompletionTokens,
    int TotalTokens
);

public record AiGoalBewertung(string GoalId, int BloomLevel, string Kommentar);
