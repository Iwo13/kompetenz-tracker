-- ============================================================
-- Handlungskompetenz-Tracker
-- Datenbankschema für SQL Server Express
-- ============================================================

USE KompetenzTracker;
GO

-- ── Lernende ─────────────────────────────────────────────────
-- Speichert alle erfassten Personen (Lernende)
CREATE TABLE Users (
    Id          UNIQUEIDENTIFIER    PRIMARY KEY DEFAULT NEWID(),
    Name        NVARCHAR(100)       NOT NULL,
    Specialty   NVARCHAR(20)        NOT NULL CHECK (Specialty IN ('platform', 'app')),
    StartDate   DATE                NOT NULL,
    CreatedAt   DATETIME2           NOT NULL DEFAULT GETDATE()
);
GO

-- ── Kompetenzbewertungen ──────────────────────────────────────
-- Eine Zeile pro Person + Leistungsziel (z.B. 'a1.1', 'g2.3')
-- Level 0 = nicht bewertet, 1-6 = Bloom-Stufe K1-K6
CREATE TABLE GoalEntries (
    Id          UNIQUEIDENTIFIER    PRIMARY KEY DEFAULT NEWID(),
    UserId      UNIQUEIDENTIFIER    NOT NULL
                    REFERENCES Users(Id) ON DELETE CASCADE,
    GoalId      NVARCHAR(20)        NOT NULL,
    Level       TINYINT             NOT NULL DEFAULT 0
                    CHECK (Level BETWEEN 0 AND 6),
    Comment     NVARCHAR(MAX)       NULL,
    UpdatedAt   DATETIME2           NOT NULL DEFAULT GETDATE(),

    -- Jede Person kann jedes Ziel nur einmal bewerten
    CONSTRAINT UQ_User_Goal UNIQUE (UserId, GoalId)
);
GO

-- ── Indizes für schnelle Abfragen ─────────────────────────────
CREATE INDEX IX_GoalEntries_UserId ON GoalEntries(UserId);
GO

-- ============================================================
-- Testdaten (optional, für Entwicklung)
-- ============================================================

INSERT INTO Users (Name, Specialty, StartDate)
VALUES
    ('Max Muster',  'app',      '2023-08-01'),
    ('Sara Beispiel','platform', '2024-08-01');
GO
