namespace Availability.Domain.Entities;

public class Event
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public DateTime DateUtc { get; set; }
    public List<Seat> Seats { get; set; } = new();
}