# Cambio de broker: Azure Service Bus a RabbitMQ

## Descripción

Durante el desarrollo del sistema de reserva de asientos se reemplazó Azure Service Bus por **RabbitMQ** como broker de mensajería entre los microservicios **Availability** y **Booking**.

El cambio permite ejecutar el broker localmente mediante Docker, sin depender de una cuenta de Azure ni de una cadena de conexión de Azure Service Bus.

## Contexto del cambio

Durante las pruebas de integración del 29/10/2026, el equipo observó que algunas solicitudes de reserva permanecían en estado `EnProceso`, cuando en pruebas anteriores habían llegado a `Confirmada`.

El equipo contaba con una cadena de conexión a Azure Service Bus, pero no con acceso administrativo para inspeccionar los mensajes activos ni los enviados a *dead-letter*. Esto dificultaba determinar si el inconveniente estaba en la aplicación o en el servicio de mensajería.

Se adoptó RabbitMQ ejecutado localmente mediante Docker, lo que facilita la inspección de colas, mensajes y consumidores durante el desarrollo y las pruebas. **No se determinó que Azure Service Bus fuera necesariamente la causa de los fallos observados.**

## Funcionamiento actual

1. **Availability** recibe una solicitud de reserva y publica un mensaje en RabbitMQ.
2. El mensaje se envía al exchange `grupo1-booking` y se entrega a la cola `booking`.
3. Las dos réplicas de **Booking** consumen la misma cola; cada mensaje se entrega a un consumidor para su procesamiento.
4. Booking procesa la reserva y se comunica con **Payment** mediante gRPC para realizar el cobro simulado.
5. Cuando la reserva queda confirmada, Booking se comunica con **Notifications** mediante HTTP para registrar el aviso simulado.

Availability responde **HTTP 202** al aceptar la solicitud para su procesamiento, sin esperar la decisión final de Booking. Durante ese intervalo, la solicitud puede permanecer en estado `EnProceso`, como parte del modelo de consistencia eventual.

## Configuración en Docker

RabbitMQ se ejecuta como servicio del entorno Docker Compose. El panel de administración está disponible en `http://localhost:15672`, con las credenciales de desarrollo definidas para el proyecto.

La configuración de mensajería utiliza:

|Elemento|Valor|Función|
|-|-|-|
|Exchange|`grupo1-booking`|Recibe los mensajes publicados por Availability|
|Cola principal|`booking`|Entrega las solicitudes a las réplicas de Booking|
|Cola de dead-letter|`booking.dead`|Recibe mensajes derivados por el mecanismo de dead-letter|

Para levantar el entorno desde la raíz del repositorio:

```powershell
docker compose up -d --build
```

Para revisar las colas:

```powershell
docker compose exec rabbitmq rabbitmqctl list\_queues name messages consumers
```

## Alcance del cambio

* **Availability y Booking:** utilizan RabbitMQ para el intercambio asíncrono de solicitudes de reserva.
* **Payment:** mantiene su comunicación gRPC con Booking.
* **Notifications:** mantiene la comunicación HTTP directa desde Booking; no consume mensajes de RabbitMQ ni requiere una cola propia.
* **Keycloak:** continúa a cargo de la autenticación y emisión de tokens; su función no cambia por el reemplazo del broker.

Este cambio corresponde al mecanismo de mensajería entre servicios y **no modifica el flujo funcional de confirmación de reservas**.

## Consideraciones

* Cada integrante puede ejecutar su propio broker RabbitMQ local con Docker.
* Si RabbitMQ no está disponible, Availability puede responder con un error al intentar publicar una solicitud.
* La cola `booking.dead` está configurada para mensajes derivados mediante dead-letter.
* Las credenciales del entorno local son de desarrollo y no deben reutilizarse en producción.

