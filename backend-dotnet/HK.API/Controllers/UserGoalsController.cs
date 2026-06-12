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
}
