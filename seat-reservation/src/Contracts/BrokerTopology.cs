namespace Contracts.Messages;

// Nombres y argumentos del broker, compartidos para que Availability (publica) y Booking
// (consume) declaren EXACTAMENTE la misma topología: RabbitMQ rechaza redeclarar una cola
// con argumentos distintos.
public static class BrokerTopology
{
    public const string Exchange = "grupo1-booking";
    public const string Queue = "booking";
    public const string DeadLetterExchange = "grupo1-booking.dlx";
    public const string DeadLetterQueue = "booking.dead";

    public static Dictionary<string, object?> QueueArguments() => new()
    {
        ["x-dead-letter-exchange"] = DeadLetterExchange
    };
}