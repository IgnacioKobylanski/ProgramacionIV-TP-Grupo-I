using Availability.Application.Abstractions;
using Availability.Infrastructure.Http;
using Availability.Infrastructure.Messaging;
using Availability.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;

namespace Availability.Infrastructure;

public class InfrastructureOptions
{
    public string Database { get; set; } = string.Empty;
    public string ServiceBusConnectionString { get; set; } = string.Empty;
    public string ServiceBusTopic { get; set; } = string.Empty;
    public string BookingBaseUrl { get; set; } = string.Empty;
}

public static class DependencyInjection
{
    // Cada capa expone cómo se registra; la capa Api solo "compone" sin conocer detalles.
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, InfrastructureOptions o)
    {
        services.AddDbContext<AvailabilityDbContext>(opt => opt.UseNpgsql(o.Database));
        services.AddScoped<IAvailabilityRepository, EfAvailabilityRepository>();

        // El cliente de Service Bus está pensado para vivir toda la aplicación: singleton.
        services.AddSingleton<IReservationPublisher>(_ =>
            new ServiceBusReservationPublisher(o.ServiceBusConnectionString, o.ServiceBusTopic));

        services.AddHttpClient<IBookingClient, HttpBookingClient>(c => c.BaseAddress = new Uri(o.BookingBaseUrl));
        return services;
    }
}