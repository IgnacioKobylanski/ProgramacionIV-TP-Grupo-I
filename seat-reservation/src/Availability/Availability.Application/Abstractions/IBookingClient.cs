namespace Availability.Application.Abstractions;

public record BookingStatus(string Status, string? Reason);

// Puerto hacia Booking (flecha GET del diagrama oficial).
public interface IBookingClient
{
    // Devuelve null si Booking todavía no procesó la solicitud.
    Task<BookingStatus?> GetStatusAsync(Guid requestId, CancellationToken ct);

    Task<IReadOnlyList<Guid>> GetOccupiedSeatIdsAsync(Guid eventId, CancellationToken ct);
}