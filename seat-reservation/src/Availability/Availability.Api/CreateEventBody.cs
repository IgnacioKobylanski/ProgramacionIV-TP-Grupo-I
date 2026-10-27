namespace Availability.Api;

public record CreateEventBody(string Name, DateTime DateUtc, int Rows, int SeatsPerRow);