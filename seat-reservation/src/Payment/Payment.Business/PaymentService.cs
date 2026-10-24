using Payment.DataAccess;
using Payment.Entities;

namespace Payment.Business;

public record PaymentResult(bool Approved, Guid PaymentId, string? Reason);

// Regla de simulación configurable desde appsettings (sin dinero real).
public class PaymentRules
{
    public decimal MaxAmount { get; set; } = 100000m;
}

// Capa de negocio: el cobro es una SIMULACIÓN. La consigna pide el resultado
// del pago, no una pasarela real. Se rechaza si el monto es inválido o excede el máximo.
public class PaymentService
{
    private readonly IPaymentRepository _repo;
    private readonly PaymentRules _rules;

    public PaymentService(IPaymentRepository repo, PaymentRules rules)
    {
        _repo = repo;
        _rules = rules;
    }

    public async Task<PaymentResult> ProcessAsync(Guid reservationId, string userId, decimal amount, CancellationToken ct)
    {
        var approved = amount > 0 && amount <= _rules.MaxAmount;

        var record = new PaymentRecord
        {
            Id = Guid.NewGuid(),
            ReservationId = reservationId,
            UserId = userId,
            Amount = amount,
            Status = approved ? PaymentStatus.Aprobado : PaymentStatus.Rechazado,
            Reason = approved ? null : "Monto fuera del rango permitido",
            CreatedAtUtc = DateTime.UtcNow
        };

        var saved = await _repo.GetOrAddAsync(record, ct);
        return new PaymentResult(saved.Status == PaymentStatus.Aprobado, saved.Id, saved.Reason);
    }
}