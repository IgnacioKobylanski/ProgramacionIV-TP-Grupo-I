using Booking.Api;
using Booking.Business;
using Booking.Business.Integration;
using Booking.DataAccess;
using Contracts.Payments;
using Microsoft.EntityFrameworkCore;
using ServiceAuth;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<BookingDbContext>(o =>
    o.UseNpgsql(builder.Configuration.GetConnectionString("Booking")));
builder.Services.AddScoped<IReservationRepository, ReservationRepository>();

builder.Services.AddSingleton(new BookingRules
{
    HoldDuration = TimeSpan.FromSeconds(builder.Configuration.GetValue<int>("Booking:HoldSeconds", 120)),
    SeatPriceCents = builder.Configuration.GetValue<long>("Booking:SeatPriceCents", 500000)
});

// AUTENTICACIÓN ENTRE SERVICIOS (punto e).
// Como CLIENTE: Booking se identifica ante Keycloak como "booking-service" y manda su token
// a Payment y a Notifications.
builder.Services.AddServiceAuth(new ServiceAuthOptions
{
    TokenEndpoint = builder.Configuration["ServiceAuth:TokenEndpoint"]!,
    ClientId = builder.Configuration["ServiceAuth:ClientId"]!,
    ClientSecret = builder.Configuration["ServiceAuth:ClientSecret"]!
});
// Como RECEPTOR: solo acepta llamadas de Availability (la flecha GET del diagrama).
builder.Services.AddKeycloakJwtBearer(builder.Configuration);
builder.Services.AddAuthorizationBuilder()
    .AddServicePolicy("AvailabilityOnly", "availability-service");

// Cliente gRPC hacia Payment (flecha CALL del diagrama), generado desde el contrato compartido.
builder.Services.AddGrpcClient<PaymentProcessor.PaymentProcessorClient>(o =>
        o.Address = new Uri(builder.Configuration["Payment:Address"]!))
    .AddHttpMessageHandler<ServiceTokenHandler>();
builder.Services.AddScoped<IPaymentGateway, GrpcPaymentGateway>();

// Cliente HTTP hacia Notifications. Timeout corto: no queremos demorar la confirmación.
builder.Services.AddHttpClient<INotificationGateway, HttpNotificationGateway>(c =>
{
    c.BaseAddress = new Uri(builder.Configuration["Notifications:BaseUrl"]!);
    c.Timeout = TimeSpan.FromSeconds(3);
})
    .AddHttpMessageHandler<ServiceTokenHandler>();

builder.Services.AddScoped<ReservationService>();
builder.Services.AddHostedService<ReservationExpiryWorker>();
builder.Services.AddHostedService<ReservationRequestConsumer>();

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    await scope.ServiceProvider.GetRequiredService<BookingDbContext>().Database.MigrateAsync();
}

app.UseAuthentication();
app.UseAuthorization();

// Flecha GET del diagrama oficial (Availability -> Booking).
// Un 404 significa "todavía no procesada" (consistencia eventual): Availability lo
// traduce como "EnProceso" para el usuario.
app.MapGet("/reservations/{requestId:guid}", async (Guid requestId, ReservationService svc, CancellationToken ct) =>
{
    var status = await svc.GetStatusAsync(requestId, ct);
    return status is null ? Results.NotFound() : Results.Ok(status);
}).RequireAuthorization("AvailabilityOnly");

// Availability pregunta qué asientos están ocupados para mostrar solo los libres.
app.MapGet("/events/{eventId:guid}/occupied-seats", async (Guid eventId, ReservationService svc, CancellationToken ct) =>
    Results.Ok(await svc.GetOccupiedSeatsAsync(eventId, ct))).RequireAuthorization("AvailabilityOnly");

app.Run();