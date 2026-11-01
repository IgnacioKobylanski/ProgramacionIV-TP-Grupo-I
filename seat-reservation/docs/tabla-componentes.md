# Tabla de interpretación del diagrama general

La siguiente tabla describe los componentes del sistema de reserva de asientos, su función y por qué participan en el procesamiento de una reserva. Corresponde al [diagrama general](diagrama-general.md).

| Componente | Rol | Justificación de su participación |
| --- | --- | --- |
| **Cliente HTTP** | Punto desde el cual se realizan las solicitudes a las APIs. | Permite consultar eventos y asientos, solicitar una reserva y consultar su resultado. También puede utilizar el endpoint de consulta de avisos de Notifications. |
| **Availability API** | Entrada al sistema para consultar disponibilidad y solicitar reservas. Utiliza Clean Architecture. | Comprueba la existencia del evento y del asiento, guarda las solicitudes y las publica en el broker. Consulta a Booking para obtener la ocupación y el resultado de una reserva. |
| **RabbitMQ** | Broker local en Docker para comunicar solicitudes de forma asíncrona. | Availability publica en el exchange `grupo1-booking` y las réplicas de Booking consumen la cola `booking`. Separa la recepción de la solicitud de su procesamiento y permite inspeccionar las colas en el entorno local. |
| **RabbitMQ — exchange `grupo1-booking`** | Enruta las solicitudes publicadas por Availability. | Es un exchange de tipo `fanout`, vinculado a la cola `booking`. Entrega los mensajes a esa cola para que Booking pueda procesarlos. |
| **RabbitMQ — cola `booking`** | Mantiene las solicitudes pendientes de procesamiento. | Las dos réplicas de Booking consumen esta misma cola. Cada entrega se asigna a un consumidor y se confirma después del procesamiento; un mensaje puede volver a entregarse. |
| **RabbitMQ — exchange `grupo1-booking.dlx`** | Enruta los mensajes derivados por el mecanismo de dead-letter. | Está configurado como destino dead-letter de `booking` y vinculado a `booking.dead`. Recibe los mensajes ilegibles que Booking rechaza sin reencolar. |
| **RabbitMQ — cola `booking.dead`** | Aparta mensajes fallidos para su inspección. | Recibe los mensajes derivados por `grupo1-booking.dlx`, evitando reintentar continuamente los que no pueden deserializarse. El proyecto no implementa un consumidor de esta cola. |
| **Booking API y workers** | Administra las reservas. Utiliza arquitectura N-Layer. | Consume solicitudes de la cola `booking`, controla si los asientos están ocupados, registra los estados de las reservas y gestiona sus vencimientos. Solicita el cobro a Payment e intenta notificar a Notifications cuando se confirma una reserva. |
| **Payment gRPC API** | Procesa cobros simulados. Utiliza arquitectura N-Layer. | Recibe las solicitudes de cobro de Booking mediante gRPC, evalúa el importe y guarda el resultado. Booking utiliza esa respuesta para confirmar o rechazar una reserva. |
| **Notifications API** | Registra los avisos de reservas confirmadas y simula su envío. | Recibe una solicitud HTTP de Booking cuando se confirma una reserva, guarda el aviso y registra el envío simulado en un log. Expone también una consulta HTTP autenticada de los avisos registrados. |
| **Keycloak** | Servidor de autenticación y autorización. | Proporciona tokens JWT para usuarios y servicios. Las APIs utilizan esos tokens y sus políticas de autorización para controlar el acceso a las operaciones protegidas. |
| **PostgreSQL — `availability`** | Almacena los datos de consulta y las solicitudes recibidas. | Guarda eventos (`Events`), asientos (`Seats`) y solicitudes (`ReservationRequests`). |
| **PostgreSQL — `booking`** | Almacena las reservas y sus estados. | Guarda las reservas (`Reservations`), los motivos de rechazo y los vencimientos. Sus restricciones de unicidad ayudan a evitar dos reservas activas para el mismo asiento de un evento. |
| **PostgreSQL — `payment`** | Almacena los resultados de los cobros. | Guarda los pagos simulados (`Payments`) asociados a las reservas. |
| **PostgreSQL — `notifications`** | Almacena los avisos de confirmación. | Guarda las notificaciones (`Notifications`) generadas para las reservas confirmadas. |

## Relación entre los componentes

El cliente se comunica con Availability por HTTP. Availability guarda la solicitud y la publica en el exchange `grupo1-booking` de RabbitMQ. El exchange la enruta a la cola `booking`, desde donde una de las réplicas de Booking la consume, administra la reserva y se conecta a Payment mediante gRPC para procesar el cobro simulado. Si la reserva se confirma, Booking intenta avisar a Notifications mediante HTTP para registrar el aviso. La autenticación de las APIs se basa en Keycloak; la conexión a RabbitMQ utiliza las credenciales del broker.

RabbitMQ se ejecuta localmente con Docker Compose, utiliza el puerto `5672` para mensajería y expone el panel de administración en `http://localhost:15672`. Los mensajes ilegibles se rechazan sin reencolar y se derivan mediante `grupo1-booking.dlx` a `booking.dead`; las excepciones de procesamiento provocan la devolución del mensaje a la cola principal. Notifications recibe llamadas HTTP de Booking y no consume mensajes de RabbitMQ.

La comunicación asíncrona **Availability → RabbitMQ → Booking** produce un período de **consistencia eventual**: la solicitud puede estar registrada antes de que exista un resultado de reserva en Booking.

Las cuatro bases pertenecen a un mismo servidor PostgreSQL; cada aplicación administra sus propios datos mediante Entity Framework Core.
