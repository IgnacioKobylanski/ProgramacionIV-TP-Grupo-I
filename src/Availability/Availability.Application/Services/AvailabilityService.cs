using Availability.Application.Abstractions;

namespace Availability.Application.Services;

public record EventDto(Guid Id, string Name, DateTime DateUtc);
public record SeatDto(Guid Id, string Label);


public class AvailabilityService
{
    private readonly IAvailabilityRepository _repo;

    public AvailabilityService(IAvailabilityRepository repo) => _repo = repo;

    public async Task<IReadOnlyList<EventDto>> ListEventsAsync(CancellationToken ct)
    {
        var events = await _repo.ListEventsAsync(ct);
        return events.Select(e => new EventDto(e.Id, e.Name, e.DateUtc)).ToList();
    }

    public async Task<IReadOnlyList<SeatDto>?> GetSeatsAsync(Guid eventId, CancellationToken ct)
    {
        if (await _repo.GetEventAsync(eventId, ct) is null) return null;

        var seats = await _repo.GetSeatsAsync(eventId, ct);
        return seats.Select(s => new SeatDto(s.Id, s.Label)).ToList();
    }
}