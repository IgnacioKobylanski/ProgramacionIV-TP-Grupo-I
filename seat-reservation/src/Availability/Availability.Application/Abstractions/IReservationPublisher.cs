using Contracts.Messages;

namespace Availability.Application.Abstractions;

// Puerto de salida hacia el broker (flecha PUBLISH del diagrama oficial).
// Application no sabe que por debajo hay Azure Service Bus: eso lo decide Infrastructure.
public interface IReservationPublisher
{
    Task PublishAsync(ReservationRequestedMessage message, CancellationToken ct);
}