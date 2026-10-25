using Microsoft.EntityFrameworkCore;
using Notifications.Models;

namespace Notifications.Data;

public class NotificationsDbContext : DbContext
{
    public NotificationsDbContext(DbContextOptions<NotificationsDbContext> options) : base(options) { }

    public DbSet<Notification> Notifications => Set<Notification>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        // Una notificación por reserva: red de seguridad contra duplicados si Booking reintenta.
        b.Entity<Notification>().HasIndex(n => n.ReservationId).IsUnique();
        b.Entity<Notification>().Property(n => n.Message).HasMaxLength(500);
    }
}