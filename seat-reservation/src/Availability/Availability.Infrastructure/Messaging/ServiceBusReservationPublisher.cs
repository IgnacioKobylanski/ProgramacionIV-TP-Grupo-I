using System.Text.Json;
using Availability.Application.Abstractions;
using Azure.Messaging.ServiceBus;
using Contracts.Messages;

namespace Availability.Infrastructure.Messaging;

// Adaptador: implementa el puerto de publicación con Azure Service Bus (topic).
public class ServiceBusReservationPublisher : IReservationPublisher, IAsyncDisposable
{
    private readonly ServiceBusClient _client;
    private readonly ServiceBusSender _sender;

    public ServiceBusReservationPublisher(string connectionString, string topicName)
    {
        _client = new ServiceBusClient(connectionString);
        _sender = _client.CreateSender(topicName);
    }

    public Task PublishAsync(ReservationRequestedMessage msg, CancellationToken ct)
    {
        var message = new ServiceBusMessage(JsonSerializer.Serialize(msg))
        {
            // El id de la solicitud es también el MessageId. No dependemos de la detección
            // de duplicados del broker: Booking es idempotente por RequestId.
            MessageId = msg.RequestId.ToString(),
            CorrelationId = msg.CorrelationId,
            ContentType = "application/json"
        };
        return _sender.SendMessageAsync(message, ct);
    }

    public async ValueTask DisposeAsync()
    {
        await _sender.DisposeAsync();
        await _client.DisposeAsync();
    }
}