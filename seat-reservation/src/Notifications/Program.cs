using Contracts.Messages;
using Microsoft.EntityFrameworkCore;
using Notifications.Data;
using Notifications.Models;
using ServiceAuth;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<NotificationsDbContext>(o =>
    o.UseNpgsql(builder.Configuration.GetConnectionString("Notifications")));

// AUTENTICACIÓN ENTRE SERVICIOS (punto e): solo Booking puede registrar notificaciones.
builder.Services.AddKeycloakJwtBearer(builder.Configuration);
builder.Services.AddAuthorizationBuilder()
    .AddServicePolicy("BookingOnly", "booking-service");

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    await scope.ServiceProvider.GetRequiredService<NotificationsDbContext>().Database.MigrateAsync();
}

app.UseAuthentication();
app.UseAuthorization();

// Punto h: Booking llama acá cuando el pago fue exitoso y la reserva quedó confirmada.
// El envío es una SIMULACIÓN: se registra la notificación y se escribe en el log.
app.MapPost("/notifications", async (ReservationConfirmedNotification n, NotificationsDbContext db,
    ILogger<Program> logger, CancellationToken ct) =>
{
    logger.LogInformation("AUDITORIA inicio notificacion. CorrelationId={CorrelationId} ReservationId={ReservationId}",
        n.CorrelationId, n.ReservationId);

    // Idempotente: si ya notificamos esta reserva, no se duplica.
    if (!await db.Notifications.AnyAsync(x => x.ReservationId == n.ReservationId, ct))
    {
        var message = $"Tu reserva fue confirmada. Evento {n.EventId}, asiento {n.SeatId}.";
        db.Notifications.Add(new Notification
        {
            Id = Guid.NewGuid(),
            ReservationId = n.ReservationId,
            UserId = n.UserId,
            Message = message,
            SentAtUtc = DateTime.UtcNow
        });
        await db.SaveChangesAsync(ct);

        logger.LogInformation("NOTIFICACION SIMULADA para {UserId}: {Message}", n.UserId, message);
    }

    logger.LogInformation("AUDITORIA fin notificacion. CorrelationId={CorrelationId} ReservationId={ReservationId}",
        n.CorrelationId, n.ReservationId);
    return Results.Ok();
}).RequireAuthorization("BookingOnly");

// Para consultar lo enviado (pruebas y evidencia): exige un token válido, de cualquier usuario.
app.MapGet("/notifications", async (NotificationsDbContext db, CancellationToken ct) =>
    Results.Ok(await db.Notifications.AsNoTracking()
        .OrderByDescending(n => n.SentAtUtc).Take(50).ToListAsync(ct))).RequireAuthorization();

app.Run();