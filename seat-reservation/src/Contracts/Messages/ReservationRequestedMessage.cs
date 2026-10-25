namespace Contracts.Messages;

// Mensaje que viaja por el broker (glosario: "Mensaje").
// Es un record inmutable porque un contrato entre microservicios no debe
// mutar una vez publicado. Vive en un proyecto compartido (Contracts) para
// que Availability y Booking acuerden la forma sin acoplarse a sus dominios.
public record ReservationRequestedMessage(
    Guid RequestId,          // identificador único de la solicitud (también sirve para idempotencia)
    Guid EventId,
    Guid SeatId,
    string UserId,
    DateTime RequestedAtUtc,
    string CorrelationId);   // une los logs de auditoría de toda la cadena de sucesos