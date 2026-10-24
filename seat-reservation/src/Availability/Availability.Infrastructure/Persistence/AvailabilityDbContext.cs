using Availability.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace Availability.Infrastructure.Persistence;

public class AvailabilityDbContext : DbContext
{
    public AvailabilityDbContext(DbContextOptions<AvailabilityDbContext> options) : base(options) { }

    public DbSet<Event> Events => Set<Event>();
    public DbSet<Seat> Seats => Set<Seat>();
    public DbSet<ReservationRequest> ReservationRequests => Set<ReservationRequest>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.Entity<Event>().Property(e => e.Name).HasMaxLength(200);
        b.Entity<Seat>().HasIndex(s => new { s.EventId, s.Label }).IsUnique();
        b.Entity<Seat>().HasOne<Event>().WithMany(e => e.Seats).HasForeignKey(s => s.EventId);
    }
}