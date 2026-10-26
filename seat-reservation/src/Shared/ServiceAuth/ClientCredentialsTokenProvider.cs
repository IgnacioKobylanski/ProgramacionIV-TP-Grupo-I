using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace ServiceAuth;

public class ServiceAuthOptions
{
    public string TokenEndpoint { get; set; } = string.Empty;
    public string ClientId { get; set; } = string.Empty;
    public string ClientSecret { get; set; } = string.Empty;
}

// Obtiene el token de ESTE servicio (flujo "client credentials": el servicio se identifica
// ante Keycloak con su id y su secreto, sin ningún usuario de por medio).
// Lo guarda en memoria y lo reutiliza hasta 30 segundos antes de que venza, para no ir a
// Keycloak en cada llamada.
public class ClientCredentialsTokenProvider
{
    private readonly HttpClient _http;
    private readonly ServiceAuthOptions _options;
    private readonly SemaphoreSlim _lock = new(1, 1);
    private string? _token;
    private DateTime _expiresAtUtc = DateTime.MinValue;

    public ClientCredentialsTokenProvider(HttpClient http, ServiceAuthOptions options)
    {
        _http = http;
        _options = options;
    }

    private record TokenResponse(
        [property: JsonPropertyName("access_token")] string AccessToken,
        [property: JsonPropertyName("expires_in")] int ExpiresIn);

    public async Task<string> GetTokenAsync(CancellationToken ct)
    {
        if (_token is not null && DateTime.UtcNow < _expiresAtUtc) return _token;

        // El semáforo evita que varias llamadas simultáneas pidan el token a la vez.
        await _lock.WaitAsync(ct);
        try
        {
            if (_token is not null && DateTime.UtcNow < _expiresAtUtc) return _token;

            using var response = await _http.PostAsync(_options.TokenEndpoint,
                new FormUrlEncodedContent(new Dictionary<string, string>
                {
                    ["grant_type"] = "client_credentials",
                    ["client_id"] = _options.ClientId,
                    ["client_secret"] = _options.ClientSecret
                }), ct);
            response.EnsureSuccessStatusCode();

            var body = await response.Content.ReadFromJsonAsync<TokenResponse>(ct)
                       ?? throw new HttpRequestException("Keycloak devolvió una respuesta vacía");

            _token = body.AccessToken;
            _expiresAtUtc = DateTime.UtcNow.AddSeconds(body.ExpiresIn - 30);
            return _token;
        }
        finally
        {
            _lock.Release();
        }
    }
}