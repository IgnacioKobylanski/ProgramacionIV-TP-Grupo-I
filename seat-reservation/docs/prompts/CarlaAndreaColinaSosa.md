# Historial de prompts: Carla Andrea Colina Sosa

**Herramienta:** ChatGPT (OpenAI).  
**Trabajo práctico:** Programación IV — Sistema de reserva de asientos.  
**Área de trabajo:** testing de Availability (REST) y Payment (gRPC), preparación del entorno y registro de resultados.  
**Referencia del código probado:** commit `eca310f28878a5d3bec1d8e84e462cb87676d9eb`.  
**Período de las interacciones documentadas:** 24 octubre de 2026.

> Este registro es un resumen temático de interacciones reales, siguiendo el formato usado en la documentación de prompts del repositorio. Las consultas se describen por su propósito; cuando se incluyen citas, corresponden a mensajes efectivamente enviados. No constituye una transcripción íntegra de la conversación.

## 1. Reconocimiento del proyecto y alcance del testing

- **Consultas / prompts:** compartí el enunciado del TP, ejemplos de mensajería, el archivo de referencia del plan y las comunicaciones del equipo. Solicité ayuda para comprender el estado de los microservicios, mi participación en el testing y el procedimiento para trabajar sobre el repositorio.
- **Qué se usó:** explicación del flujo de Availability, Azure Service Bus, Booking, Payment, Notifications y Keycloak; identificación de pruebas posibles sin esperar la integración completa.
- **Mi aporte:** aporté la documentación del grupo, identifiqué la división de tareas y decidí comenzar con pruebas independientes de Availability y Payment, sin modificar código compartido.

## 2. Preparación del entorno de pruebas

- **Consultas / prompts:** comuniqué que había clonado el repositorio en Visual Studio y consulté el error `Npgsql.NpgsqlException: Failed to connect to 127.0.0.1:5432`, ocurrido al ejecutar `Database.MigrateAsync()`. También pedí indicaciones ante problemas al configurar WSL y Docker.
- **Qué se usó:** explicación de la dependencia de PostgreSQL; comandos para comprobar y habilitar WSL 2, iniciar Docker y comprobar los contenedores; ejecución de `dotnet build`, `docker compose up -d` y `docker compose ps`.
- **Mi aporte:** cloné el repositorio, compilé la solución, habilité WSL 2, instalé Docker Desktop, inicié PostgreSQL y Keycloak y comprobé que los servicios estaban operativos.

## 3. Pruebas funcionales de Availability (REST)

- **Consultas / prompts:** compartí los resultados JSON de las consultas a `/events` y `/events/{id}/seats`, así como el HTTP 404 obtenido al solicitar los asientos de un evento inexistente. Solicité la interpretación de esas respuestas.
- **Qué se usó:** casos AV-01 (consulta de eventos), AV-02 (consulta de 20 asientos) y AV-03 (evento inexistente), junto con criterios de comparación entre resultado esperado y observado.
- **Mi aporte:** ejecuté las solicitudes desde el navegador, comprobé la existencia de un evento y sus 20 asientos, verifiqué el manejo del evento inexistente y aporté las respuestas observadas.

## 4. Preparación de las pruebas gRPC de Payment

- **Consultas / prompts:** solicité instrucciones para instalar Postman, crear una solicitud gRPC, utilizar el archivo `src/Contracts/Protos/payment.proto` y seleccionar el método `PaymentProcessor.ChargeReservation`. Consulté las opciones de la interfaz cuando no encontraba el método.
- **Qué se usó:** configuración de `localhost:5003` sin TLS, selección del contrato gRPC y carga de mensajes de prueba.
- **Mi aporte:** inicié Payment en Visual Studio, configuré Postman e invoqué personalmente el servicio.

## 5. Pruebas de cobro, rechazo e idempotencia

- **Consultas / prompts:** envié a la conversación las respuestas del cobro aprobado, del cobro rechazado por monto fuera de rango y de la repetición de una reserva.
- **Qué se usó:** casos PAY-01 (cobro aprobado), PAY-02 (repetición de la misma reserva) y PAY-03 (monto superior al máximo); comprobación de `approved`, `payment_id` y `reason`.
- **Mi aporte:** ejecuté las solicitudes desde Postman, verifiqué que el pago aprobado devolviera el mismo `payment_id` al repetirse y comprobé la respuesta de rechazo con el motivo correspondiente.

## 6. Verificación de auditoría y persistencia

- **Consultas / prompts:** compartí las líneas `AUDITORIA inicio cobro` y `AUDITORIA fin cobro`, y pedí orientación para consultar la base de datos de Payment desde Docker.
- **Qué se usó:** interpretación del `CorrelationId` y de los registros SQL; comandos `psql` de solo lectura para identificar la base `payment` y contar registros por `ReservationId`.
- **Mi aporte:** revisé los logs del servicio y ejecuté una consulta SQL que devolvió **un registro** para la reserva repetida, complementando la comprobación de idempotencia realizada en Postman.

## 7. Identificación de la versión y organización de las evidencias

