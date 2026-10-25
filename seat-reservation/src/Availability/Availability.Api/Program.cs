using System.Security.Claims;
using Availability.Api;
using Availability.Application.Services;
using Availability.Infrastructure;
using Availability.Infrastructure.Persistence;
using Azure.Messaging.ServiceBus;
using Microsoft.AspNetCore.Authentication.JwtBearer;

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

// AUTENTICACIÓN: Availability NO guarda contraseñas ni emite tokens. Eso lo hace el servidor
// de autorización del diagrama oficial (Keycloak). Acá solo se verifica que el token tenga
// firma válida, que lo haya emitido nuestro realm y que no esté vencido.
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o =>
    {
        o.Authority = builder.Configuration["Auth:Authority"];
        o.RequireHttpsMetadata = builder.Configuration.GetValue<bool>("Auth:RequireHttpsMetadata");
        // Conservamos los nombres originales de los claims (sub, preferred_username).
        o.MapInboundClaims = false;
        // Simplificación documentada: Keycloak no incluye nuestra API en "aud" por defecto.
        // Se valida firma, emisor y vigencia; el control por audiencia queda como mejora.
        o.TokenValidationParameters.ValidateAudience = false;
    });
builder.Services.AddAuthorization();

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    await DbSeeder.InitializeAsync(scope.ServiceProvider.GetRequiredService<AvailabilityDbContext>());
}

app.UseAuthentication();
app.UseAuthorization();

// El usuario sale del token (nombre de usuario; si no está, el identificador "sub").
static string? UserIdOf(ClaimsPrincipal user) =>
    user.FindFirst("preferred_username")?.Value ?? user.FindFirst("sub")?.Value;

// Consultas públicas: el enunciado dice que no requieren iniciar sesión.
app.MapGet("/events", async (AvailabilityService svc, CancellationToken ct) =>
    Results.Ok(await svc.ListEventsAsync(ct)));

app.MapGet("/events/{eventId:guid}/seats", async (Guid eventId, AvailabilityService svc, CancellationToken ct) =>
{
    try
    {
        var seats = await svc.GetSeatsAsync(eventId, ct);
        return seats is null ? Results.NotFound() : Results.Ok(seats);
    }
    catch (HttpRequestException)
    {
        // Sin Booking no sabemos qué asientos están ocupados: preferimos un 503 antes que
        // mostrar como libres asientos que no lo están.
        return Results.StatusCode(StatusCodes.Status503ServiceUnavailable);
    }
});

// Para reservar hace falta un token (punto 2 del flujo). Responde 202: aceptada, no terminada.
app.MapPost("/reservations", async (ReservationRequestBody body, HttpContext http,
    AvailabilityService svc, CancellationToken ct) =>
{
    var userId = UserIdOf(http.User);
    if (userId is null) return Results.Unauthorized();

    var correlationId = http.Request.Headers["X-Correlation-Id"].FirstOrDefault() ?? Guid.NewGuid().ToString();
    try
    {
        var requestId = await svc.RequestReservationAsync(body.EventId, body.SeatId, userId, correlationId, ct);
        return requestId is null
            ? Results.NotFound(new { error = "El asiento no existe para ese evento" })
            : Results.Accepted($"/reservations/{requestId}", new { requestId, correlationId });
    }
    catch (ServiceBusException)
    {
        return Results.StatusCode(StatusCodes.Status503ServiceUnavailable);
    }
}).RequireAuthorization();

// Consultar el resultado también requiere token, y solo se ve lo propio.
app.MapGet("/reservations/{requestId:guid}", async (Guid requestId, HttpContext http,
    AvailabilityService svc, CancellationToken ct) =>
{
    var userId = UserIdOf(http.User);
    if (userId is null) return Results.Unauthorized();

    try
    {
        var result = await svc.GetResultAsync(requestId, userId, ct);
        return result is null ? Results.NotFound() : Results.Ok(result);
    }
    catch (HttpRequestException)
    {
        // Booking no responde: lo informamos en lugar de un error genérico.
        return Results.StatusCode(StatusCodes.Status503ServiceUnavailable);
    }
}).RequireAuthorization();

app.Run();