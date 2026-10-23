using Availability.Domain.Entities;

namespace Availability.Application.Abstractions;

public interface IAvailabilityRepository
{
    Task<IReadOnlyList<Event>> ListEventsAsync(CancellationToken ct);
    Task<Event?> GetEventAsync(Guid eventId, CancellationToken ct);
    Task<IReadOnlyList<Seat>> GetSeatsAsync(Guid eventId, CancellationToken ct);
}