using Microsoft.EntityFrameworkCore;
using Payment.Entities;

namespace Payment.DataAccess;

public interface IPaymentRepository
{
    Task<PaymentRecord> GetOrAddAsync(PaymentRecord record, CancellationToken ct);
}

public class PaymentRepository : IPaymentRepository
{
    private readonly PaymentDbContext _db;

    public PaymentRepository(PaymentDbContext db) => _db = db;

    public async Task<PaymentRecord> GetOrAddAsync(PaymentRecord record, CancellationToken ct)
    {
        var existing = await FindAsync(record.ReservationId, ct);
        if (existing is not null) return existing;

        _db.Payments.Add(record);
        try
        {
            await _db.SaveChangesAsync(ct);
            return record;
        }
        catch (DbUpdateException)
        {
            _db.Entry(record).State = EntityState.Detached;
            var winner = await FindAsync(record.ReservationId, ct);
            if (winner is null) throw;
            return winner;
        }
    }

    private Task<PaymentRecord?> FindAsync(Guid reservationId, CancellationToken ct) =>
        _db.Payments.AsNoTracking().FirstOrDefaultAsync(p => p.ReservationId == reservationId, ct);
}