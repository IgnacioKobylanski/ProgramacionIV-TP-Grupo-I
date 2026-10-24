namespace Booking.Business;

public enum PaymentOutcome
{
    Approved,
    Declined,
    Unavailable
}

public interface IPaymentGateway
{
    Task<PaymentOutcome> ChargeAsync(Guid reservationId, string userId, long amountCents,
        string correlationId, CancellationToken ct);
}