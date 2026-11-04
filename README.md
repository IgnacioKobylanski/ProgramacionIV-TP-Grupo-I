# 🎟️ Sistema Seat Reservation
## 🧭 Índice de navegación

> Punto de entrada al proyecto: guía de inicio rápido, credenciales de desarrollo y mapa general de la documentación, infraestructura y código.

## ⚡ Cómo levantar el sistema (inicio rápido)

> Para arquitectura, detalle de endpoints y pruebas completas, ver el [`README principal`](seat-reservation/README.md) y el [`README del frontend`](seat-reservation/frontend/README.md).

```bash
cd seat-reservation
docker compose up -d --build
docker compose ps
```

* **Acceso web (Docker / Nginx):** http://localhost:3000
* **Acceso web en desarrollo (Vite opcional):** http://localhost:5173 (ejecutando `npm ci && npm run dev` desde `seat-reservation/frontend`)
* **API pública de entrada (Availability):** http://localhost:5001/events
* **Login con Google (opcional):** Requiere configuración adicional con script. Detalle en el [`README principal`](seat-reservation/README.md) y en la [`Guía de Google y Keycloak`](seat-reservation/docs/autenticacion-google-keycloak.md).
* **Login con GitHub (opcional, respaldo de Google):** Se agregó **como medida de prevención**, por si Google no levanta la suspensión de la cuenta con la que se creó el cliente OAuth. No reemplaza a Google: son dos proveedores alternativos y ambos son opcionales. Se activa con un script. Detalle en la [`Guía de GitHub y Keycloak`](seat-reservation/docs/autenticacion-github-keycloak.md).

---
## 🔑 Credenciales

**Credenciales de desarrollo local** (no hay datos reales; figuran en el `docker-compose.yml` y en el [`README principal`](seat-reservation/README.md)):

| Recurso | Usuario | Contraseña |
|---|---|---|
| Aplicación Web (Keycloak) (`http://localhost:3000` o `5173`) | `usuario1` / `usuario2` | igual al nombre de usuario |
| Panel de Keycloak (`http://localhost:8081`) | `admin` | `admin` |
| Panel de RabbitMQ (`http://localhost:15672` · AMQP `5672`) | `app` | `app` |
| PostgreSQL (`localhost:5432`) | `app` | `app` |

Los secretos de los clientes de servicio de Keycloak (`availability-service` y `booking-service`) son credenciales de desarrollo y figuran tanto en el `docker-compose.yml` como en el realm exportado ([`seat-reservation-realm.json`](seat-reservation/infra/keycloak/seat-reservation-realm.json)).

---
## 📚 Documentación

