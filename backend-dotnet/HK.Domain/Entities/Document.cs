namespace HK.Domain.Entities;

public class Document
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid UserId { get; set; }
    public string ApCode { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? Kurzbeschreibung { get; set; }
    public string? Umsetzung { get; set; }
    public string? Luecken { get; set; }
    public string Bewertungsart { get; set; } = "manuell";
    public string? FeedbackBerufsbildner { get; set; }
    public string FileName { get; set; } = string.Empty;
    public string ContentType { get; set; } = string.Empty;
    public byte[] FileData { get; set; } = [];
    public long FileSize { get; set; }
    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;
    public DateTime? DocumentDate { get; set; }

    public User User { get; set; } = null!;
    public ICollection<DocumentGoalLink> GoalLinks { get; set; } = [];
}
