# 🎟️ Sistema Seat Reservation
## 🧭 Índice de navegación

> Punto de entrada al proyecto: guía de inicio rápido, credenciales de desarrollo y mapa general de la documentación, infraestructura y código.

## ⚡ Cómo levantar el sistema (inicio rápido)

> Para arquitectura y pruebas completas, ver el [`README`](seat-reservation/README.md)

```bash
cd seat-reservation
docker compose up -d --build
docker compose ps
```

* **Acceso web:** http://localhost:3000
* **Login con Google (opcional):** Requiere configuración adicional con script. Detalle en [`README`](seat-reservation/README.md). 
---
## 🔑 Credenciales

**Credenciales de desarrollo local** (no hay datos reales; figuran en el `docker-compose.yml` y en el [`Readme`](seat-reservation/README.md)):

| Recurso | Usuario | Contraseña |
|---|---|---|
| Aplicación Web (Keycloak) (`http://localhost:3000`) | `usuario1` / `usuario2` | igual al nombre de usuario |
| Panel de Keycloak (`http://localhost:8081`) | `admin` | `admin` |
| Panel de RabbitMQ (`http://localhost:15672`) | `app` | `app` |
| PostgreSQL (`localhost:5432`) | `app` | `app` |

Los secretos de los clientes de servicio de Keycloak (`availability-service`, `booking-service`) son credenciales de desarrollo y figuran en el realm exportado ([`seat-reservation-realm.json`](seat-reservation/infra/keycloak/seat-reservation-realm.json)).

---
## 📚 Documentación

| Documento | Para qué sirve |
|---|---|
| [`Readme`](seat-reservation/README.md) | Guía principal: arquitectura, ejecución, flujos de prueba, decisiones de diseño, autenticación con Google, limitaciones, estructura del repositorio y equipo |
| [`Tabla de componentes`](seat-reservation/docs/tabla-componentes.md) | **Consigna 1** — tabla de interpretación del diagrama |
| [`Diagrama general.md`](seat-reservation/docs/diagrama-general.md) | Diagrama general; **marca la zona de consistencia eventual** (consigna 3.g) y el servicio de notificaciones (3.h) |
| [`Arquitectura de Availability`](seat-reservation/docs/arq-availability.md) | Arquitectura + diagrama por capas de Availability (consigna 3.i) |
| [`Arquitectura de Booking`](seat-reservation/docs/arq-booking.md) | Arquitectura de Booking: endpoints, autenticación y flujo de procesamiento |
| [`Arquitectura de Payment`](seat-reservation/docs/arq-payment.md) | Arquitectura de Payment: método gRPC `ChargeReservation` |
| [`Arquitectura de Notifications`](seat-reservation/docs/arq-notifications.md) | Arquitectura de Notifications: endpoints, idempotencia por `ReservationId` y decisión de usar HTTP directo desde Booking |
| [`Cambio de broker`](seat-reservation/docs/documentacion-cambio-broker.md) | Motivo y alcance del reemplazo de Azure Service Bus por RabbitMQ (exchange, colas y configuración en Docker) |
| [`Autenticación con Google y Keycloak`](seat-reservation/docs/autenticacion-google-keycloak.md) | Guía de la federación con Google (OIDC) a través de Keycloak, convivencia con los usuarios locales y diagnóstico de errores |
| [`Pruebas del backend`](seat-reservation/docs/backend-tests.md) | Plan y registro de pruebas del backend (27 casos, bloques A–F; ver estado más abajo) |
| [`Pruebas de RabbitMQ`](seat-reservation/docs/rabbitmq-tests.md) | RAB-01 (dos consumidores en la cola `booking`) y RAB-02 (mensaje inválido a `booking.dead`) |
| [`Pruebas del frontend`](seat-reservation/docs/frontend-tests.md) | Plan de 17 casos del frontend (bloques A–E), aún sin ejecutar |
| [`Referencia del plan`](seat-reservation/docs/referencia-del-plan.md) | Plan original del equipo (⚠️ desactualizado: Service Bus, Notifications como worker, puertos y colas) |
| [`Prompts`](seat-reservation/docs/prompts/) | **Consigna 2** — historial de prompts por integrante (ver tabla del equipo) |
| [`README del frontend`](seat-reservation/frontend/README.md) | Texto de la plantilla de Vite (no describe la aplicación; ver la sección de frontend del `Readme` principal) |

---
## 🛠️ Infraestructura y scripts

