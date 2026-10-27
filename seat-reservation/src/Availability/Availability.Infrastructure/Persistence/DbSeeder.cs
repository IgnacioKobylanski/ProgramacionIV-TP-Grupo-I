using Availability.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace Availability.Infrastructure.Persistence;

public static class DbSeeder
{
    // IDs fijos y legibles para poder probar a mano sin copiar GUIDs aleatorios.
    public static readonly Guid DemoEventId = Guid.Parse("11111111-1111-1111-1111-111111111111");

    private record SeedEvent(Guid Id, int Number, string Name, int DaysFromNow, string[] Rows, int SeatsPerRow);

    private static readonly SeedEvent[] Events =
    [
        new(DemoEventId, 0, "Recital de prueba", 30, ["A", "B"], 10),
        new(Guid.Parse("22222222-2222-2222-2222-222222222222"), 1, "Conferencia de tecnología", 45, ["A", "B", "C"], 8),
        new(Guid.Parse("33333333-3333-3333-3333-333333333333"), 2, "Obra de teatro", 60, ["A", "B", "C", "D"], 6),
    ];

    public static async Task InitializeAsync(AvailabilityDbContext db)
    {
        // Aplica las migraciones pendientes: el esquema queda versionado en el repo.
        await db.Database.MigrateAsync();

        foreach (var e in Events)
        {
            // Idempotente: agrega solo los eventos que faltan, así funciona también sobre una base ya existente.
            if (await db.Events.AnyAsync(x => x.Id == e.Id)) continue;

            var ev = new Event { Id = e.Id, Name = e.Name, DateUtc = DateTime.UtcNow.AddDays(e.DaysFromNow) };
            var n = 1;
            foreach (var row in e.Rows)
                for (var number = 1; number <= e.SeatsPerRow; number++, n++)
                    ev.Seats.Add(new Seat
                    {
                        // El evento 0 conserva los ids de antes (...0000-000000000001); los otros llevan su número.
                        Id = new Guid($"00000000-0000-0000-{e.Number:D4}-{n:D12}"),
                        EventId = ev.Id,
                        Label = $"{row}{number}"
                    });
            db.Events.Add(ev);
        }
        await db.SaveChangesAsync();
    }
}