# Tabla de interpretación del diagrama general

La siguiente tabla describe los componentes del sistema de reserva de asientos, su función y por qué participan en el procesamiento de una reserva. Corresponde al [diagrama general](diagrama-general.md).

| Componente | Rol | Justificación de su participación |
| --- | --- | --- |
| **Cliente HTTP** | Punto desde el cual se realizan las solicitudes a las APIs. | Permite consultar eventos y asientos, solicitar una reserva y consultar su resultado. También puede utilizar el endpoint de consulta de avisos de Notifications. |
| **Availability API** | Entrada al sistema para consultar disponibilidad y solicitar reservas. Utiliza Clean Architecture. | Comprueba la existencia del evento y del asiento, guarda las solicitudes y las publica en el broker. Consulta a Booking para obtener la ocupación y el resultado de una reserva. |
| **Azure Service Bus** | Intermediario para comunicar solicitudes de forma asíncrona. | Availability publica cada solicitud en el topic `grupo1-booking-topic` y Booking la recibe desde la suscripción `booking`. Así, la recepción del pedido y su procesamiento se realizan por separado. |
| **Booking API y workers** | Administra las reservas. Utiliza arquitectura N-Layer. | Procesa las solicitudes recibidas, controla si los asientos están ocupados, registra los estados de las reservas y gestiona sus vencimientos. Solicita el cobro a Payment e intenta notificar a Notifications cuando se confirma una reserva. |
| **Payment gRPC API** | Procesa cobros simulados. Utiliza arquitectura N-Layer. | Recibe las solicitudes de cobro de Booking mediante gRPC, evalúa el importe y guarda el resultado. Booking utiliza esa respuesta para confirmar o rechazar una reserva. |
| **Notifications API** | Registra los avisos de reservas confirmadas y simula su envío. | Recibe una solicitud HTTP de Booking cuando se confirma una reserva, guarda el aviso y registra el envío simulado en un log. Expone también una consulta HTTP autenticada de los avisos registrados. |
| **Keycloak** | Servidor de autenticación y autorización. | Proporciona tokens JWT para usuarios y servicios. Las APIs utilizan esos tokens y sus políticas de autorización para controlar el acceso a las operaciones protegidas. |
| **PostgreSQL — `availability`** | Almacena los datos de consulta y las solicitudes recibidas. | Guarda eventos (`Events`), asientos (`Seats`) y solicitudes (`ReservationRequests`). |
| **PostgreSQL — `booking`** | Almacena las reservas y sus estados. | Guarda las reservas (`Reservations`), los motivos de rechazo y los vencimientos. Sus restricciones de unicidad ayudan a evitar dos reservas activas para el mismo asiento de un evento. |
| **PostgreSQL — `payment`** | Almacena los resultados de los cobros. | Guarda los pagos simulados (`Payments`) asociados a las reservas. |
| **PostgreSQL — `notifications`** | Almacena los avisos de confirmación. | Guarda las notificaciones (`Notifications`) generadas para las reservas confirmadas. |

## Relación entre los componentes

El cliente se comunica con Availability por HTTP. Availability guarda la solicitud y la publica en Azure Service Bus. Booking consume ese mensaje, administra la reserva y se conecta a Payment mediante gRPC para procesar el cobro simulado. Si la reserva se confirma, Booking intenta avisar a Notifications mediante HTTP para registrar el aviso. La autenticación se basa en Keycloak.

La comunicación asíncrona entre Availability y Booking produce un período de **consistencia eventual**: la solicitud puede estar registrada antes de que exista un resultado de reserva en Booking.

Las cuatro bases pertenecen a un mismo servidor PostgreSQL; cada aplicación administra sus propios datos mediante Entity Framework Core.
