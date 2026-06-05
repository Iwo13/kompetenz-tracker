namespace HK.Application.DTOs;

public record UserResponse(
    Guid Id,
    string Name,
    string Specialty,
    DateOnly StartDate,
    DateTime CreatedAt
);

public record CreateUserRequest(
    string Name,
    string Specialty,
    DateOnly StartDate
);
