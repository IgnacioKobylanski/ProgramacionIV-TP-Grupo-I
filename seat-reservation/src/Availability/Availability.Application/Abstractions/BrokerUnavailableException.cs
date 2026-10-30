namespace Availability.Application.Abstractions;

// El broker no está disponible o rechazó el mensaje. La capa Api lo traduce a 503.
// Application no sabe qué broker hay por debajo: Infrastructure envuelve acá el error técnico.
public class BrokerUnavailableException : Exception
{
    public BrokerUnavailableException(string message, Exception inner) : base(message, inner) { }
}