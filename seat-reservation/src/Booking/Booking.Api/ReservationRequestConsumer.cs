using System.Text.Json;
using Azure.Messaging.ServiceBus;
using Booking.Business;
using Contracts.Messages;

namespace Booking.Api;

// Flecha SUBSCRIBE del diagrama oficial. Todas las réplicas de Booking leen de la MISMA
// suscripción, y Service Bus entrega cada mensaje a una sola de ellas (consumidores competidores).
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
        await using var client = new ServiceBusClient(_config["ServiceBus:ConnectionString"]);
        await using var processor = client.CreateProcessor(
            _config["ServiceBus:TopicName"],
            _config["ServiceBus:SubscriptionName"],
            new ServiceBusProcessorOptions { MaxConcurrentCalls = 4, AutoCompleteMessages = false });

        processor.ProcessMessageAsync += OnMessageAsync;
        processor.ProcessErrorAsync += OnErrorAsync;

        await processor.StartProcessingAsync(stoppingToken);
        try { await Task.Delay(Timeout.Infinite, stoppingToken); }
        catch (OperationCanceledException) { }
        await processor.StopProcessingAsync(CancellationToken.None);
    }

    private async Task OnMessageAsync(ProcessMessageEventArgs args)
    {
        ReservationRequestedMessage? msg;
        try { msg = JsonSerializer.Deserialize<ReservationRequestedMessage>(args.Message.Body.ToString()); }
        catch (JsonException) { msg = null; }
        if (msg is null)
        {
            // Un mensaje ilegible no se arregla reintentando: va a la cola de mensajes fallidos.
            await args.DeadLetterMessageAsync(args.Message, "MensajeInvalido",
                "No se pudo deserializar", cancellationToken: args.CancellationToken);
            return;
        }

        using var scope = _scopes.CreateScope();
        var service = scope.ServiceProvider.GetRequiredService<ReservationService>();
        await service.ProcessRequestAsync(msg, args.CancellationToken);

        // Se confirma al broker SOLO después de procesar. Si algo lanza una excepción, el
        // mensaje vuelve a entregarse, y como ProcessRequestAsync es idempotente por RequestId
        // no hay riesgo de duplicar la reserva (entrega "al menos una vez").
        await args.CompleteMessageAsync(args.Message, args.CancellationToken);
    }

    private Task OnErrorAsync(ProcessErrorEventArgs args)
    {
        _logger.LogError(args.Exception, "Error del broker. Origen={Source} Entidad={Entity}",
            args.ErrorSource, args.EntityPath);
        return Task.CompletedTask;
    }
}