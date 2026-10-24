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