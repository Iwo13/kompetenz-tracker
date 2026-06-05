namespace HK.Domain.Entities;

public class GoalEntry
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid UserId { get; set; }
    public string GoalId { get; set; } = string.Empty;
    public byte Level { get; set; }
    public string? Comment { get; set; }
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    public User User { get; set; } = null!;
}
