namespace HK.Application.DTOs;

public record GoalEntryResponse(
    string GoalId,
    int EffectiveLevel,
    int ManualLevel,
    string? Comment,
    DateTime? UpdatedAt,
    IEnumerable<GoalContributionDto> DocumentContributions
);

public record GoalContributionDto(
    Guid DocId,
    string DocTitle,
    int BloomLevel
);

public record UpsertGoalRequest(
    string GoalId,
    int Level,
    string? Comment
);
