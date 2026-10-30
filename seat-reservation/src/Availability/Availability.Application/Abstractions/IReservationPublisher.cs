using Contracts.Messages;

namespace Availability.Application.Abstractions;

// Puerto de salida hacia el broker (flecha PUBLISH del diagrama oficial).
// Application no depende de RabbitMQ: esa implementación queda a cargo de Infrastructure.
public interface IReservationPublisher
{
    Task PublishAsync(ReservationRequestedMessage message, CancellationToken ct);
}