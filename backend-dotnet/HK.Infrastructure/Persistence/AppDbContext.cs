using HK.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace HK.Infrastructure.Persistence;

public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<User> Users => Set<User>();
    public DbSet<GoalEntry> GoalEntries => Set<GoalEntry>();
    public DbSet<UserRotation> UserRotations => Set<UserRotation>();
    public DbSet<Document> Documents => Set<Document>();
    public DbSet<DocumentGoalLink> DocumentGoalLinks => Set<DocumentGoalLink>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>(b =>
        {
            b.ToTable("Users");
            b.HasKey(u => u.Id);
            b.Property(u => u.Id).ValueGeneratedNever();
            b.Property(u => u.Name).HasMaxLength(100).IsRequired();
            b.Property(u => u.Email).HasMaxLength(200);
            b.Property(u => u.Specialty).HasMaxLength(25).IsRequired();
            b.Property(u => u.CreatedAt).HasDefaultValueSql("GETUTCDATE()");
            b.HasIndex(u => u.Email).IsUnique().HasDatabaseName("UQ_Users_Email")
             .HasFilter("[Email] IS NOT NULL");
        });

        modelBuilder.Entity<GoalEntry>(b =>
        {
            b.ToTable("GoalEntries");
            b.HasKey(g => g.Id);
            b.Property(g => g.Id).ValueGeneratedNever();
            b.Property(g => g.GoalId).HasMaxLength(20).IsRequired();
            b.Property(g => g.Comment).HasColumnType("nvarchar(max)");
            b.HasIndex(g => new { g.UserId, g.GoalId }).IsUnique().HasDatabaseName("UQ_User_Goal");
            b.HasOne(g => g.User)
             .WithMany(u => u.GoalEntries)
             .HasForeignKey(g => g.UserId)
             .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<UserRotation>(b =>
        {
            b.ToTable("UserRotations");
            b.HasKey(r => r.Id);
            b.Property(r => r.Id).ValueGeneratedNever();
            b.Property(r => r.ApCode).HasMaxLength(10).IsRequired();
            b.HasOne(r => r.User)
             .WithMany(u => u.Rotations)
             .HasForeignKey(r => r.UserId)
             .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<Document>(b =>
        {
            b.ToTable("Documents");
            b.HasKey(d => d.Id);
            b.Property(d => d.Id).ValueGeneratedNever();
            b.Property(d => d.ApCode).HasMaxLength(20).IsRequired();
            b.Property(d => d.Title).HasMaxLength(200).IsRequired();
            b.Property(d => d.Description).HasColumnType("nvarchar(max)");
            b.Property(d => d.FileName).HasMaxLength(260).IsRequired();
            b.Property(d => d.ContentType).HasMaxLength(100).IsRequired();
            b.Property(d => d.FileData).HasColumnType("varbinary(max)").IsRequired();
            b.Property(d => d.UploadedAt).HasDefaultValueSql("GETUTCDATE()");
            b.HasOne(d => d.User)
             .WithMany(u => u.Documents)
             .HasForeignKey(d => d.UserId)
             .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<DocumentGoalLink>(b =>
        {
            b.ToTable("DocumentGoalLinks");
            b.HasKey(l => l.Id);
            b.Property(l => l.Id).ValueGeneratedNever();
            b.Property(l => l.GoalId).HasMaxLength(20).IsRequired();
            b.Property(l => l.Einschaetzung).HasColumnType("nvarchar(max)");
            b.HasIndex(l => new { l.DocumentId, l.GoalId }).IsUnique().HasDatabaseName("UQ_Doc_Goal");
            b.HasOne(l => l.Document)
             .WithMany(d => d.GoalLinks)
             .HasForeignKey(l => l.DocumentId)
             .OnDelete(DeleteBehavior.Cascade);
        });
    }
}
