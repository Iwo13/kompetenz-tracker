using HK.Application.DTOs;
using HK.Domain.Entities;
using HK.Infrastructure.Persistence;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace HK.API.Controllers;

[ApiController]
[Route("[controller]")]
public class UsersController(AppDbContext db) : ControllerBase
{
    [HttpGet]
    public async Task<IEnumerable<UserResponse>> GetAll()
        => await db.Users
            .OrderBy(u => u.Name)
            .Select(u => ToResponse(u))
            .ToListAsync();

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<UserResponse>> GetById(Guid id)
    {
        var user = await db.Users.FindAsync(id);
        return user is null ? NotFound() : ToResponse(user);
    }

    [HttpPost]
    public async Task<ActionResult<UserResponse>> Create(CreateUserRequest req)
    {
        var email = string.IsNullOrWhiteSpace(req.Email) ? null : req.Email.Trim();
        if (email is not null && await db.Users.AnyAsync(u => u.Email == email))
            return Conflict(new { detail = "E-Mail-Adresse wird bereits verwendet." });

        var user = new User
        {
            Name      = req.Name.Trim(),
            Email     = email,
            Specialty = req.Specialty,
            StartDate = req.StartDate,
        };
        db.Users.Add(user);
        await db.SaveChangesAsync();
        return CreatedAtAction(nameof(GetById), new { id = user.Id }, ToResponse(user));
    }

    [HttpPut("{id:guid}")]
    public async Task<ActionResult<UserResponse>> Update(Guid id, CreateUserRequest req)
    {
        var user = await db.Users.FindAsync(id);
        if (user is null) return NotFound();

        var email = string.IsNullOrWhiteSpace(req.Email) ? null : req.Email.Trim();
        if (email is not null && await db.Users.AnyAsync(u => u.Email == email && u.Id != id))
            return Conflict(new { detail = "E-Mail-Adresse wird bereits verwendet." });

        user.Name      = req.Name.Trim();
        user.Email     = email;
        user.Specialty = req.Specialty;
        user.StartDate = req.StartDate;
        await db.SaveChangesAsync();
        return ToResponse(user);
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> Delete(Guid id)
    {
        var user = await db.Users.FindAsync(id);
        if (user is null) return NotFound();
        db.Users.Remove(user);
        await db.SaveChangesAsync();
        return NoContent();
    }

    private static UserResponse ToResponse(User u) =>
        new(u.Id, u.Name, u.Email, u.Specialty, u.StartDate, u.CreatedAt);
}
