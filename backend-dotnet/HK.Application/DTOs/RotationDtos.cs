namespace HK.Application.DTOs;

public record RotationResponse(
    Guid Id,
    Guid UserId,
    string ApCode,
    DateOnly Von,
    DateOnly? Bis
);

public record CreateRotationRequest(
    string ApCode,
    DateOnly Von,
    DateOnly? Bis
);
