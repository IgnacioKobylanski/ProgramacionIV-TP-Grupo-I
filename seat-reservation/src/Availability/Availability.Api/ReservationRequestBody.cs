namespace Availability.Api;

// El usuario ya NO viaja en el cuerpo: sale del token validado.
// Si lo aceptáramos del cliente, cualquiera podría reservar a nombre de otro.
public record ReservationRequestBody(Guid EventId, Guid SeatId);