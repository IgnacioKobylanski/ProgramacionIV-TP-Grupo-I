using Availability.Application.Services;
using Availability.Infrastructure;
using Availability.Infrastructure.Persistence;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddInfrastructure(builder.Configuration.GetConnectionString("Availability")!);
builder.Services.AddScoped<AvailabilityService>();

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    await DbSeeder.InitializeAsync(scope.ServiceProvider.GetRequiredService<AvailabilityDbContext>());
}

app.MapGet("/events", async (AvailabilityService svc, CancellationToken ct) =>
    Results.Ok(await svc.ListEventsAsync(ct)));

app.MapGet("/events/{eventId:guid}/seats", async (Guid eventId, AvailabilityService svc, CancellationToken ct) =>
{
    var seats = await svc.GetSeatsAsync(eventId, ct);
    return seats is null ? Results.NotFound() : Results.Ok(seats);
});

app.Run();