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
}