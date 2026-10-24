using Booking.Entities;
using Microsoft.EntityFrameworkCore;

namespace Booking.DataAccess;

public class BookingDbContext : DbContext
{
    public const string RequestIndex = "ux_reservations_request_id";
    public const string ActiveSeatIndex = "ux_reservations_active_seat";

    public BookingDbContext(DbContextOptions<BookingDbContext> options) : base(options) { }

    public DbSet<Reservation> Reservations => Set<Reservation>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        var r = b.Entity<Reservation>();

        r.Property(x => x.Status).HasConversion<string>().HasMaxLength(20);
        r.Property(x => x.Reason).HasConversion<string>().HasMaxLength(30);

        r.HasIndex(x => x.RequestId).IsUnique().HasDatabaseName(RequestIndex);

        r.HasIndex(x => new { x.EventId, x.SeatId })
            .IsUnique()
            .HasFilter("\"Status\" IN ('Retenida', 'Confirmada')")
            .HasDatabaseName(ActiveSeatIndex);

        r.HasIndex(x => new { x.Status, x.ExpiresAtUtc });
    }
}