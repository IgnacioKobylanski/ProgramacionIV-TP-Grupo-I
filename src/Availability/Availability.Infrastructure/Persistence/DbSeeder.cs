using Availability.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace Availability.Infrastructure.Persistence;

public static class DbSeeder
{
    public static readonly Guid DemoEventId = Guid.Parse("11111111-1111-1111-1111-111111111111");

    public static async Task InitializeAsync(AvailabilityDbContext db)
    {
        await db.Database.MigrateAsync();

        if (await db.Events.AnyAsync()) return;

        var ev = new Event { Id = DemoEventId, Name = "Recital de prueba", DateUtc = DateTime.UtcNow.AddDays(30) };
        db.Events.Add(ev);

        var n = 1;
        foreach (var row in new[] { "A", "B" })
            for (var number = 1; number <= 10; number++, n++)
                db.Seats.Add(new Seat
                {
                    Id = new Guid($"00000000-0000-0000-0000-{n:D12}"),
                    EventId = ev.Id,
                    Label = $"{row}{number}"
                });

        await db.SaveChangesAsync();
    }
}