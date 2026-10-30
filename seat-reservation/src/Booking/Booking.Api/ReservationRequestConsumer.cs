using System.Text;
using System.Text.Json;
using Booking.Business;
using Contracts.Messages;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

namespace Booking.Api;

// Flecha SUBSCRIBE del diagrama oficial. Todas las réplicas de Booking consumen de la MISMA
// cola, y RabbitMQ entrega cada mensaje a una sola de ellas (consumidores competidores).
public class ReservationRequestConsumer : BackgroundService
{
    private readonly IConfiguration _config;
    private readonly IServiceScopeFactory _scopes;
    private readonly ILogger<ReservationRequestConsumer> _logger;

    public ReservationRequestConsumer(IConfiguration config, IServiceScopeFactory scopes,
        ILogger<ReservationRequestConsumer> logger)
    {
        _config = config;
        _scopes = scopes;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var factory = new ConnectionFactory
        {
            HostName = _config["RabbitMq:Host"] ?? "localhost",
            Port = _config.GetValue("RabbitMq:Port", 5672),
            UserName = _config["RabbitMq:User"] ?? "app",
            Password = _config["RabbitMq:Password"] ?? "app"
        };

        // El broker puede tardar unos segundos en aceptar conexiones: se reintenta en vez de caerse.
        IConnection? connection = null;
        while (connection is null)
        {
            try { connection = await factory.CreateConnectionAsync(stoppingToken); }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                _logger.LogWarning("No se pudo conectar a RabbitMQ: {Message}. Reintentando.", ex.Message);
                await Task.Delay(TimeSpan.FromSeconds(3), stoppingToken);
            }
        }

        await using var conexion = connection;
        await using var channel = await conexion.CreateChannelAsync(cancellationToken: stoppingToken);

        // Se declara la topología (es idempotente): así el orden de arranque de los servicios no importa.
        await channel.ExchangeDeclareAsync(BrokerTopology.DeadLetterExchange, ExchangeType.Fanout,
            durable: true, cancellationToken: stoppingToken);
        await channel.QueueDeclareAsync(BrokerTopology.DeadLetterQueue, durable: true, exclusive: false,
            autoDelete: false, cancellationToken: stoppingToken);
        await channel.QueueBindAsync(BrokerTopology.DeadLetterQueue, BrokerTopology.DeadLetterExchange,
            routingKey: "", cancellationToken: stoppingToken);

        await channel.ExchangeDeclareAsync(BrokerTopology.Exchange, ExchangeType.Fanout,
            durable: true, cancellationToken: stoppingToken);
        await channel.QueueDeclareAsync(BrokerTopology.Queue, durable: true, exclusive: false,
            autoDelete: false, arguments: BrokerTopology.QueueArguments(), cancellationToken: stoppingToken);
        await channel.QueueBindAsync(BrokerTopology.Queue, BrokerTopology.Exchange,
            routingKey: "", cancellationToken: stoppingToken);

        // Un mensaje por vez por réplica: el reparto entre réplicas queda parejo.
        await channel.BasicQosAsync(prefetchSize: 0, prefetchCount: 1, global: false,
            cancellationToken: stoppingToken);

        var consumer = new AsyncEventingBasicConsumer(channel);
        consumer.ReceivedAsync += (_, ea) => OnMessageAsync(channel, ea, stoppingToken);
        await channel.BasicConsumeAsync(BrokerTopology.Queue, false, consumer, stoppingToken);

        _logger.LogInformation("AUDITORIA consumidor iniciado. Exchange={Exchange} Cola={Queue}",
            BrokerTopology.Exchange, BrokerTopology.Queue);

        try { await Task.Delay(Timeout.Infinite, stoppingToken); }
        catch (OperationCanceledException) { }
    }

    private async Task OnMessageAsync(IChannel channel, BasicDeliverEventArgs ea, CancellationToken ct)
    {
        ReservationRequestedMessage? msg = null;
        try { msg = JsonSerializer.Deserialize<ReservationRequestedMessage>(Encoding.UTF8.GetString(ea.Body.Span)); }
        catch (JsonException) { }

        if (msg is null)
        {
            // Un mensaje ilegible no se arregla reintentando: va a la cola de mensajes fallidos.
            _logger.LogWarning("Mensaje ilegible, va a la cola de fallidos. DeliveryTag={Tag}", ea.DeliveryTag);
            await channel.BasicNackAsync(ea.DeliveryTag, multiple: false, requeue: false, ct);
            return;
        }

        _logger.LogInformation("AUDITORIA mensaje recibido. RequestId={RequestId}", msg.RequestId);
        try
        {
            using var scope = _scopes.CreateScope();
            var service = scope.ServiceProvider.GetRequiredService<ReservationService>();
            await service.ProcessRequestAsync(msg, ct);

            // Se confirma al broker SOLO después de procesar. Si algo falla, el mensaje vuelve a la
            // cola, y como ProcessRequestAsync es idempotente por RequestId no duplica la reserva.
            await channel.BasicAckAsync(ea.DeliveryTag, multiple: false, ct);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            _logger.LogError(ex, "Falló el procesamiento. RequestId={RequestId}. Vuelve a la cola.", msg.RequestId);
            await channel.BasicNackAsync(ea.DeliveryTag, multiple: false, requeue: true, ct);
        }
    }
}