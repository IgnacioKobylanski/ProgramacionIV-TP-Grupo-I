using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace ServiceAuth;

public static class ServiceAuthExtensions
{
    // Para los servicios que LLAMAN a otros: registra el proveedor de token (uno solo por
    // proceso, para que el cache funcione) y el handler que lo agrega a las llamadas.
    public static IServiceCollection AddServiceAuth(this IServiceCollection services, ServiceAuthOptions options)
    {
        services.AddSingleton(_ => new ClientCredentialsTokenProvider(new HttpClient(), options));
        services.AddTransient<ServiceTokenHandler>();
        return services;
    }

    // Para los servicios que RECIBEN llamadas: validan los tokens que emite Keycloak
    // (firma, emisor y vigencia), igual que Availability.
    public static IServiceCollection AddKeycloakJwtBearer(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
            .AddJwtBearer(o =>
            {
                o.Authority = configuration["Auth:Authority"];
                o.RequireHttpsMetadata = configuration.GetValue<bool>("Auth:RequireHttpsMetadata");
                o.MapInboundClaims = false;
                // Simplificación documentada: se valida firma, emisor y vigencia; el control por audiencia queda como mejora.
                o.TokenValidationParameters.ValidateAudience = false;
            });
        return services;
    }

    // Política: solo acepta tokens del servicio indicado. En un token de servicio, el claim
    // "azp" (authorized party) es el client id de quien pidió el token.
    public static AuthorizationBuilder AddServicePolicy(this AuthorizationBuilder builder, string policyName, string allowedClientId) =>
        builder.AddPolicy(policyName, p => p.RequireAuthenticatedUser().RequireClaim("azp", allowedClientId));
}