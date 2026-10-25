namespace Notifications.Models;

public class Notification
{
    public Guid Id { get; set; }
    public Guid ReservationId { get; set; }
    public string UserId { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
    public DateTime SentAtUtc { get; set; }
}