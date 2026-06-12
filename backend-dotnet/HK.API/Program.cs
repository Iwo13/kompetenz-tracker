using System.Text.Json;
using HK.API.Services;
using HK.Infrastructure.Persistence;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.Identity.Web;

var builder = WebApplication.CreateBuilder(args);

// ── EF Core / SQL Server ──────────────────────────────────────────────────────
builder.Services.AddDbContext<AppDbContext>(opts =>
    opts.UseSqlServer(builder.Configuration.GetConnectionString("Default")));

// ── Controllers + JSON-Serialisierung ────────────────────────────────────────
// snake_case-Ausgabe entspricht dem Python-Backend-Vertrag
builder.Services.AddControllers()
    .AddJsonOptions(opts =>
    {
        opts.JsonSerializerOptions.PropertyNamingPolicy        = JsonNamingPolicy.SnakeCaseLower;
        opts.JsonSerializerOptions.DictionaryKeyPolicy         = JsonNamingPolicy.SnakeCaseLower;
        opts.JsonSerializerOptions.PropertyNameCaseInsensitive = true;
        opts.JsonSerializerOptions.DefaultIgnoreCondition      =
            System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull;
    });

// ── Swagger ───────────────────────────────────────────────────────────────────
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
    c.SwaggerDoc("v1", new() { Title = "HK-Tracker API", Version = "v1" }));

// ── Entra ID / Zertifikat-Auth ────────────────────────────────────────────────
// Nur aktiv wenn TenantId + ClientId in appsettings gesetzt sind
var azureAdSection = builder.Configuration.GetSection("AzureAd");
if (!string.IsNullOrEmpty(azureAdSection["TenantId"]) &&
    !string.IsNullOrEmpty(azureAdSection["ClientId"]))
{
    builder.Services
        .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
        .AddMicrosoftIdentityWebApi(azureAdSection);
    builder.Services.AddAuthorization();
}

// ── AI Evaluation Service ─────────────────────────────────────────────────────
builder.Services.AddHttpClient<AiEvaluationService>();

// ── CORS: Frontend-Dev erlauben ───────────────────────────────────────────────
builder.Services.AddCors(opts => opts.AddDefaultPolicy(p =>
    p.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()));

var app = builder.Build();

// ── DB-Schema sicherstellen ────────────────────────────────────────────────────
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();

    // Neue Tabellen nachrüsten falls DB bereits existiert (EnsureCreated ignoriert das)
    db.Database.ExecuteSqlRaw("""
        IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Documents')
        BEGIN
            CREATE TABLE Documents (
                Id          UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
                UserId      UNIQUEIDENTIFIER NOT NULL,
                ApCode      NVARCHAR(20)     NOT NULL,
                Title       NVARCHAR(200)    NOT NULL,
                Description NVARCHAR(MAX)    NULL,
                FileName    NVARCHAR(260)    NOT NULL,
                ContentType NVARCHAR(100)    NOT NULL,
                FileData    VARBINARY(MAX)   NOT NULL,
                FileSize    BIGINT           NOT NULL DEFAULT 0,
                UploadedAt  DATETIME2        NOT NULL DEFAULT GETUTCDATE(),
                CONSTRAINT FK_Documents_Users FOREIGN KEY (UserId) REFERENCES Users(Id) ON DELETE CASCADE
            );
        END

        IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('Documents') AND name = 'Kurzbeschreibung')
        BEGIN
            ALTER TABLE Documents ADD
                Kurzbeschreibung NVARCHAR(MAX) NULL,
                Umsetzung        NVARCHAR(MAX) NULL,
                Luecken          NVARCHAR(MAX) NULL,
                Bewertungsart    NVARCHAR(20)  NOT NULL DEFAULT 'manuell';
        END

        IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('Documents') AND name = 'FeedbackBerufsbildner')
        BEGIN
            ALTER TABLE Documents ADD FeedbackBerufsbildner NVARCHAR(MAX) NULL;
        END

        IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('Documents') AND name = 'DocumentDate')
        BEGIN
            ALTER TABLE Documents ADD DocumentDate DATETIME2 NULL;
        END

        IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'DocumentGoalLinks')
        BEGIN
            CREATE TABLE DocumentGoalLinks (
                Id            UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
                DocumentId    UNIQUEIDENTIFIER NOT NULL,
                GoalId        NVARCHAR(20)     NOT NULL,
                Einschaetzung NVARCHAR(MAX)    NULL,
                BloomLevel    TINYINT          NULL,
                CONSTRAINT FK_DocGoalLinks_Documents FOREIGN KEY (DocumentId) REFERENCES Documents(Id) ON DELETE CASCADE,
                CONSTRAINT UQ_Doc_Goal UNIQUE (DocumentId, GoalId)
            );
        END
        """);
}

app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.UseSwagger();
app.UseSwaggerUI();
app.MapControllers();
app.Run();
