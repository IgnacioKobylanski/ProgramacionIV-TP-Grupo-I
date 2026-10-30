using System.Text;
using System.Text.Json;
using Availability.Application.Abstractions;
using Contracts.Messages;
using RabbitMQ.Client;

namespace Availability.Infrastructure.Messaging;

// Adaptador: implementa el puerto de publicación con RabbitMQ (exchange fanout).
public class RabbitMqReservationPublisher : IReservationPublisher, IAsyncDisposable
{
    private readonly ConnectionFactory _factory;
    private readonly SemaphoreSlim _gate = new(1, 1);
    private IConnection? _connection;
    private IChannel? _channel;

    public RabbitMqReservationPublisher(string host, int port, string user, string password)
    {
        _factory = new ConnectionFactory
        {
            HostName = host,
            Port = port,
            UserName = user,
            Password = password,
            // Si el broker está caído conviene fallar rápido y responder 503, no esperar 30 s.
            RequestedConnectionTimeout = TimeSpan.FromSeconds(5)
        };
    }

    public async Task PublishAsync(ReservationRequestedMessage msg, CancellationToken ct)
    {
        // Un solo canal compartido: se serializan las publicaciones para no depender de
        // cómo maneja el cliente la concurrencia sobre un mismo canal.
        await _gate.WaitAsync(ct);
        try
        {
            var channel = await EnsureChannelAsync(ct);
            var props = new BasicProperties
            {
                // El id de la solicitud es también el MessageId. No dependemos de la detección
                // de duplicados del broker: Booking es idempotente por RequestId.
                MessageId = msg.RequestId.ToString(),
                CorrelationId = msg.CorrelationId,
                ContentType = "application/json",
                DeliveryMode = DeliveryModes.Persistent
            };
            var body = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(msg));

            // Con confirmaciones activas, esta línea termina cuando el broker aceptó el mensaje.
            await channel.BasicPublishAsync(BrokerTopology.Exchange, routingKey: "", mandatory: false,
                basicProperties: props, body: body, cancellationToken: ct);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            // Se descarta la conexión para armarla de nuevo en el próximo intento.
            await DiscardAsync();
            throw new BrokerUnavailableException("No se pudo publicar en el broker", ex);
        }
        finally
        {
            _gate.Release();
        }
    }

    private async Task<IChannel> EnsureChannelAsync(CancellationToken ct)
    {
        if (_channel is { IsOpen: true }) return _channel;

        await DiscardAsync();
        _connection = await _factory.CreateConnectionAsync(ct);
        _channel = await _connection.CreateChannelAsync(
            new CreateChannelOptions(publisherConfirmationsEnabled: true, publisherConfirmationTrackingEnabled: true),
            ct);

        // Misma declaración que en Booking (ver Contracts.Messages.BrokerTopology). Si Availability
        // publicara antes de que exista la cola, RabbitMQ descartaría el mensaje: por eso se declara acá también.
        await _channel.ExchangeDeclareAsync(BrokerTopology.DeadLetterExchange, ExchangeType.Fanout,
            durable: true, cancellationToken: ct);
        await _channel.QueueDeclareAsync(BrokerTopology.DeadLetterQueue, durable: true, exclusive: false,
            autoDelete: false, cancellationToken: ct);
        await _channel.QueueBindAsync(BrokerTopology.DeadLetterQueue, BrokerTopology.DeadLetterExchange,
            routingKey: "", cancellationToken: ct);

        await _channel.ExchangeDeclareAsync(BrokerTopology.Exchange, ExchangeType.Fanout,
            durable: true, cancellationToken: ct);
        await _channel.QueueDeclareAsync(BrokerTopology.Queue, durable: true, exclusive: false,
            autoDelete: false, arguments: BrokerTopology.QueueArguments(), cancellationToken: ct);
        await _channel.QueueBindAsync(BrokerTopology.Queue, BrokerTopology.Exchange,
            routingKey: "", cancellationToken: ct);

        return _channel;
    }

    private async Task DiscardAsync()
    {
        try { if (_channel is not null) await _channel.DisposeAsync(); } catch { }
        try { if (_connection is not null) await _connection.DisposeAsync(); } catch { }
        _channel = null;
        _connection = null;
    }

    public async ValueTask DisposeAsync()
    {
        await DiscardAsync();
        _gate.Dispose();
    }
}