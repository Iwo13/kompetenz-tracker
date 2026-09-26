using HK.API.Services;
using HK.Application.DTOs;
using HK.Domain.Entities;
using HK.Infrastructure.Persistence;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace HK.API.Controllers;

[ApiController]
[Route("users/{userId:guid}/documents")]
public class UserDocumentsController(AppDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IEnumerable<DocumentResponse>> GetAll(Guid userId)
    {
        // FileData (Binärinhalt) wird bewusst nicht geladen — nur Metadaten für die Listenansicht
        var rows = await db.Documents
            .Where(d => d.UserId == userId)
            .OrderByDescending(d => d.UploadedAt)
            .Select(d => new {
                d.Id, d.UserId, d.ApCode, d.Title, d.Description,
                d.Kurzbeschreibung, d.Umsetzung, d.Luecken, d.Bewertungsart, d.FeedbackBerufsbildner,
                d.Technologies, d.Environments,
                d.FileName, d.ContentType, d.FileSize, d.UploadedAt, d.DocumentDate,
                GoalLinks = d.GoalLinks.Select(l => new { l.Id, l.GoalId, l.Einschaetzung, l.BloomLevel }),
            })
            .ToListAsync();

        return rows.Select(d => new DocumentResponse(
            d.Id, d.UserId, d.ApCode, d.Title, d.Description,
            d.Kurzbeschreibung, d.Umsetzung, d.Luecken, d.Bewertungsart, d.FeedbackBerufsbildner,
            SplitTags(d.Technologies), SplitTags(d.Environments),
            d.FileName, d.ContentType, d.FileSize, d.UploadedAt, d.DocumentDate,
            d.GoalLinks.Select(l => new DocumentGoalLinkDto(l.Id, l.GoalId, l.Einschaetzung, l.BloomLevel))
        ));
    }

    [HttpPost]
    [RequestSizeLimit(50 * 1024 * 1024)]
    public async Task<ActionResult<DocumentResponse>> Create(
        Guid userId,
        [FromForm] string title,
        [FromForm] string apCode,
        [FromForm] string? description,
        [FromForm] string? goalIds,
        [FromForm] string? bewertungsart,
        [FromForm] string? documentDate,
        IFormFile file)
    {
        if (file is null || file.Length == 0)
            return BadRequest("Keine Datei hochgeladen.");

        using var ms = new MemoryStream();
        await file.CopyToAsync(ms);

        var doc = new Document
        {
            UserId        = userId,
            ApCode        = apCode,
            Title         = title.Trim(),
            Description   = description?.Trim(),
            Bewertungsart = bewertungsart?.Trim() ?? "manuell",
            FileName      = file.FileName,
            ContentType   = file.ContentType,
            FileData      = ms.ToArray(),
            FileSize      = file.Length,
            DocumentDate  = ParseDate(documentDate),
        };

        if (!string.IsNullOrWhiteSpace(goalIds))
        {
            foreach (var gid in goalIds.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
                doc.GoalLinks.Add(new DocumentGoalLink { GoalId = gid, BloomLevel = 1 });
        }

        db.Documents.Add(doc);
        await db.SaveChangesAsync();
        return CreatedAtAction(nameof(GetAll), new { userId }, ToResponse(doc));
    }

    [HttpPut("{docId:guid}")]
    public async Task<ActionResult<DocumentResponse>> Update(
        Guid userId, Guid docId, UpdateDocumentRequest req)
    {
        var doc = await db.Documents
            .Include(d => d.GoalLinks)
            .FirstOrDefaultAsync(d => d.Id == docId && d.UserId == userId);
        if (doc is null) return NotFound();

        doc.Title                  = req.Title.Trim();
        doc.Description            = req.Description?.Trim();
        doc.ApCode                 = req.ApCode;
        doc.Kurzbeschreibung       = req.Kurzbeschreibung?.Trim();
        doc.Umsetzung              = req.Umsetzung?.Trim();
        doc.Luecken                = req.Luecken?.Trim();
        doc.FeedbackBerufsbildner  = req.FeedbackBerufsbildner?.Trim();
        doc.DocumentDate           = ParseDate(req.DocumentDate);

        var existing  = doc.GoalLinks.Select(l => l.GoalId).ToHashSet();
        var requested = req.GoalIds.ToHashSet();

        foreach (var gid in requested.Except(existing))
            doc.GoalLinks.Add(new DocumentGoalLink { GoalId = gid, DocumentId = docId, BloomLevel = 1 });

        var toRemove = doc.GoalLinks.Where(l => !requested.Contains(l.GoalId)).ToList();
        db.DocumentGoalLinks.RemoveRange(toRemove);

        await db.SaveChangesAsync();
        return ToResponse(doc);
    }

    [HttpDelete("{docId:guid}")]
    public async Task<IActionResult> Delete(Guid userId, Guid docId)
    {
        var doc = await db.Documents.FirstOrDefaultAsync(d => d.Id == docId && d.UserId == userId);
        if (doc is null) return NotFound();
        db.Documents.Remove(doc);
        await db.SaveChangesAsync();
        return NoContent();
    }

    [HttpGet("{docId:guid}/file")]
    public async Task<IActionResult> DownloadFile(Guid userId, Guid docId)
    {
        var doc = await db.Documents
            .Where(d => d.Id == docId && d.UserId == userId)
            .Select(d => new { d.FileData, d.ContentType, d.FileName })
            .FirstOrDefaultAsync();
        if (doc is null) return NotFound();
        return File(doc.FileData, doc.ContentType, doc.FileName);
    }

    [HttpPut("{docId:guid}/goals/{goalId}")]
    public async Task<ActionResult<DocumentGoalLinkDto>> UpdateGoalLink(
        Guid userId, Guid docId, string goalId, UpdateGoalLinkRequest req)
    {
        var link = await db.DocumentGoalLinks
            .FirstOrDefaultAsync(l => l.DocumentId == docId && l.GoalId == goalId);
        if (link is null) return NotFound();

        link.Einschaetzung = req.Einschaetzung;

        if (req.BloomLevel.HasValue)
        {
            link.BloomLevel = req.BloomLevel;

            var entry = await db.GoalEntries
                .FirstOrDefaultAsync(g => g.UserId == userId && g.GoalId == goalId);

            if (entry is null)
            {
                db.GoalEntries.Add(new GoalEntry
                {
                    UserId    = userId,
                    GoalId    = goalId,
                    Level     = req.BloomLevel.Value,
                    UpdatedAt = DateTime.UtcNow,
                });
            }
            else if (req.BloomLevel.Value > entry.Level)
            {
                entry.Level     = req.BloomLevel.Value;
                entry.UpdatedAt = DateTime.UtcNow;
            }
        }

        await db.SaveChangesAsync();
        return new DocumentGoalLinkDto(link.Id, link.GoalId, link.Einschaetzung, link.BloomLevel);
    }

    [HttpPost("{docId:guid}/ai-evaluate")]
    public async Task<ActionResult<AiEvaluateResponse>> AiEvaluate(
        Guid userId, Guid docId, [FromServices] AiEvaluationService aiService)
    {
        if (!aiService.IsConfigured)
            return BadRequest(new { error = "AI-Bewertung ist nicht konfiguriert. Endpoint und ApiKey in appsettings setzen." });

        var doc = await db.Documents
            .Include(d => d.GoalLinks)
            .FirstOrDefaultAsync(d => d.Id == docId && d.UserId == userId);
        if (doc is null) return NotFound();

        var user = await db.Users.FindAsync(userId);
        if (user is null) return NotFound();

        var result = await aiService.EvaluateAsync(doc, user.Specialty);
        if (result is null)
            return StatusCode(503, new { error = $"AI-Analyse fehlgeschlagen (Specialty: {user.Specialty}). Keine Leistungsziele geladen oder KI-Verbindungsfehler. Bitte Backend-Logs prüfen." });

        // Nur leere Textfelder befüllen – manuelle Einträge bleiben erhalten
        if (string.IsNullOrWhiteSpace(doc.Kurzbeschreibung))
            doc.Kurzbeschreibung = result.Kurzbeschreibung.Trim();
        if (string.IsNullOrWhiteSpace(doc.Umsetzung))
            doc.Umsetzung = result.Umsetzung.Trim();
        if (string.IsNullOrWhiteSpace(doc.Luecken))
            doc.Luecken = result.Luecken.Trim();

        // Technologien + Umgebungen: neue Tags ergänzen, bestehende behalten
        doc.Technologies = MergeTags(doc.Technologies, result.Technologien);
        doc.Environments = MergeTags(doc.Environments, result.Umgebungen);

        // Nur Leistungsziele ergänzen, die noch nicht verknüpft sind
        var existingGoalIds = doc.GoalLinks.Select(l => l.GoalId).ToHashSet();
        foreach (var b in result.Bewertungen.Take(10))
        {
            if (existingGoalIds.Contains(b.GoalId)) continue;
            doc.GoalLinks.Add(new DocumentGoalLink
            {
                GoalId        = b.GoalId,
                DocumentId    = docId,
                BloomLevel    = (byte)Math.Clamp(b.BloomLevel, 1, 6),
                Einschaetzung = b.Kommentar,
            });
        }

        await db.SaveChangesAsync();
        return new AiEvaluateResponse(
            ToResponse(doc),
            result.PromptTokens,
            result.CompletionTokens,
            result.TotalTokens);
    }

    private static DocumentResponse ToResponse(Document d) =>
        new(d.Id, d.UserId, d.ApCode, d.Title, d.Description,
            d.Kurzbeschreibung, d.Umsetzung, d.Luecken, d.Bewertungsart, d.FeedbackBerufsbildner,
            SplitTags(d.Technologies), SplitTags(d.Environments),
            d.FileName, d.ContentType, d.FileSize, d.UploadedAt, d.DocumentDate,
            d.GoalLinks.Select(l => new DocumentGoalLinkDto(l.Id, l.GoalId, l.Einschaetzung, l.BloomLevel)));

    private static IEnumerable<string> SplitTags(string? value) =>
        value?.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries) ?? [];

    private static string? MergeTags(string? existing, IEnumerable<string> incoming)
    {
        var current = SplitTags(existing).ToHashSet(StringComparer.OrdinalIgnoreCase);
        foreach (var tag in incoming) current.Add(tag.Trim());
        return current.Count == 0 ? null : string.Join(",", current);
    }

    private static DateTime? ParseDate(string? s) =>
        DateTime.TryParse(s, out var dt) ? DateTime.SpecifyKind(dt.Date, DateTimeKind.Utc) : null;
}
