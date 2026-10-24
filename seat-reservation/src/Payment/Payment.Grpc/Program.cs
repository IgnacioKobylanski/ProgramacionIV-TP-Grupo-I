using Microsoft.EntityFrameworkCore;
using Payment.Business;
using Payment.DataAccess;
using Payment.Grpc.Services;

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

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    await scope.ServiceProvider.GetRequiredService<PaymentDbContext>().Database.MigrateAsync();
}

app.MapGrpcService<PaymentGrpcService>();
app.Run();