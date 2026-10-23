namespace Payment.Entities;

public enum PaymentStatus
{
    Aprobado = 1,
    Rechazado = 2
}

public class PaymentRecord
{
    public Guid Id { get; set; }
    public Guid ReservationId { get; set; }
    public string UserId { get; set; } = string.Empty;
    public decimal Amount { get; set; }
    public PaymentStatus Status { get; set; }
    public string? Reason { get; set; }
    public DateTime CreatedAtUtc { get; set; }
}