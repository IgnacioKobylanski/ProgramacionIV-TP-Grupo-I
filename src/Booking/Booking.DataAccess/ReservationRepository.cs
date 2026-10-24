using Booking.Entities;
using Microsoft.EntityFrameworkCore;
using Npgsql;

namespace Booking.DataAccess;

public enum CreateResult
{
    Created,
    SeatTaken,
    DuplicateRequest
}

public interface IReservationRepository
{
    Task<Reservation?> GetByRequestIdAsync(Guid requestId, CancellationToken ct);
    Task<CreateResult> TryAddAsync(Reservation reservation, CancellationToken ct);
    Task<bool> TryTransitionAsync(Guid reservationId, ReservationStatus from, ReservationStatus to,
        RejectionReason? reason, CancellationToken ct);
    Task<int> ExpireOverdueAsync(DateTime nowUtc, CancellationToken ct);
}

// Capa de acceso a datos (N-Layer): Business no conoce EF Core ni Npgsql.
public class ReservationRepository : IReservationRepository
{
    private readonly BookingDbContext _db;

    public ReservationRepository(BookingDbContext db) => _db = db;

    public Task<Reservation?> GetByRequestIdAsync(Guid requestId, CancellationToken ct) =>
        _db.Reservations.AsNoTracking().FirstOrDefaultAsync(r => r.RequestId == requestId, ct);

    // Control de concurrencia OPTIMISTA: no bloqueamos nada. Intentamos insertar y dejamos
    // que la restricción única decida quién gana. Es más simple y escala mejor con réplicas
    // que un lock distribuido (por eso no hace falta ZooKeeper).
    public async Task<CreateResult> TryAddAsync(Reservation reservation, CancellationToken ct)
    {
        _db.Reservations.Add(reservation);
        try
        {
            await _db.SaveChangesAsync(ct);
            return CreateResult.Created;
        }
        catch (DbUpdateException ex) when (ex.InnerException is PostgresException
        { SqlState: PostgresErrorCodes.UniqueViolation } pg)
        {
            _db.Entry(reservation).State = EntityState.Detached;
            return pg.ConstraintName == BookingDbContext.RequestIndex
                ? CreateResult.DuplicateRequest
                : CreateResult.SeatTaken;
        }
    }

    // Compare-and-set: solo cambia el estado si sigue siendo el esperado. Evita pisar,
    // por ejemplo, una reserva que venció mientras se esperaba la respuesta de Payment.
    public async Task<bool> TryTransitionAsync(Guid reservationId, ReservationStatus from, ReservationStatus to,
        RejectionReason? reason, CancellationToken ct)
    {
        var rows = await _db.Reservations
            .Where(r => r.Id == reservationId && r.Status == from)
            .ExecuteUpdateAsync(s => s
                .SetProperty(r => r.Status, to)
                .SetProperty(r => r.Reason, reason), ct);
        return rows == 1;
    }

    // Es una sola sentencia UPDATE: si hay varias réplicas ejecutándola, no se pisan.
    public Task<int> ExpireOverdueAsync(DateTime nowUtc, CancellationToken ct) =>
        _db.Reservations
            .Where(r => r.Status == ReservationStatus.Retenida && r.ExpiresAtUtc < nowUtc)
            .ExecuteUpdateAsync(s => s.SetProperty(r => r.Status, ReservationStatus.Vencida), ct);
}