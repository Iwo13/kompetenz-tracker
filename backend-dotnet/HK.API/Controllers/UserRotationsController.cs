using HK.Application.DTOs;
using HK.Domain.Entities;
using HK.Infrastructure.Persistence;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace HK.API.Controllers;

[ApiController]
[Route("users/{userId:guid}/rotations")]
public class UserRotationsController(AppDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IEnumerable<RotationResponse>> GetAll(Guid userId)
        => await db.UserRotations
            .Where(r => r.UserId == userId)
            .OrderBy(r => r.Von)
            .Select(r => ToResponse(r))
            .ToListAsync();

    [HttpPost]
    public async Task<ActionResult<RotationResponse>> Create(Guid userId, CreateRotationRequest req)
    {
        var rot = new UserRotation
        {
            UserId  = userId,
            ApCode  = req.ApCode,
            Von     = req.Von,
            Bis     = req.Bis,
        };
        db.UserRotations.Add(rot);
        await db.SaveChangesAsync();
        return CreatedAtAction(nameof(GetAll), new { userId }, ToResponse(rot));
    }

    [HttpPut("{rotId:guid}")]
    public async Task<ActionResult<RotationResponse>> Update(
        Guid userId, Guid rotId, CreateRotationRequest req)
    {
        var rot = await db.UserRotations
            .FirstOrDefaultAsync(r => r.Id == rotId && r.UserId == userId);
        if (rot is null) return NotFound();
        rot.ApCode = req.ApCode;
        rot.Von    = req.Von;
        rot.Bis    = req.Bis;
        await db.SaveChangesAsync();
        return ToResponse(rot);
    }

    [HttpDelete("{rotId:guid}")]
    public async Task<IActionResult> Delete(Guid userId, Guid rotId)
    {
        var rot = await db.UserRotations
            .FirstOrDefaultAsync(r => r.Id == rotId && r.UserId == userId);
        if (rot is null) return NotFound();
        db.UserRotations.Remove(rot);
        await db.SaveChangesAsync();
        return NoContent();
    }

    private static RotationResponse ToResponse(UserRotation r) =>
        new(r.Id, r.UserId, r.ApCode, r.Von, r.Bis);
}
