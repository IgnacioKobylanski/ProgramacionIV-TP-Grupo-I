namespace Contracts.Messages;


public record ReservationRequestedMessage(
    Guid RequestId,
    Guid EventId,
    Guid SeatId,
    string UserId,
    DateTime RequestedAtUtc,
    string CorrelationId);