| Documento | Para qué sirve |
|---|---|
| [`README principal (Backend y Sistema)`](seat-reservation/README.md) | Guía principal: arquitectura, ejecución, endpoints, variables de entorno, flujos de prueba, decisiones de diseño, autenticación con Google, limitaciones y estructura |
| [`README del Frontend`](seat-reservation/frontend/README.md) | Guía completa de la interfaz web **SeatReserve** (React 19 + TypeScript + Vite): ejecución con Docker o Vite, configuración `VITE_*`, CORS, pantallas, polling y componentes |
| [`Documentación del Frontend`](seat-reservation/docs/documentacion-frontend.md) | Documento técnico complementario sobre el diseño e integración del frontend |
| [`Tabla de componentes`](seat-reservation/docs/tabla-componentes.md) | **Consigna 1** — tabla de interpretación del diagrama |
| [`Diagrama general`](seat-reservation/docs/diagrama-general.md) | Diagrama general; **marca la zona de consistencia eventual** (consigna 3.g) y el servicio de notificaciones (consigna 3.h) |
| [`Arquitectura de Availability`](seat-reservation/docs/arq-availability.md) | Arquitectura + diagrama por capas de Availability (consigna 3.i) |
| [`Arquitectura de Booking`](seat-reservation/docs/arq-booking.md) | Arquitectura de Booking: endpoints, consumidores, vencimiento, autenticación y flujo de procesamiento |
| [`Arquitectura de Payment`](seat-reservation/docs/arq-payment.md) | Arquitectura de Payment: método gRPC `ChargeReservation` e idempotencia |
| [`Arquitectura de Notifications`](seat-reservation/docs/arq-notifications.md) | Arquitectura de Notifications: endpoints, idempotencia por `ReservationId` y decisión de usar HTTP directo desde Booking |
| [`Cambio de broker`](seat-reservation/docs/documentacion-cambio-broker.md) | Motivo y alcance del reemplazo de Azure Service Bus por RabbitMQ (exchanges, colas y configuración en Docker) |
| [`Autenticación con Google y Keycloak`](seat-reservation/docs/autenticacion-google-keycloak.md) | Guía de la federación con Google (OIDC) a través de Keycloak, convivencia con los usuarios locales y diagnóstico de errores |
| [`Autenticación con GitHub y Keycloak`](seat-reservation/docs/autenticacion-github-keycloak.md) | Guía para agregar GitHub como proveedor de identidad externo de respaldo (por la suspensión de la cuenta de Google): creación de la OAuth App, uso del script, pruebas y diagnóstico de errores |
| [`Pruebas del backend`](seat-reservation/docs/testing/backend-tests.md) | Plan y registro de pruebas del backend (27 casos, bloques A–F) |
| [`Pruebas de RabbitMQ`](seat-reservation/docs/testing/rabbitmq-tests.md) | RAB-01 (dos consumidores competidores en la cola `booking`) y RAB-02 (mensaje inválido derivado a `booking.dead`) |
| [`Pruebas del frontend`](seat-reservation/docs/testing/frontend-tests.md) | Plan y registro de los 17 casos de prueba del frontend (bloques A–E) |
| [`Referencia del plan`](seat-reservation/docs/referencia-del-plan.md) | Plan original del equipo (fue actualizado) |
| [`Prompts`](seat-reservation/docs/prompts/) | **Consigna 2** — historial de prompts utilizados por cada integrante del equipo |

---
## 🛠️ Infraestructura y scripts

| Recurso | Descripción |
|---|---|
| [`docker-compose.yml`](seat-reservation/docker-compose.yml) · [`Dockerfile`](seat-reservation/Dockerfile) | Todo el sistema en contenedores: PostgreSQL 16, RabbitMQ 4 (con panel management), Keycloak 26, los cuatro microservicios (Booking con 2 réplicas) y el frontend. Un único `Dockerfile` parametrizado (`PROJECT`, `DLL`) compila y sirve los 4 servicios .NET 10 |
| [`frontend/Dockerfile`](seat-reservation/frontend/Dockerfile) · [`frontend/nginx.conf`](seat-reservation/frontend/nginx.conf) | Build de Vite (Node 22) servido con Nginx en el puerto `3000` (interno `80`), con *fallback* a `index.html` para soportar las rutas de React Router |
| [`infra/postgres/init.sql`](seat-reservation/infra/postgres/init.sql) | Script de inicialización que crea las cuatro bases de datos independientes: `availability`, `booking`, `payment` y `notifications` |
| [`infra/keycloak/seat-reservation-realm.json`](seat-reservation/infra/keycloak/seat-reservation-realm.json) | Realm exportado `seat-reservation`: cliente público `seat-web` (frontend), clientes confidenciales `availability-service` y `booking-service` (*client credentials*) y usuarios de prueba (`usuario1`, `usuario2`). No incluye secretos de Google ni de GitHub |
| [`scripts/funciones-prueba.ps1`](seat-reservation/scripts/funciones-prueba.ps1) | Funciones PowerShell para probar el flujo por consola: `Eventos`, `Seat`, `Asientos`, `Token`, `Resultado` y `ReservarAutenticado` (opera con los 3 eventos de demostración) |
| [`scripts/configurar-google.ps1`](seat-reservation/scripts/configurar-google.ps1) | Registra Google como proveedor de identidad OIDC en el realm de Keycloak pidiendo *Client ID* y *Client Secret* por consola sin guardarlos en el repositorio |
| [`scripts/configurar-github.ps1`](seat-reservation/scripts/configurar-github.ps1) | Registra GitHub como proveedor de identidad en el realm de Keycloak, como respaldo de Google. Pide *Client ID* y *Client Secret* por consola sin guardarlos en el repositorio |
| [`scripts/configurar-secretos.ps1`](seat-reservation/scripts/configurar-secretos.ps1) | Solo para ejecución local con `dotnet run`: guarda en *user-secrets* (fuera del repo) el secreto de cliente de Keycloak de Availability y Booking. No es necesario con Docker |
| [`scripts/levantar-servicios.ps1`](seat-reservation/scripts/levantar-servicios.ps1) | Ejecución alternativa del backend con `dotnet run` (abre una ventana por servicio: Payment, Notifications, Booking y Availability). Requiere `postgres`, `keycloak` y `rabbitmq` activos en Docker |
| [`scripts/tests_back_bloque_A.py`](seat-reservation/scripts/tests_back_bloque_A.py) | Script automatizado para pruebas de caja negra del bloque A del backend (Python, solo librería estándar): `python tests_back_bloque_A.py [--base-url URL] [--only 3,5]` |

