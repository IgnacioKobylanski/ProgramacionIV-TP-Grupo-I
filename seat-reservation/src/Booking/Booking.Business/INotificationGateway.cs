using Contracts.Messages;

namespace Booking.Business;

// Puerto hacia Notifications: la lógica de reservas no sabe que por debajo hay HTTP.
public interface INotificationGateway
{
    Task NotifyConfirmedAsync(ReservationConfirmedNotification notification, CancellationToken ct);
}