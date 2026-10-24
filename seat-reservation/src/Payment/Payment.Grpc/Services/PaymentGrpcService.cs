using Contracts.Payments;
using Grpc.Core;
using Payment.Business;

namespace Payment.Grpc.Services;

public class PaymentGrpcService : PaymentProcessor.PaymentProcessorBase
{
    private readonly PaymentService _service;
    private readonly ILogger<PaymentGrpcService> _logger;

    public PaymentGrpcService(PaymentService service, ILogger<PaymentGrpcService> logger)
    {
        _service = service;
        _logger = logger;
    }

    public override async Task<ChargeReply> ChargeReservation(ChargeRequest request, ServerCallContext context)
    {
        if (!Guid.TryParse(request.ReservationId, out var reservationId))
            throw new RpcException(new Status(StatusCode.InvalidArgument, "reservation_id inválido"));

        _logger.LogInformation("AUDITORIA inicio cobro. CorrelationId={CorrelationId} ReservationId={ReservationId}",
            request.CorrelationId, reservationId);

        var result = await _service.ProcessAsync(
            reservationId, request.UserId, request.AmountCents / 100m, context.CancellationToken);

        _logger.LogInformation("AUDITORIA fin cobro. CorrelationId={CorrelationId} ReservationId={ReservationId} Aprobado={Approved}",
            request.CorrelationId, reservationId, result.Approved);

        return new ChargeReply
        {
            Approved = result.Approved,
            PaymentId = result.PaymentId.ToString(),
            Reason = result.Reason ?? string.Empty
        };
    }
}