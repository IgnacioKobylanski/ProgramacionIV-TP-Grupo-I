using Microsoft.EntityFrameworkCore;
using Payment.Business;
using Payment.DataAccess;
using Payment.Grpc.Services;
using ServiceAuth;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddGrpc();
builder.Services.AddDbContext<PaymentDbContext>(o =>
    o.UseNpgsql(builder.Configuration.GetConnectionString("Payment")));
builder.Services.AddScoped<IPaymentRepository, PaymentRepository>();
builder.Services.AddSingleton(new PaymentRules
{
    MaxAmount = builder.Configuration.GetValue<decimal>("Payment:MaxAmount", 100000m)
});
builder.Services.AddScoped<PaymentService>();

// AUTENTICACIÓN ENTRE SERVICIOS (punto e): Payment solo acepta llamadas de Booking.
builder.Services.AddKeycloakJwtBearer(builder.Configuration);
builder.Services.AddAuthorizationBuilder()
    .AddServicePolicy("BookingOnly", "booking-service");

var app = builder.Build();

// Aplica las migraciones al arrancar (esquema versionado en el repo).
using (var scope = app.Services.CreateScope())
{
    await scope.ServiceProvider.GetRequiredService<PaymentDbContext>().Database.MigrateAsync();
}

app.UseAuthentication();
app.UseAuthorization();

app.MapGrpcService<PaymentGrpcService>().RequireAuthorization("BookingOnly");
app.Run();