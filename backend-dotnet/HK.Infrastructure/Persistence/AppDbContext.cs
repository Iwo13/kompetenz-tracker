using HK.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace HK.Infrastructure.Persistence;

public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<User> Users => Set<User>();
    public DbSet<GoalEntry> GoalEntries => Set<GoalEntry>();
    public DbSet<UserRotation> UserRotations => Set<UserRotation>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>(b =>
        {
            b.ToTable("Users");
            b.HasKey(u => u.Id);
            b.Property(u => u.Id).ValueGeneratedNever();
            b.Property(u => u.Name).HasMaxLength(100).IsRequired();
            b.Property(u => u.Specialty).HasMaxLength(20).IsRequired();
            b.Property(u => u.CreatedAt).HasDefaultValueSql("GETUTCDATE()");
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
    }
}
