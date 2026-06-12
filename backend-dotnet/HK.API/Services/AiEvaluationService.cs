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
        var docText  = ExtractText(doc.FileData, doc.ContentType, doc.FileName);
        var goals    = LoadGoals(specialty);
        var prompt   = BuildPrompt(doc.Title, doc.Description, docText, goals);
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
            .Select(p => p.InnerText) ?? [];
        return string.Join("\n", paragraphs.Where(t => !string.IsNullOrWhiteSpace(t)));
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
        foreach (var sc   in area.GetProperty("subComps").EnumerateArray())
        foreach (var g    in sc.GetProperty("goals").EnumerateArray())
        {
            goals.Add(new CompetencyGoal(
                g.GetProperty("id").GetString()   ?? "",
                g.GetProperty("text").GetString() ?? "",
                g.GetProperty("max").GetInt32()
            ));
        }

        return goals;
    }

    // ── Prompt-Aufbau ────────────────────────────────────────────────────────────

    private static string BuildPrompt(string title, string? description, string docText, List<CompetencyGoal> goals)
    {
        const int maxTextLength = 8000;
        if (docText.Length > maxTextLength)
            docText = docText[..maxTextLength] + "\n[... Text gekürzt ...]";

        var goalLines   = string.Join("\n", goals.Select(g => $"{g.Id} (max K{g.Max}): {g.Text}"));
        var descLine    = string.IsNullOrEmpty(description) ? "" : $"Beschreibung: {description}\n";
        var jsonExample = """
            {
              "kurzbeschreibung": "Kurze Beschreibung des Dokuments in 3–5 Sätzen",
              "umsetzung": "Wie wurde die Arbeit umgesetzt – Vorgehen und Methodik",
              "luecken": "Was fehlt oder könnte bei der nächsten Arbeit verbessert werden",
              "bewertungen": [
                { "goal_id": "a1.1", "bloom_level": 3, "kommentar": "Begründung in 1–2 Sätzen" }
              ]
            }
            """;

        return $"""
            ## Dokument des Lernenden
            Titel: {title}
            {descLine}
            ## Inhalt
            {docText}

            ## Bloom-Taxonomie
            {BloomDefinition}

            ## Leistungsziele
            {goalLines}

            ## Aufgabe
            Analysiere das Dokument und identifiziere die 10 am deutlichsten nachgewiesenen Leistungsziele.
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
                new { role = "system", content = "Du bist ein Kompetenz-Bewerter für die Schweizer Berufsbildung (EFZ). Antworte ausschliesslich mit einem gültigen JSON-Objekt ohne weitere Erklärungen." },
                new { role = "user", content = userPrompt }
            },
            temperature     = 0.3,
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

        var doc     = JsonDocument.Parse(body);
        var content = doc.RootElement
            .GetProperty("choices")[0]
            .GetProperty("message")
            .GetProperty("content")
            .GetString() ?? "";

        return ParseAiResponse(content);
    }

    private AiEvaluationResult? ParseAiResponse(string content)
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

            return new AiEvaluationResult(
                root.TryGetProperty("kurzbeschreibung", out var f1) ? f1.GetString() ?? "" : "",
                root.TryGetProperty("umsetzung",        out var f2) ? f2.GetString() ?? "" : "",
                root.TryGetProperty("luecken",          out var f3) ? f3.GetString() ?? "" : "",
                bewertungen
            );
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "AI-Antwort konnte nicht geparst werden: {Content}", content);
            return null;
        }
    }

    private record CompetencyGoal(string Id, string Text, int Max);
}

public record AiEvaluationResult(
    string Kurzbeschreibung,
    string Umsetzung,
    string Luecken,
    IEnumerable<AiGoalBewertung> Bewertungen
);

public record AiGoalBewertung(string GoalId, int BloomLevel, string Kommentar);
