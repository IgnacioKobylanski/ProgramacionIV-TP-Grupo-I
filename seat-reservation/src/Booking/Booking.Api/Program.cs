using Booking.Api;
using Booking.Business;
using Booking.Business.Integration;
using Booking.DataAccess;
using Contracts.Messages;
using Contracts.Payments;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<BookingDbContext>(o =>
    o.UseNpgsql(builder.Configuration.GetConnectionString("Booking")));
builder.Services.AddScoped<IReservationRepository, ReservationRepository>();

builder.Services.AddSingleton(new BookingRules
{
    HoldDuration = TimeSpan.FromSeconds(builder.Configuration.GetValue<int>("Booking:HoldSeconds", 120)),
    SeatPriceCents = builder.Configuration.GetValue<long>("Booking:SeatPriceCents", 500000)
});

builder.Services.AddGrpcClient<PaymentProcessor.PaymentProcessorClient>(o =>
    o.Address = new Uri(builder.Configuration["Payment:Address"]!));
builder.Services.AddScoped<IPaymentGateway, GrpcPaymentGateway>();

builder.Services.AddScoped<ReservationService>();
builder.Services.AddHostedService<ReservationExpiryWorker>();

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    await scope.ServiceProvider.GetRequiredService<BookingDbContext>().Database.MigrateAsync();
}


app.MapGet("/reservations/{requestId:guid}", async (Guid requestId, ReservationService svc, CancellationToken ct) =>
{
    var status = await svc.GetStatusAsync(requestId, ct);
    return status is null ? Results.NotFound() : Results.Ok(status);
});

if (app.Environment.IsDevelopment())
{
    app.MapPost("/dev/reservations", async (ReservationRequestedMessage msg, ReservationService svc, CancellationToken ct) =>
    {
        await svc.ProcessRequestAsync(msg, ct);
        return Results.Ok(await svc.GetStatusAsync(msg.RequestId, ct));
    });
}

app.Run();