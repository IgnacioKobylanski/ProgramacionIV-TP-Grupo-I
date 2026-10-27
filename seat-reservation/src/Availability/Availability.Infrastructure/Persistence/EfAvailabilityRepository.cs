using Availability.Application.Abstractions;
using Availability.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace Availability.Infrastructure.Persistence;

public class EfAvailabilityRepository : IAvailabilityRepository
{
    private readonly AvailabilityDbContext _db;

    public EfAvailabilityRepository(AvailabilityDbContext db) => _db = db;

    public async Task<IReadOnlyList<Event>> ListEventsAsync(CancellationToken ct) =>
        await _db.Events.AsNoTracking().OrderBy(e => e.DateUtc).ToListAsync(ct);

    public Task<Event?> GetEventAsync(Guid eventId, CancellationToken ct) =>
        _db.Events.AsNoTracking().FirstOrDefaultAsync(e => e.Id == eventId, ct);

    public async Task<IReadOnlyList<Seat>> GetSeatsAsync(Guid eventId, CancellationToken ct) =>
        await _db.Seats.AsNoTracking().Where(s => s.EventId == eventId).OrderBy(s => s.Label).ToListAsync(ct);
    
    public Task<Seat?> GetSeatAsync(Guid eventId, Guid seatId, CancellationToken ct) =>
    _db.Seats.AsNoTracking().FirstOrDefaultAsync(s => s.EventId == eventId && s.Id == seatId, ct);

    public async Task AddRequestAsync(ReservationRequest request, CancellationToken ct)
    {
        _db.ReservationRequests.Add(request);
        await _db.SaveChangesAsync(ct);
    }

    public Task<ReservationRequest?> GetRequestAsync(Guid requestId, CancellationToken ct) =>
        _db.ReservationRequests.AsNoTracking().FirstOrDefaultAsync(r => r.Id == requestId, ct);

    public async Task AddEventAsync(Event ev, CancellationToken ct)
    {
        _db.Events.Add(ev); // agrega también sus asientos
        await _db.SaveChangesAsync(ct);
    }
}