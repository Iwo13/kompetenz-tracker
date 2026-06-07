namespace HK.Domain.Entities;

public class DocumentGoalLink
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid DocumentId { get; set; }
    public string GoalId { get; set; } = string.Empty;
    public string? Einschaetzung { get; set; }
    public byte? BloomLevel { get; set; }

    public Document Document { get; set; } = null!;
}
