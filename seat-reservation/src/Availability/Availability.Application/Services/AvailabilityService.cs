using Availability.Application.Abstractions;
using Availability.Domain.Entities;
using Contracts.Messages;
using Microsoft.Extensions.Logging;

namespace Availability.Application.Services;

public record EventDto(Guid Id, string Name, DateTime DateUtc);
public record SeatDto(Guid Id, string Label, bool Occupied);
public record ReservationResultDto(Guid RequestId, string Status, string? Reason);
public record MyReservationDto(Guid RequestId, Guid EventId, string EventName, DateTime EventDateUtc, string SeatLabel, string Status, string? Reason, DateTime CreatedAtUtc);

// Servicio de aplicación: orquesta los casos de uso. Las reglas viven acá y no en las
// entidades (dominio anémico).
public class AvailabilityService
{
    private readonly IAvailabilityRepository _repo;
    private readonly IReservationPublisher _publisher;
    private readonly IBookingClient _booking;
    private readonly ILogger<AvailabilityService> _logger;

    public AvailabilityService(IAvailabilityRepository repo, IReservationPublisher publisher,
        IBookingClient booking, ILogger<AvailabilityService> logger)
    {
        _repo = repo;
        _publisher = publisher;
        _booking = booking;
        _logger = logger;
    }

    public async Task<IReadOnlyList<EventDto>> ListEventsAsync(CancellationToken ct)
    {
        var events = await _repo.ListEventsAsync(ct);
        return events.Select(e => new EventDto(e.Id, e.Name, e.DateUtc)).ToList();
    }

    // Punto 1 del flujo: devuelve asientos disponibles y ocupados. Availability no sabe qué
    // reservas existen (eso es de Booking), así que se lo pregunta con el GET del diagrama.
    // Por la consistencia eventual, un asiento recién solicitado puede verse libre unos
    // instantes: si otro se lo gana, Booking rechaza la reserva por "asiento ocupado".
    public async Task<IReadOnlyList<SeatDto>?> GetSeatsAsync(Guid eventId, CancellationToken ct)
    {
        if (await _repo.GetEventAsync(eventId, ct) is null) return null;

        var seats = await _repo.GetSeatsAsync(eventId, ct);
        var occupied = (await _booking.GetOccupiedSeatIdsAsync(eventId, ct)).ToHashSet();

        return seats
            .OrderBy(s => s.Label[..1]).ThenBy(s => s.Label.Length).ThenBy(s => s.Label) // A1..A9, A10, B1...
            .Select(s => new SeatDto(s.Id, s.Label, occupied.Contains(s.Id)))
            .ToList();
    }

    // Punto 3 del flujo: verifica el asiento, registra la solicitud con id único y la
    // publica. NO espera el resultado: responde "recibida" de inmediato.
    // Devuelve null si el asiento no existe.
    public async Task<Guid?> RequestReservationAsync(Guid eventId, Guid seatId, string userId,
        string correlationId, CancellationToken ct)
    {
        _logger.LogInformation("AUDITORIA inicio solicitud. CorrelationId={CorrelationId} SeatId={SeatId}",
            correlationId, seatId);

        if (await _repo.GetSeatAsync(eventId, seatId, ct) is null)
        {
            _logger.LogInformation("AUDITORIA fin solicitud. CorrelationId={CorrelationId} Resultado=AsientoInexistente",
                correlationId);
            return null;
        }

        var request = new ReservationRequest
        {
            Id = Guid.NewGuid(),
            EventId = eventId,
            SeatId = seatId,
            UserId = userId,
            CreatedAtUtc = DateTime.UtcNow
        };

        // Primero guardamos y después publicamos. Si publicar falla, el usuario recibe un
        // error y puede reintentar: queda una solicitud sin mensaje, que es inofensiva.
        // Al revés (publicar y después guardar) Booking podría procesar algo que
        // Availability no registró. La solución completa a esta doble escritura sería un
        // patrón Outbox; queda fuera del alcance del TP.
        await _repo.AddRequestAsync(request, ct);
        await _publisher.PublishAsync(
            new ReservationRequestedMessage(request.Id, eventId, seatId, userId, request.CreatedAtUtc, correlationId), ct);

        _logger.LogInformation("AUDITORIA fin solicitud. CorrelationId={CorrelationId} RequestId={RequestId} Resultado=Publicada",
            correlationId, request.Id);
        return request.Id;
    }

    // Punto 7 del flujo: el usuario consulta a Availability y este consulta a Booking.
    // Un usuario solo puede ver el resultado de SUS solicitudes. Para las ajenas respondemos
    // igual que para las inexistentes (null -> 404) y no revelamos que existen.
    public async Task<ReservationResultDto?> GetResultAsync(Guid requestId, string userId, CancellationToken ct)
    {
        var request = await _repo.GetRequestAsync(requestId, ct);
        if (request is null || request.UserId != userId) return null;

        var status = await _booking.GetStatusAsync(requestId, ct);

        // CONSISTENCIA EVENTUAL: entre que Availability publicó y Booking decidió, Booking
        // todavía no conoce la solicitud. Ese intervalo se muestra como "EnProceso".
        return status is null
            ? new ReservationResultDto(requestId, "EnProceso", null)
            : new ReservationResultDto(requestId, status.Status, status.Reason);
    }

    // Lista las reservas de un usuario en cualquier estado. 
    public async Task<IReadOnlyList<MyReservationDto>> GetMyReservationsAsync(string userId, CancellationToken ct)
    {
        var reservations = await _booking.GetReservationsByUserAsync(userId, ct);

        // Se consulta una vez por evento distinto (no una vez por reserva).
        var events = new Dictionary<Guid, Event>();
        var seatLabels = new Dictionary<Guid, string>();
        foreach (var eventId in reservations.Select(r => r.EventId).Distinct())
        {
            var ev = await _repo.GetEventAsync(eventId, ct);
            if (ev is null) continue;
            events[eventId] = ev;
            foreach (var seat in await _repo.GetSeatsAsync(eventId, ct))
                seatLabels[seat.Id] = seat.Label;
        }

        return reservations
            .Select(r =>
            {
                events.TryGetValue(r.EventId, out var ev);
                return new MyReservationDto(r.RequestId, r.EventId, ev?.Name ?? "Evento desconocido",
                    ev?.DateUtc ?? default, seatLabels.GetValueOrDefault(r.SeatId, "?"),
                    r.Status, r.Reason, r.CreatedAtUtc);
            })
            .ToList();
    }    
}