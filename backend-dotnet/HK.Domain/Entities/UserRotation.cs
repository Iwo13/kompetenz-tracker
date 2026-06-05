namespace HK.Domain.Entities;

public class UserRotation
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid UserId { get; set; }
    public string ApCode { get; set; } = string.Empty;
    public DateOnly Von { get; set; }
    public DateOnly? Bis { get; set; }

    public User User { get; set; } = null!;
}
