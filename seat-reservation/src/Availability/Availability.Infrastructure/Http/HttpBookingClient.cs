using System.Net;
using System.Net.Http.Json;
using Availability.Application.Abstractions;

namespace Availability.Infrastructure.Http;

// Adaptador HTTP hacia Booking (flecha GET del diagrama oficial).
public class HttpBookingClient : IBookingClient
{
    private readonly HttpClient _http;

    public HttpBookingClient(HttpClient http) => _http = http;

    private record BookingResponse(string Status, string? Reason);

    public async Task<BookingStatus?> GetStatusAsync(Guid requestId, CancellationToken ct)
    {
        var response = await _http.GetAsync($"reservations/{requestId}", ct);

        // 404 = Booking todavía no procesó la solicitud (no es un error).
        if (response.StatusCode == HttpStatusCode.NotFound) return null;

        response.EnsureSuccessStatusCode();
        var body = await response.Content.ReadFromJsonAsync<BookingResponse>(ct);
        return body is null ? null : new BookingStatus(body.Status, body.Reason);
    }

    public async Task<IReadOnlyList<Guid>> GetOccupiedSeatIdsAsync(Guid eventId, CancellationToken ct) =>
    await _http.GetFromJsonAsync<List<Guid>>($"events/{eventId}/occupied-seats", ct) ?? new List<Guid>();


    // El userId va en la URL.
    public async Task<IReadOnlyList<BookingReservation>> GetReservationsByUserAsync(string userId, CancellationToken ct) =>
        await _http.GetFromJsonAsync<List<BookingReservation>>(
            $"reservations?userId={Uri.EscapeDataString(userId)}", ct) ?? new List<BookingReservation>();
}