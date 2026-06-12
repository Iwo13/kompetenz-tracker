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
        => await db.Documents
            .Where(d => d.UserId == userId)
            .Include(d => d.GoalLinks)
            .OrderByDescending(d => d.UploadedAt)
            .Select(d => ToResponse(d))
            .ToListAsync();

    [HttpPost]
    [RequestSizeLimit(50 * 1024 * 1024)]
    public async Task<ActionResult<DocumentResponse>> Create(
        Guid userId,
        [FromForm] string title,
        [FromForm] string apCode,
        [FromForm] string? description,
        [FromForm] string? goalIds,
        [FromForm] string? bewertungsart,
        IFormFile file)
    {
        if (file is null || file.Length == 0)
            return BadRequest("Keine Datei hochgeladen.");

        using var ms = new MemoryStream();
        await file.CopyToAsync(ms);

        var doc = new Document
        {
            UserId       = userId,
            ApCode       = apCode,
            Title        = title.Trim(),
            Description  = description?.Trim(),
            Bewertungsart = bewertungsart?.Trim() ?? "manuell",
            FileName     = file.FileName,
            ContentType  = file.ContentType,
            FileData     = ms.ToArray(),
            FileSize     = file.Length,
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
    public async Task<ActionResult<DocumentResponse>> AiEvaluate(
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
            return StatusCode(503, new { error = "AI-Analyse fehlgeschlagen. Bitte Logs prüfen." });

        doc.Kurzbeschreibung = result.Kurzbeschreibung.Trim();
        doc.Umsetzung        = result.Umsetzung.Trim();
        doc.Luecken          = result.Luecken.Trim();

        db.DocumentGoalLinks.RemoveRange(doc.GoalLinks);
        doc.GoalLinks.Clear();

        foreach (var b in result.Bewertungen.Take(10))
        {
            doc.GoalLinks.Add(new DocumentGoalLink
            {
                GoalId        = b.GoalId,
                DocumentId    = docId,
                BloomLevel    = (byte)Math.Clamp(b.BloomLevel, 1, 6),
                Einschaetzung = b.Kommentar,
            });
        }

        await db.SaveChangesAsync();
        return ToResponse(doc);
    }

    private static DocumentResponse ToResponse(Document d) =>
        new(d.Id, d.UserId, d.ApCode, d.Title, d.Description,
            d.Kurzbeschreibung, d.Umsetzung, d.Luecken, d.Bewertungsart, d.FeedbackBerufsbildner,
            d.FileName, d.ContentType, d.FileSize, d.UploadedAt,
            d.GoalLinks.Select(l => new DocumentGoalLinkDto(l.Id, l.GoalId, l.Einschaetzung, l.BloomLevel)));
}
