using System.Net.Http.Json;
using Contracts.Messages;

namespace Booking.Business.Integration;

// Adaptador HTTP hacia Notifications. Lanza excepción si falla: quién decide qué hacer
// con el error es la capa de negocio.
public class HttpNotificationGateway : INotificationGateway
{
    private readonly HttpClient _http;

    public HttpNotificationGateway(HttpClient http) => _http = http;

    public async Task NotifyConfirmedAsync(ReservationConfirmedNotification notification, CancellationToken ct)
    {
        using var response = await _http.PostAsJsonAsync("notifications", notification, ct);
        response.EnsureSuccessStatusCode();
    }
}