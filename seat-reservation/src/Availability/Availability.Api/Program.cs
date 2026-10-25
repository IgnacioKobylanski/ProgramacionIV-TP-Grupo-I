using Availability.Api;
using Availability.Application.Services;
using Availability.Infrastructure;
using Availability.Infrastructure.Persistence;
using Azure.Messaging.ServiceBus;

var builder = WebApplication.CreateBuilder(args);

var serviceBusConnection = builder.Configuration["ServiceBus:ConnectionString"];
if (string.IsNullOrWhiteSpace(serviceBusConnection))
    throw new InvalidOperationException(
        "Falta ServiceBus:ConnectionString. Configurala con user-secrets (ver README).");

builder.Services.AddInfrastructure(new InfrastructureOptions
{
    Database = builder.Configuration.GetConnectionString("Availability")!,
    ServiceBusConnectionString = serviceBusConnection,
    ServiceBusTopic = builder.Configuration["ServiceBus:TopicName"]!,
    BookingBaseUrl = builder.Configuration["Booking:BaseUrl"]!
});
builder.Services.AddScoped<AvailabilityService>();

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    await DbSeeder.InitializeAsync(scope.ServiceProvider.GetRequiredService<AvailabilityDbContext>());
}

// Consultas públicas: el enunciado dice que no requieren iniciar sesión.
app.MapGet("/events", async (AvailabilityService svc, CancellationToken ct) =>
    Results.Ok(await svc.ListEventsAsync(ct)));

app.MapGet("/events/{eventId:guid}/seats", async (Guid eventId, AvailabilityService svc, CancellationToken ct) =>
{
    var seats = await svc.GetSeatsAsync(eventId, ct);
    return seats is null ? Results.NotFound() : Results.Ok(seats);
});

// Solicitud de reserva: responde 202 (aceptada, no terminada). El resultado se consulta después.
// Pendiente: exigir token (hoy es anónimo).
app.MapPost("/reservations", async (ReservationRequestBody body, HttpContext http,
    AvailabilityService svc, CancellationToken ct) =>
{
    var correlationId = http.Request.Headers["X-Correlation-Id"].FirstOrDefault() ?? Guid.NewGuid().ToString();
    try
    {
        var requestId = await svc.RequestReservationAsync(body.EventId, body.SeatId, body.UserId, correlationId, ct);
        return requestId is null
            ? Results.NotFound(new { error = "El asiento no existe para ese evento" })
            : Results.Accepted($"/reservations/{requestId}", new { requestId, correlationId });
    }
    catch (ServiceBusException)
    {
        return Results.StatusCode(StatusCodes.Status503ServiceUnavailable);
    }
});

app.MapGet("/reservations/{requestId:guid}", async (Guid requestId, AvailabilityService svc, CancellationToken ct) =>
{
    try
    {
        var result = await svc.GetResultAsync(requestId, ct);
        return result is null ? Results.NotFound() : Results.Ok(result);
    }
    catch (HttpRequestException)
    {
        // Booking no responde: lo informamos en lugar de un error genérico.
        return Results.StatusCode(StatusCodes.Status503ServiceUnavailable);
    }
});

app.Run();