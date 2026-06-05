namespace HK.Application.DTOs;

public record GoalEntryResponse(
    Guid Id,
    Guid UserId,
    string GoalId,
    int Level,
    string? Comment,
    DateTime UpdatedAt
);

public record UpsertGoalRequest(
    string GoalId,
    int Level,
    string? Comment
);
