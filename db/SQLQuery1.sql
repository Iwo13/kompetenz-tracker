USE KompetenzTracker;
GO

-- Lernende
CREATE TABLE Users (
    Id          UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Name        NVARCHAR(100)   NOT NULL,
    Specialty   NVARCHAR(20)    NOT NULL CHECK (Specialty IN ('platform', 'app')),
    StartDate   DATE            NOT NULL,
    CreatedAt   DATETIME2       DEFAULT GETDATE()
);

-- Bewertungen pro Leistungsziel
CREATE TABLE GoalEntries (
    Id          UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserId      UNIQUEIDENTIFIER NOT NULL REFERENCES Users(Id) ON DELETE CASCADE,
    GoalId      NVARCHAR(20)    NOT NULL,   -- z.B. 'a1.1', 'g2.3'
    Level       TINYINT         NOT NULL DEFAULT 0 CHECK (Level BETWEEN 0 AND 6),
    Comment     NVARCHAR(MAX),
    UpdatedAt   DATETIME2       DEFAULT GETDATE(),
    CONSTRAINT UQ_User_Goal UNIQUE (UserId, GoalId)
);
GO

-- Testdaten: ein Lernender
INSERT INTO Users (Name, Specialty, StartDate)
VALUES ('Max Muster', 'app', '2023-08-01');
GO

SELECT * FROM Users;
SELECT * FROM GoalEntries;
GO
