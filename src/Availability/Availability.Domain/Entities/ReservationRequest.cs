namespace Availability.Domain.Entities;

public class ReservationRequest
{
    public Guid Id { get; set; }
    public Guid EventId { get; set; }
    public Guid SeatId { get; set; }
    public string UserId { get; set; } = string.Empty;
    public DateTime CreatedAtUtc { get; set; }
}