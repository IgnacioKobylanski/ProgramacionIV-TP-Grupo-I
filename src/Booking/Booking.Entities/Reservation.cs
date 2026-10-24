namespace Booking.Entities;

public enum ReservationStatus
{
    Retenida = 1,
    Confirmada = 2,
    Rechazada = 3,
    Vencida = 4
}

public enum RejectionReason
{
    AsientoOcupado = 1,
    PagoFallido = 2,
    PagoNoDisponible = 3
}

public class Reservation
{
    public Guid Id { get; set; }
    public Guid RequestId { get; set; }
    public Guid EventId { get; set; }
    public Guid SeatId { get; set; }
    public string UserId { get; set; } = string.Empty;
    public ReservationStatus Status { get; set; }
    public RejectionReason? Reason { get; set; }
    public DateTime CreatedAtUtc { get; set; }
    public DateTime ExpiresAtUtc { get; set; }
}