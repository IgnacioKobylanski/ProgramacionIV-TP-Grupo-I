namespace Availability.Api;

// Cuando agreguemos autenticación, UserId saldrá del token y no del cuerpo.
public record ReservationRequestBody(Guid EventId, Guid SeatId, string UserId);