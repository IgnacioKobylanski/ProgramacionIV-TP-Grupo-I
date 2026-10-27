# Historial de prompts: Ignacio Kobylanski

Herramienta: Claude (Anthropic). Componentes trabajados: estructura de la solución,
infraestructura local (Docker) y Availability (Clean Architecture).

## 1. Decisiones de arquitectura
- Prompts: planteé cómo organizar el TP antes de crear el repo y, más adelante, consulté si era válido usar Keycloak como servidor de autorización.
- Qué se usó: monorepo, PostgreSQL con una base por servicio, Keycloak, dos colas en Service Bus, orden de trabajo.
- Mi aporte: revisé las alternativas, adopté el stack y validé la elección de Keycloak antes de usarlo.

## 2. Estructura de la solución
- Prompt: pedí asistencia con el código base.
- Qué se usó: comandos `dotnet new` y referencias entre proyectos que reflejan Clean y N-Layer.
- Mi aporte: ejecuté todo, corregí detalles, elegí .NET 10 (el que uso en mis otros proyectos) y verifiqué que compilara.

## 3. Infraestructura local
- Prompt: pedí Postgres y Keycloak en Docker.
- Qué se usó: `docker-compose.yml` y script de inicialización.
- Mi aporte: levanté los contenedores, verifiqué las 4 bases y cuestioné las credenciales fijas del compose antes de subirlo.

## 4. Availability (Clean Architecture)
- Prompt: pedí el código de contratos, dominio anémico, aplicación, infraestructura y endpoints, a partir de un diagrama de clases base.
- Qué se usó: entidades, servicio, repositorio con EF Core y endpoints de consulta.
- Mi aporte: detecté que `EnsureCreated` no era buena práctica y pedí migraciones; corregí un error de compilación; verifiqué los paquetes instalados; probé los endpoints en el navegador, corregí detalles menores.

## 5. Gestión del repositorio
- Prompts: consultas sobre repo público o privado, idioma de los commits y revisión del `.gitignore` y del `docker-compose.yml`.
- Mi aporte: decidí mantener el repo privado hasta la entrega, excluir los secretos con `.gitignore` y escribir los commits en español para que el grupo los entienda.

## 6. Payment (gRPC, N-Layer)
- Prompts: consulte que paso es el mas optimo sin tener el string de conexion para poder avanzar.
- Qué se usó: contrato gRPC compartido en Contracts, entidades anémicas, repositorio idempotente, servicio de cobro simulado y servicio gRPC con logs de auditoría.
- Mi aporte: decidí avanzar con Payment sin esperar el broker, corregí el conflicto de versiones de Google.Protobuf, levanté la infraestructura en Docker y verifiqué que el servicio arrancara y respondiera.

## 7. Booking (N-Layer)
- Prompts: pedí implementar Booking con retención de asientos, concurrencia, cobro por gRPC a Payment y vencimiento. Después consulté tres decisiones de diseño: si los enums en español eran correctos, si no usar un lock distribuido era la mejor opción, y si la consigna exigía tratar reembolsos(no lo hacia segun mi interpretacion).
- Qué se usó: entidad de reserva con estados y motivos de rechazo, índice único parcial, repositorio con control de concurrencia optimista, servicio de reservas idempotente, cliente gRPC con deadline, servicio de vencimiento y endpoint de consulta de estado.
- Mi aporte: cuestioné las decisiones de diseño antes de adoptarlas; resolví el error del build (proceso bloqueando el ejecutable); ejecuté las pruebas de camino feliz, asiento ocupado, pago no disponible, asiento liberado, concurrencia (5 pedidos simultáneos, 1 confirmado) y vencimiento, y verifiqué los estados en la base.

## 8. Conexión con Azure Service Bus (Availability y Booking)
- Prompts: compartí el ejemplo del profesor (sin la clave) y pedí conectar Availability y Booking al topic del grupo. Consulté cómo guardar el connection string sin subirlo al repo y si el publicador como singleton era una mala práctica.
- Qué se usó: puertos `IReservationPublisher` e `IBookingClient`, publicador y consumidor de Service Bus, endpoint `POST /reservations` con respuesta 202 y endpoint de consulta del resultado.
- Mi aporte: guardé el string con user-secrets, configuré el topic y la suscripción según el ejemplo del profesor, apliqué el ajuste para mensajes con formato inválido, revisé el consumidor y probé el flujo completo (POST con respuesta inmediata y consulta con resultado `Confirmada`).

