using Booking.DataAccess;
using Booking.Entities;
using Contracts.Messages;
using Microsoft.Extensions.Logging;

namespace Booking.Business;

public class BookingRules
{
    public TimeSpan HoldDuration { get; set; } = TimeSpan.FromMinutes(2);
    // La consigna no define precios: usamos un monto fijo configurable (simplificación documentada).
    public long SeatPriceCents { get; set; } = 500000;
}

public record ReservationStatusDto(Guid RequestId, Guid ReservationId, string Status,
    string? Reason, DateTime ExpiresAtUtc);

public class ReservationService
{
    private readonly IReservationRepository _repo;
    private readonly IPaymentGateway _payments;
    private readonly BookingRules _rules;
    private readonly ILogger<ReservationService> _logger;

    public ReservationService(IReservationRepository repo, IPaymentGateway payments,
        BookingRules rules, ILogger<ReservationService> logger)
    {
        _repo = repo;
        _payments = payments;
        _rules = rules;
        _logger = logger;
    }

    public async Task ProcessRequestAsync(ReservationRequestedMessage msg, CancellationToken ct)
    {
        _logger.LogInformation("AUDITORIA inicio reserva. CorrelationId={CorrelationId} RequestId={RequestId} SeatId={SeatId}",
            msg.CorrelationId, msg.RequestId, msg.SeatId);

        if (await _repo.GetByRequestIdAsync(msg.RequestId, ct) is not null)
        {
            _logger.LogInformation("Solicitud duplicada ignorada. CorrelationId={CorrelationId}", msg.CorrelationId);
            return;
        }

        var reservation = Build(msg, ReservationStatus.Retenida, null);
        var created = await _repo.TryAddAsync(reservation, ct);

        if (created == CreateResult.DuplicateRequest)
        {
            _logger.LogInformation("Solicitud duplicada concurrente ignorada. CorrelationId={CorrelationId}", msg.CorrelationId);
            return;
        }

        if (created == CreateResult.SeatTaken)
        {
            await _repo.TryAddAsync(Build(msg, ReservationStatus.Rechazada, RejectionReason.AsientoOcupado), ct);
            _logger.LogInformation("AUDITORIA fin reserva. CorrelationId={CorrelationId} Resultado=Rechazada Motivo=AsientoOcupado",
                msg.CorrelationId);
            return;
        }

        var outcome = await _payments.ChargeAsync(reservation.Id, msg.UserId, _rules.SeatPriceCents,
            msg.CorrelationId, ct);

        ReservationStatus finalStatus;
        RejectionReason? reason;
        if (outcome == PaymentOutcome.Approved)
        {
            finalStatus = ReservationStatus.Confirmada;
            reason = null;
        }
        else
        {
            finalStatus = ReservationStatus.Rechazada;
            reason = outcome == PaymentOutcome.Declined
                ? RejectionReason.PagoFallido
                : RejectionReason.PagoNoDisponible;
        }

        var changed = await _repo.TryTransitionAsync(reservation.Id, ReservationStatus.Retenida, finalStatus, reason, ct);
        if (!changed)
        {
            // La reserva venció mientras esperábamos a Payment. Si el cobro fue aprobado habría
            // que reembolsarlo (compensación): queda documentado como mejora fuera del alcance.
            _logger.LogWarning("La reserva ya no estaba Retenida al recibir el resultado. CorrelationId={CorrelationId}",
                msg.CorrelationId);
        }

        _logger.LogInformation("AUDITORIA fin reserva. CorrelationId={CorrelationId} Resultado={Status} Motivo={Reason}",
            msg.CorrelationId, finalStatus, reason?.ToString() ?? "-");
    }

    public async Task<ReservationStatusDto?> GetStatusAsync(Guid requestId, CancellationToken ct)
    {
        var r = await _repo.GetByRequestIdAsync(requestId, ct);
        return r is null
            ? null
            : new ReservationStatusDto(r.RequestId, r.Id, r.Status.ToString(), r.Reason?.ToString(), r.ExpiresAtUtc);
    }

    public Task<int> ExpireOverdueAsync(CancellationToken ct) =>
        _repo.ExpireOverdueAsync(DateTime.UtcNow, ct);

    private Reservation Build(ReservationRequestedMessage msg, ReservationStatus status, RejectionReason? reason)
    {
        var now = DateTime.UtcNow;
        return new Reservation
        {
            Id = Guid.NewGuid(),
            RequestId = msg.RequestId,
            EventId = msg.EventId,
            SeatId = msg.SeatId,
            UserId = msg.UserId,
            Status = status,
            Reason = reason,
            CreatedAtUtc = now,
            ExpiresAtUtc = now + _rules.HoldDuration
        };
    }
}