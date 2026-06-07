namespace HK.Application.DTOs;

public record DocumentGoalLinkDto(
    Guid Id,
    string GoalId,
    string? Einschaetzung,
    byte? BloomLevel
);

public record DocumentResponse(
    Guid Id,
    Guid UserId,
    string ApCode,
    string Title,
    string? Description,
    string FileName,
    string ContentType,
    long FileSize,
    DateTime UploadedAt,
    IEnumerable<DocumentGoalLinkDto> GoalLinks
);

public record UpdateDocumentRequest(
    string Title,
    string? Description,
    string ApCode,
    IEnumerable<string> GoalIds
);

public record UpdateGoalLinkRequest(
    string? Einschaetzung,
    byte? BloomLevel
);
