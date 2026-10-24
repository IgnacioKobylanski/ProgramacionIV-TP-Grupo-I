using Contracts.Payments;
using Grpc.Core;
using Microsoft.Extensions.Logging;

namespace Booking.Business.Integration;

// Cliente gRPC hacia Payment (flecha CALL del diagrama oficial).
public class GrpcPaymentGateway : IPaymentGateway
{
    private readonly PaymentProcessor.PaymentProcessorClient _client;
    private readonly ILogger<GrpcPaymentGateway> _logger;

    public GrpcPaymentGateway(PaymentProcessor.PaymentProcessorClient client, ILogger<GrpcPaymentGateway> logger)
    {
        _client = client;
        _logger = logger;
    }

    public async Task<PaymentOutcome> ChargeAsync(Guid reservationId, string userId, long amountCents,
        string correlationId, CancellationToken ct)
    {
        try
        {
            var reply = await _client.ChargeReservationAsync(
                new ChargeRequest
                {
                    ReservationId = reservationId.ToString(),
                    UserId = userId,
                    AmountCents = amountCents,
                    CorrelationId = correlationId
                },
                deadline: DateTime.UtcNow.AddSeconds(5),
                cancellationToken: ct);

            return reply.Approved ? PaymentOutcome.Approved : PaymentOutcome.Declined;
        }
        catch (RpcException ex)
        {
            _logger.LogWarning("Payment no disponible. CorrelationId={CorrelationId} Codigo={Code}",
                correlationId, ex.StatusCode);
            return PaymentOutcome.Unavailable;
        }
    }
}