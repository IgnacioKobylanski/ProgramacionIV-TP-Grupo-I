namespace Availability.Application.Abstractions;

public record BookingStatus(string Status, string? Reason);

// Reserva de un usuario tal como la devuelve Booking (GET /reservations?userId=...).
public record BookingReservation(Guid RequestId, Guid EventId, Guid SeatId,
    string Status, string? Reason, DateTime CreatedAtUtc);

// Puerto hacia Booking (flecha GET del diagrama oficial).
public interface IBookingClient
{
    // Devuelve null si Booking todavía no procesó la solicitud.
    Task<BookingStatus?> GetStatusAsync(Guid requestId, CancellationToken ct);

    Task<IReadOnlyList<Guid>> GetOccupiedSeatIdsAsync(Guid eventId, CancellationToken ct);

    // Lista las reservas de un usuario en cualquier estado. Si no tiene, devuelve una lista vacía.
    Task<IReadOnlyList<BookingReservation>> GetReservationsByUserAsync(string userId, CancellationToken ct);
}