## 9. Agregar mas comentarios de diseño
- Prompt: Olvide agregar o pedir que se agreguen comentarios en codigo, pedi que se agregaran mas para respetar la consigna y de modo que sirvan de base para la documentación del grupo.
- Qué se usó: los comentarios que justifican las decisiones: puertos y adaptadores en Availability, índice único parcial y control de concurrencia optimista en Booking, idempotencia por RequestId, deadline en la llamada gRPC, singleton del cliente de Service Bus y consistencia eventual en la consulta de estado.
- Mi aporte:  agregue los comentarios en cada archivo y verifiqué que el proyecto siguiera compilando.

## 10. Notifications (punto h)
- Prompts: pedí asistencia para avanzar con Notifications, consulte si el diseño que sugeri era optimo para el caso.
- Qué se usó: API mínima con su propia base, contrato `ReservationConfirmedNotification`, puerto y adaptador HTTP en Booking, aviso solo cuando la reserva queda confirmada y tolerante a fallas.
- Mi aporte: apliqué los cambios en Booking y Notifications, resolví un error de compilación, generé la migración y verifiqué que todo compilara.

## 11. Asientos libres en Availability
- Prompts: pedí que Availability muestre solo los asientos disponibles (para que cumpliera el punto 1 del flujo, el cual habia quedado desincronizado).
- Qué se usó: endpoint de asientos ocupados en Booking y su consumo desde Availability con el `GET` del diagrama oficial; el listado va ordenado y responde 503 si Booking no está disponible.
- Mi aporte: apliqué los cambios en los dos servicios y verifiqué que compilaran.

## 12. Keycloak configuracion inicial
- Prompts: pedí asistencia para configurar desde el panel de administrador
- Qué se usó: Panel de administracion de Keycloak
- Mi aporte: Cree los usuarios iniciales y realice los cambios necesarios en el codigo testeando minimamente su correcto funcionamiento.

## 13. Autenticación entre servicios (punto e)
- Prompts: pedí seguir con la autenticación entre servicios;.
- Qué se usó: dos clients de servicio en Keycloak, un proyecto compartido que pide y reutiliza el token de servicio, y políticas que aceptan solo al servicio que corresponde (Booking acepta a Availability; Payment y Notifications aceptan a Booking).
- Mi aporte: creé los clients, corregí el Client ID mal cargado, guardé los secretos con user-secrets, apliqué el código y verifiqué el flujo completo y los rechazos (sin token da 401 y con un token de otro servicio o usuario da 403).

## 14. Exportación del realm
- Prompts: pedí que la configuración de Keycloak quede en el repositorio y se cargue sola al levantar Docker.
- Qué se usó: exportación del realm a `infra/keycloak/seat-reservation-realm.json` y el montaje del archivo para importarlo al iniciar.
- Mi aporte: exporté el realm y verifiqué que el archivo incluye los clients y los usuarios de prueba.

## 15. Docker Compose con todos los servicios y réplicas de Booking
- Prompts: Debati la manera de como se va a levantar el backend del proyecto, teniendo en cuenta lo que dijo el profesor (lo que no está aclarado no está prohibido, solo hace falta que compile y levante) pedí asistencia para hacerlo desde el docker compose up.
- Qué se usó: un Dockerfile compartido por los cuatro servicios, un docker-compose con PostgreSQL, Keycloak y los servicios, dos réplicas de Booking sobre la misma suscripción, la configuración del emisor de Keycloak para que los tokens valgan dentro y fuera de Docker, y secretos de desarrollo fijos en el realm.
- Mi aporte: decidí dockerizar por ser la forma más limpia de ejecutar el sistema, apliqué los archivos y los secretos del realm, y creé el `.env` con el connection string. [Verifiqué que el sistema levanta con un solo `docker compose up` y que las dos réplicas se reparten los mensajes.]

## 16. Eliminacion de .env
- Prompts: pedí un script para que le sea mas sencillo al grupo guardar el string de conexion.
- Qué se usó: se crearon varios scripts para mejorar la calidad de vida del grupo al momento de levantar el proyecto.
- Mi aporte: edite un par de errores en los scripts para que no dieran errores y los probe.

## 17. Varios eventos y CORS
- Prompts: Le pedi que agregue dos eventos mas en el seeder y me pasara el codigo necesario para las clases para poder sumar 2 eventos mas.
- Qué se usó: tres eventos sembrados de forma idempotente.
- Mi aporte: aplique los cambios necesesarios, levante la app para ver que no habia problemas.