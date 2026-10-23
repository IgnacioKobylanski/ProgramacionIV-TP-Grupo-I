using Microsoft.EntityFrameworkCore;
using Payment.Entities;

namespace Payment.DataAccess;

public class PaymentDbContext : DbContext
{
    public PaymentDbContext(DbContextOptions<PaymentDbContext> options) : base(options) { }

    public DbSet<PaymentRecord> Payments => Set<PaymentRecord>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.Entity<PaymentRecord>().HasIndex(p => p.ReservationId).IsUnique();
        b.Entity<PaymentRecord>().Property(p => p.Amount).HasPrecision(18, 2);
        b.Entity<PaymentRecord>().Property(p => p.Status).HasConversion<string>();
    }
}