- **Consultas / prompts:** consulté cómo documentar las pruebas cuando el resto del grupo sigue publicando commits; compartí las salidas de `git reflog`, `git status`, `git fetch origin` y `git log`.
- **Qué se usó:** identificación del commit base `eca310f`, diferencia entre `git fetch` y `git pull`, y criterio de documentación por ejecuciones asociadas a una revisión concreta del repositorio.
- **Mi aporte:** identifiqué el commit clonado y comprobé que mi árbol de trabajo estaba limpio; consulté los cambios remotos sin modificar el código local y decidí conservar la primera ejecución como referencia para posteriores pruebas de regresión.

## Alcance de la asistencia

La IA se utilizó como apoyo para interpretar errores, preparar el entorno, definir procedimientos de prueba y analizar resultados. La ejecución de comandos, las solicitudes HTTP/gRPC, la revisión de registros y las comprobaciones en PostgreSQL se realizaron manualmente. **No se generó ni modificó código de los microservicios durante estas actividades de testing.**

## 8. Diagnóstico del problema con Azure Service Bus

- **Consultas / prompts:** solicité asistencia para investigar por qué los mensajes publicados por Availability no eran recibidos por Booking. Compartí fragmentos del código del publicador, del consumidor y de la configuración de los servicios. También consulté cómo ejecutar de forma independiente el ejemplo de mensajería proporcionado por el profesor.
- **Qué se usó:** revisión de la configuración del topic, namespace, credenciales y suscripción; análisis del funcionamiento del consumidor de Booking; instrucciones para ejecutar una aplicación de consola con Azure Service Bus y comparar sus resultados con los obtenidos por otro integrante.
- **Mi aporte:** revisé la configuración local y ejecuté personalmente el ejemplo del profesor desde mi computadora. El mensaje se enviaba correctamente, pero no se recibía desde la suscripción. Este comportamiento también se había reproducido en las pruebas de otro integrante, sin que se identificara la causa. Los resultados se compartieron con el equipo y contribuyeron a evaluar una alternativa de mensajería.

## 9. Migración de Azure Service Bus a RabbitMQ

- **Consultas / prompts:** compartí las comunicaciones del equipo sobre las dificultades con Azure Service Bus y la decisión de utilizar RabbitMQ como broker local. Solicité orientación para obtener la nueva versión del repositorio y comprender los cambios en la infraestructura.
- **Qué se usó:** explicación de las diferencias entre ambas soluciones, identificación del exchange `grupo1-booking`, la cola `booking` y la cola de mensajes fallidos `booking.dead`; procedimientos para clonar el repositorio y preparar el entorno con Docker Compose.
- **Mi aporte:** participé en la evaluación de la alternativa, apoyé la decisión del equipo y preparé una nueva copia local del proyecto, conservando la versión anterior como respaldo. La implementación de la migración estuvo a cargo de otro integrante; mi participación se concentró en preparar y verificar el nuevo entorno de pruebas.

## 10. Verificación del entorno local con RabbitMQ

- **Consultas / prompts:** compartí los resultados de `docker compose up -d --build` y los errores de inicio de RabbitMQ. Solicité ayuda para interpretar los registros y comprobar el funcionamiento del broker y de las réplicas de Booking.
- **Qué se usó:** análisis del error de permisos sobre `.erlang.cookie`, inspección del almacenamiento de Docker, recreación del contenedor y su volumen anónimo, comprobación de los servicios mediante `docker compose ps` y consulta de las colas con `rabbitmqctl`.
- **Mi aporte:** compilé las imágenes de los microservicios, resolví el inconveniente local de inicio de RabbitMQ y comprobé que los ocho contenedores estuvieran en ejecución. Verifiqué que la cola `booking` registrara dos consumidores conectados, correspondientes a las dos réplicas de Booking.

## 11. Prueba de tratamiento de mensajes inválidos

- **Consultas / prompts:** solicité instrucciones para utilizar el panel de administración de RabbitMQ y comprobar el tratamiento de un mensaje que no tuviera formato JSON válido.
- **Qué se usó:** publicación manual desde el exchange `grupo1-booking`, consulta de las colas y verificación del mensaje almacenado en `booking.dead`.
- **Mi aporte:** publiqué un mensaje de texto inválido, comprobé que la cola `booking.dead` registrara un mensaje y verifiqué que su contenido coincidiera con el enviado. Conservé capturas como respaldo de la prueba y registré el resultado como aprobado.

## Alcance de la asistencia

La IA se utilizó como apoyo para comprender la arquitectura, interpretar errores, preparar los entornos de prueba, definir procedimientos y analizar resultados. La ejecución de comandos, las solicitudes HTTP/gRPC, las comprobaciones en PostgreSQL y las verificaciones de RabbitMQ fueron realizadas manualmente.

No se generó ni modificó código de los microservicios durante estas actividades. La migración a RabbitMQ fue implementada por otro integrante del equipo.

El registro prioriza las intervenciones relevantes para el desarrollo del trabajo práctico y omite las comprobaciones intermedias que no aportaron resultados significativos.