| Recurso | Descripción |
|---|---|
| [`docker-compose.yml`](seat-reservation/docker-compose.yml) · [`Dockerfile`](seat-reservation/Dockerfile) | Todo el sistema en contenedores: PostgreSQL 16, RabbitMQ 4 (con panel), Keycloak 26, los cuatro servicios (Booking con 2 réplicas) y el frontend. Un Dockerfile parametrizado (`PROJECT`, `DLL`) sirve a los 4 servicios .NET |
| [`frontend/Dockerfile`](seat-reservation/frontend/Dockerfile) · [`frontend/nginx.conf`](seat-reservation/frontend/nginx.conf) | Build de Vite (Node 22) servido con nginx en el puerto 3000, con *fallback* a `index.html` para las rutas de React |
| [`infra/postgres/init.sql`](seat-reservation/infra/postgres/init.sql) | Crea las cuatro bases: `availability`, `booking`, `payment` y `notifications` |
| [`infra/keycloak/seat-reservation-realm.json`](seat-reservation/infra/keycloak/seat-reservation-realm.json) | Realm exportado: clientes `seat-web` (frontend), `availability-service` y `booking-service` (client credentials) y usuarios de prueba (`usuario1`, `usuario2`). No incluye el proveedor Google |
| [`scripts/funciones-prueba.ps1`](seat-reservation/scripts/funciones-prueba.ps1) | Funciones PowerShell para probar el flujo: `Eventos`, `Seat`, `Asientos`, `Token`, `Resultado` y `ReservarAutenticado` (usa los 3 eventos de demostración) |
| [`scripts/configurar-google.ps1`](seat-reservation/scripts/configurar-google.ps1) | Registra Google como proveedor de identidad en el realm; pide *Client ID* y *Client Secret* por consola sin guardarlos |
| [`scripts/configurar-secretos.ps1`](seat-reservation/scripts/configurar-secretos.ps1) | Solo para el modo `dotnet run`: guarda en *user-secrets* (fuera del repo) el secreto de cliente de Keycloak de Availability y Booking y elimina cualquier connection string de Service Bus. No hace falta con Docker |
| [`scripts/levantar-servicios.ps1`](seat-reservation/scripts/levantar-servicios.ps1) | Ejecución alternativa con `dotnet run` (una ventana por servicio: Payment, Notifications, Booking y Availability). Requiere `postgres`, `keycloak` y `rabbitmq` en Docker |
| [`scripts/tests_back_bloque_A.py`](seat-reservation/scripts/tests_back_bloque_A.py) | Pruebas de caja negra del bloque A del backend (Python, solo librería estándar): `python tests_back_bloque_A.py [--base-url URL] [--only 3,5]` |

---
## 💻 Código

| Componente | Descripción |
|---|---|
| [`Availability (Clean Architecture)`](seat-reservation/src/Availability/) | `Api`, `Application`, `Domain` e `Infrastructure`. Eventos y asientos, solicitud de reserva y publicación en RabbitMQ. Carga 3 eventos de demostración (Recital: 20 asientos; TecWeek 2026: 24; Teatro: 24). Endpoints: `GET /events`, `GET /events/{id}/seats`, `POST /reservations`, `GET /reservations/{requestId}`, `GET /reservations/mine` |
| [`Booking (N-Layer)`](seat-reservation/src/Booking/) | `Api`, `Business`, `DataAccess` y `Entities`. Consumidor de la cola `booking`, vencimiento de reservas (worker), cliente gRPC de Payment y cliente HTTP de Notifications. Endpoints (solo `availability-service`): `GET /reservations/{requestId}`, `GET /events/{id}/occupied-seats`, `GET /reservations?userId=` |
| [`Payment (N-Layer, gRPC)`](seat-reservation/src/Payment/) | `Grpc`, `Business`, `DataAccess` y `Entities`. Método `ChargeReservation`, cobro simulado e idempotente. Solo acepta a `booking-service` |
| [`Notifications (API mínima)`](seat-reservation/src/Notifications/) | `POST /notifications` (solo `booking-service`, idempotente por `ReservationId`) y `GET /notifications` (últimas 50, cualquier token válido) |
| [`Contratos compartidos (mensajes + .proto)`](seat-reservation/src/Contracts/) | Mensajes del broker, topología de RabbitMQ (`BrokerTopology`) y contrato gRPC [`payment.proto`](seat-reservation/src/Contracts/Protos/payment.proto) |
| [`Autenticación entre servicios (librería compartida)`](seat-reservation/src/Shared/ServiceAuth/) | Token por *client credentials*, manejador de tokens salientes y validación JWT con políticas por servicio |
| [`Frontend`](seat-reservation/frontend/src/) | React 19 + TypeScript + Vite con `keycloak-js` (PKCE). Rutas: `/` (eventos), `/events/:eventId` (asientos), `/reservations/:requestId` (resultado con *polling*) y `/mis-reservas` |
| [`Solución .NET`](seat-reservation/SeatReservation.sln) | Agrupa los 15 proyectos de `src/` |

