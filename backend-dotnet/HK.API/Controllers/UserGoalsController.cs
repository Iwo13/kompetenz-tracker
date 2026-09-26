using HK.API.Services;
using HK.Application.DTOs;
using HK.Domain.Entities;
using HK.Infrastructure.Persistence;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace HK.API.Controllers;

[ApiController]
[Route("users/{userId:guid}/goals")]
public class UserGoalsController(AppDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IEnumerable<GoalEntryResponse>> GetAll(Guid userId)
    {
        var manualEntries = await db.GoalEntries
            .Where(g => g.UserId == userId)
            .ToListAsync();

        var docContributions = await db.DocumentGoalLinks
            .Include(l => l.Document)
            .Where(l => l.Document.UserId == userId && l.BloomLevel.HasValue)
            .Select(l => new {
                l.GoalId,
                BloomLevel = (int)l.BloomLevel!.Value,
                DocId = l.Document.Id,
                DocTitle = l.Document.Title
            })
            .ToListAsync();

        var allGoalIds = manualEntries.Select(e => e.GoalId)
            .Concat(docContributions.Select(c => c.GoalId))
            .Distinct()
            .OrderBy(id => id);

        return allGoalIds.Select(goalId =>
        {
            var manual = manualEntries.FirstOrDefault(e => e.GoalId == goalId);
            var manualLevel = manual?.Level ?? 0;

            var contributions = docContributions
                .Where(c => c.GoalId == goalId)
                .Select(c => new GoalContributionDto(c.DocId, c.DocTitle, c.BloomLevel))
                .ToList();

            var docMax = contributions.Count > 0 ? contributions.Max(c => c.BloomLevel) : 0;

            return new GoalEntryResponse(
                goalId,
                Math.Max(manualLevel, docMax),
                manualLevel,
                manual?.Comment,
                manual?.UpdatedAt,
                contributions
            );
        }).ToList();
    }

    [HttpPut("{goalId}")]
    public async Task<ActionResult<GoalEntryResponse>> Upsert(
        Guid userId, string goalId, UpsertGoalRequest req)
    {
        var entry = await db.GoalEntries
            .FirstOrDefaultAsync(g => g.UserId == userId && g.GoalId == goalId);

        if (entry is null)
        {
            entry = new GoalEntry { UserId = userId, GoalId = goalId };
            db.GoalEntries.Add(entry);
        }

        entry.Level     = (byte)Math.Clamp(req.Level, 0, 6);
        entry.Comment   = req.Comment;
        entry.UpdatedAt = DateTime.UtcNow;
        await db.SaveChangesAsync();

        var contributions = await db.DocumentGoalLinks
            .Include(l => l.Document)
            .Where(l => l.Document.UserId == userId && l.GoalId == goalId && l.BloomLevel.HasValue)
            .Select(l => new GoalContributionDto(l.Document.Id, l.Document.Title, (int)l.BloomLevel!.Value))
            .ToListAsync();

        var docMax = contributions.Count > 0 ? contributions.Max(c => c.BloomLevel) : 0;

        return new GoalEntryResponse(
            goalId,
            Math.Max(entry.Level, docMax),
            entry.Level,
            entry.Comment,
            entry.UpdatedAt,
            contributions
        );
    }

    [HttpPost("{goalId}/ai-suggest")]
    public async Task<ActionResult<GoalAiSuggestResponse>> AiSuggest(
        Guid userId, string goalId, GoalAiSuggestRequest req, [FromServices] AiEvaluationService aiService)
    {
        if (!aiService.IsConfigured)
            return BadRequest(new { detail = "AI-Bewertung ist nicht konfiguriert. Endpoint und ApiKey in appsettings setzen." });

        if (string.IsNullOrWhiteSpace(req.Comment))
            return BadRequest(new { detail = "Kein Kompetenznachweis-Text vorhanden." });

        var user = await db.Users.FindAsync(userId);
        if (user is null) return NotFound();

        var result = await aiService.SuggestGoalLevelAsync(user.Specialty, goalId, req.Comment);
        if (result is null)
            return StatusCode(503, new { detail = "AI-Analyse fehlgeschlagen. Bitte Leistungsziel und Konfiguration prüfen." });

        return new GoalAiSuggestResponse(
            result.BloomLevel, result.Begruendung, result.OptimierterText,
            result.PromptTokens, result.CompletionTokens, result.TotalTokens);
    }
}
