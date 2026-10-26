using System.Net.Http.Headers;

namespace ServiceAuth;

// Se engancha a un cliente HTTP (o gRPC) y agrega el token de este servicio a cada pedido
// saliente. Así el código de negocio no sabe nada de tokens.
public class ServiceTokenHandler : DelegatingHandler
{
    private readonly ClientCredentialsTokenProvider _tokens;

    public ServiceTokenHandler(ClientCredentialsTokenProvider tokens) => _tokens = tokens;

    protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
    {
        var token = await _tokens.GetTokenAsync(ct);
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        return await base.SendAsync(request, ct);
    }
}