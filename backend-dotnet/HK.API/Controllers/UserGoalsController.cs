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
        => await db.GoalEntries
            .Where(g => g.UserId == userId)
            .Select(g => ToResponse(g))
            .ToListAsync();

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
        return ToResponse(entry);
    }

    private static GoalEntryResponse ToResponse(GoalEntry g) =>
        new(g.Id, g.UserId, g.GoalId, g.Level, g.Comment, g.UpdatedAt);
}
