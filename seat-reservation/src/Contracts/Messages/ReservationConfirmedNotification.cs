namespace Contracts.Messages;

// Cuerpo de la llamada HTTP de Booking a Notifications (punto h de la consigna).
// Va en Contracts para que ambos servicios compartan la misma forma.
public record ReservationConfirmedNotification(
    Guid ReservationId,
    Guid RequestId,
    Guid EventId,
    Guid SeatId,
    string UserId,
    DateTime ConfirmedAtUtc,
    string CorrelationId);