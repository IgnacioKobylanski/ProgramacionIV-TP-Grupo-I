using Availability.Application.Abstractions;
using Availability.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;

namespace Availability.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, string connectionString)
    {
        services.AddDbContext<AvailabilityDbContext>(o => o.UseNpgsql(connectionString));
        services.AddScoped<IAvailabilityRepository, EfAvailabilityRepository>();
        return services;
    }
}