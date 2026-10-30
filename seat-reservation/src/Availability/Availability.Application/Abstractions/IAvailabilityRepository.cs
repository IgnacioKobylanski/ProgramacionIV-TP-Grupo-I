using Availability.Domain.Entities;

namespace Availability.Application.Abstractions;

public interface IAvailabilityRepository
{
    Task<IReadOnlyList<Event>> ListEventsAsync(CancellationToken ct);
    Task<Event?> GetEventAsync(Guid eventId, CancellationToken ct);
    Task<IReadOnlyList<Seat>> GetSeatsAsync(Guid eventId, CancellationToken ct);
    Task<Seat?> GetSeatAsync(Guid eventId, Guid seatId, CancellationToken ct);
    Task AddRequestAsync(ReservationRequest request, CancellationToken ct);
    Task<ReservationRequest?> GetRequestAsync(Guid requestId, CancellationToken ct);
}