---
## 💻 Código

| Componente | Descripción |
|---|---|
| [`Availability (Clean Architecture)`](seat-reservation/src/Availability/) | Proyectos `Api`, `Application`, `Domain` e `Infrastructure`. Consulta de eventos y asientos, solicitud de reserva y publicación en RabbitMQ. Siembra automáticamente 3 eventos de demostración (`Recital Mercedes Sosa`: 20 asientos; `TecWeek 2026`: 24; `Teatro: Esperando a Godot`: 24). Endpoints: `GET /events`, `GET /events/{eventId}/seats`, `POST /reservations`, `GET /reservations/{requestId}`, `GET /reservations/mine` |
| [`Booking (N-Layer)`](seat-reservation/src/Booking/) | Proyectos `Api`, `Business`, `DataAccess` y `Entities`. Consumidor de la cola `booking` (`ReservationRequestConsumer`), worker de vencimiento de reservas cada 10 s (`ReservationExpiryWorker`), cliente gRPC de Payment y cliente HTTP de Notifications. Endpoints internos (solo `availability-service`): `GET /reservations/{requestId}`, `GET /events/{eventId}/occupied-seats`, `GET /reservations?userId=` |
| [`Payment (N-Layer, gRPC)`](seat-reservation/src/Payment/) | Proyectos `Grpc`, `Business`, `DataAccess` y `Entities`. Expone el método gRPC `ChargeReservation`: cobro simulado (aprueba montos `> 0` y `<= MaxAmount`) e idempotente por `ReservationId`. Solo acepta tokens de `booking-service` |
| [`Notifications (API mínima)`](seat-reservation/src/Notifications/) | Proyecto `Notifications`. Endpoints: `POST /notifications` (solo `booking-service`, idempotente por `ReservationId`) y `GET /notifications` (devuelve las últimas 50 notificaciones; requiere cualquier token válido) |
| [`Contratos compartidos (mensajes + .proto)`](seat-reservation/src/Contracts/) | Mensajes compartidos (`ReservationRequestedMessage`, `ReservationConfirmedNotification`), topología de RabbitMQ (`BrokerTopology`: exchanges `grupo1-booking` y `grupo1-booking.dlx`, colas `booking` y `booking.dead`) y contrato gRPC [`payment.proto`](seat-reservation/src/Contracts/Protos/payment.proto) |
| [`Autenticación entre servicios`](seat-reservation/src/Shared/ServiceAuth/) | Librería `ServiceAuth`: proveedor de tokens con caché en memoria por *client credentials* (`ClientCredentialsTokenProvider`), delegating handler (`ServiceTokenHandler`) y validación JWT con políticas por claim `azp` |
| [`Frontend (SeatReserve)`](seat-reservation/frontend/src/) | React 19 + TypeScript + Vite con `keycloak-js` (PKCE `S256`) y React Router 7. Rutas: `/` (eventos), `/events/:eventId` (grilla de asientos), `/reservations/:requestId` (seguimiento con *polling* cada 1 s hasta 30 s) y `/mis-reservas` (historial y filtro por estado) |
| [`Solución .NET`](seat-reservation/SeatReservation.sln) | Solución de Visual Studio que agrupa los 15 proyectos `.csproj` dentro de `src/` |