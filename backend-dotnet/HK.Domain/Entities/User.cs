namespace HK.Domain.Entities;

public class User
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Name { get; set; } = string.Empty;
    public string Specialty { get; set; } = string.Empty;
    public DateOnly StartDate { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public ICollection<GoalEntry> GoalEntries { get; set; } = [];
    public ICollection<UserRotation> Rotations { get; set; } = [];
}
