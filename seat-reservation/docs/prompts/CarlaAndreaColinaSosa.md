# Historial de prompts: Carla Andrea Colina Sosa

**Herramienta:** ChatGPT (OpenAI).  

**Trabajo práctico:** Programación IV — Sistema de reserva de asientos.  

**Área de trabajo:** pruebas de Availability (REST), Payment (gRPC), RabbitMQ y frontend React; preparación de entornos, autenticación y documentación de resultados.  

**Referencia inicial del código probado:** commit `eca310f28878a5d3bec1d8e84e462cb87676d9eb`. Las pruebas posteriores utilizaron versiones actualizadas del proyecto; no se registró aquí el hash exacto de la última ejecución.  

**Período de las interacciones documentadas:** 24 al 31 de octubre de 2026.

> Este registro es un resumen temático de interacciones reales, siguiendo el formato usado en la documentación de prompts del repositorio. Las consultas se describen por su propósito; cuando se incluyen citas, corresponden a mensajes efectivamente enviados. No constituye una transcripción íntegra de la conversación.

## 1. Reconocimiento del proyecto y alcance del testing

- \***\*Consultas / prompts:\*\*** compartí el enunciado del TP, ejemplos de mensajería, el archivo de referencia del plan y las comunicaciones del equipo. Solicité ayuda para comprender el estado de los microservicios, mi participación en el testing y el procedimiento para trabajar sobre el repositorio.

- \***\*Qué se usó:\*\*** explicación del flujo de Availability, Azure Service Bus, Booking, Payment, Notifications y Keycloak; identificación de pruebas posibles sin esperar la integración completa.

- \***\*Mi aporte:\*\*** aporté la documentación del grupo, identifiqué la división de tareas y decidí comenzar con pruebas independientes de Availability y Payment, sin modificar código compartido.

## 2. Preparación del entorno de pruebas

- \***\*Consultas / prompts:\*\*** comuniqué que había clonado el repositorio en Visual Studio y consulté el error `Npgsql.NpgsqlException: Failed to connect to 127.0.0.1:5432`, ocurrido al ejecutar `Database.MigrateAsync()`. También pedí indicaciones ante problemas al configurar WSL y Docker.

- \***\*Qué se usó:\*\*** explicación de la dependencia de PostgreSQL; comandos para comprobar y habilitar WSL 2, iniciar Docker y comprobar los contenedores; ejecución de `dotnet build`, `docker compose up -d` y `docker compose ps`.

- \***\*Mi aporte:\*\*** cloné el repositorio, compilé la solución, habilité WSL 2, instalé Docker Desktop, inicié PostgreSQL y Keycloak y comprobé que los servicios estaban operativos.

## 3. Pruebas funcionales de Availability (REST)

- \***\*Consultas / prompts:\*\*** compartí los resultados JSON de las consultas a `/events` y `/events/{id}/seats`, así como el HTTP 404 obtenido al solicitar los asientos de un evento inexistente. Solicité la interpretación de esas respuestas.

- \***\*Qué se usó:\*\*** casos AV-01 (consulta de eventos), AV-02 (consulta de 20 asientos) y AV-03 (evento inexistente), junto con criterios de comparación entre resultado esperado y observado.

- \***\*Mi aporte:\*\*** ejecuté las solicitudes desde el navegador, comprobé la existencia de un evento y sus 20 asientos, verifiqué el manejo del evento inexistente y aporté las respuestas observadas.

## 4. Preparación de las pruebas gRPC de Payment

- \***\*Consultas / prompts:\*\*** solicité instrucciones para instalar Postman, crear una solicitud gRPC, utilizar el archivo `src/Contracts/Protos/payment.proto` y seleccionar el método `PaymentProcessor.ChargeReservation`. Consulté las opciones de la interfaz cuando no encontraba el método.

- \***\*Qué se usó:\*\*** configuración de `localhost:5003` sin TLS, selección del contrato gRPC y carga de mensajes de prueba.

- \***\*Mi aporte:\*\*** inicié Payment en Visual Studio, configuré Postman e invoqué personalmente el servicio.

## 5. Pruebas de cobro, rechazo e idempotencia

- \***\*Consultas / prompts:\*\*** envié a la conversación las respuestas del cobro aprobado, del cobro rechazado por monto fuera de rango y de la repetición de una reserva.

- \***\*Qué se usó:\*\*** casos PAY-01 (cobro aprobado), PAY-02 (repetición de la misma reserva) y PAY-03 (monto superior al máximo); comprobación de `approved`, `payment_id` y `reason`.

- \***\*Mi aporte:\*\*** ejecuté las solicitudes desde Postman, verifiqué que el pago aprobado devolviera el mismo `payment_id` al repetirse y comprobé la respuesta de rechazo con el motivo correspondiente.

## 6. Verificación de auditoría y persistencia

- \***\*Consultas / prompts:\*\*** compartí las líneas `AUDITORIA inicio cobro` y `AUDITORIA fin cobro`, y pedí orientación para consultar la base de datos de Payment desde Docker.

- \***\*Qué se usó:\*\*** interpretación del `CorrelationId` y de los registros SQL; comandos `psql` de solo lectura para identificar la base `payment` y contar registros por `ReservationId`.

- \***\*Mi aporte:\*\*** revisé los logs del servicio y ejecuté una consulta SQL que devolvió \***\*un registro\*\*** para la reserva repetida, complementando la comprobación de idempotencia realizada en Postman.

## 7. Identificación de la versión y organización de las evidencias

- \***\*Consultas / prompts:\*\*** consulté cómo documentar las pruebas cuando el resto del grupo sigue publicando commits; compartí las salidas de `git reflog`, `git status`, `git fetch origin` y `git log`.

- \***\*Qué se usó:\*\*** identificación del commit base `eca310f`, diferencia entre `git fetch` y `git pull`, y criterio de documentación por ejecuciones asociadas a una revisión concreta del repositorio.

- \***\*Mi aporte:\*\*** identifiqué el commit clonado y comprobé que mi árbol de trabajo estaba limpio; consulté los cambios remotos sin modificar el código local y decidí conservar la primera ejecución como referencia para posteriores pruebas de regresión.

## Nota de alcance de la primera etapa

La IA se utilizó como apoyo para interpretar errores, preparar el entorno, definir procedimientos de prueba y analizar resultados. La ejecución de comandos, las solicitudes HTTP/gRPC, la revisión de registros y las comprobaciones en PostgreSQL se realizaron manualmente. \***\*No se generó ni modificó código de los microservicios durante estas actividades de testing.\*\***

## 8. Diagnóstico del problema con Azure Service Bus

- \***\*Consultas / prompts:\*\*** solicité asistencia para investigar por qué los mensajes publicados por Availability no eran recibidos por Booking. Compartí fragmentos del código del publicador, del consumidor y de la configuración de los servicios. También consulté cómo ejecutar de forma independiente el ejemplo de mensajería proporcionado por el profesor.

- \***\*Qué se usó:\*\*** revisión de la configuración del topic, namespace, credenciales y suscripción; análisis del funcionamiento del consumidor de Booking; instrucciones para ejecutar una aplicación de consola con Azure Service Bus y comparar sus resultados con los obtenidos por otro integrante.

- \***\*Mi aporte:\*\*** revisé la configuración local y ejecuté personalmente el ejemplo del profesor desde mi computadora. El mensaje se enviaba correctamente, pero no se recibía desde la suscripción. Este comportamiento también se había reproducido en las pruebas de otro integrante, sin que se identificara la causa. Los resultados se compartieron con el equipo y contribuyeron a evaluar una alternativa de mensajería.

## 9. Migración de Azure Service Bus a RabbitMQ

- \***\*Consultas / prompts:\*\*** compartí las comunicaciones del equipo sobre las dificultades con Azure Service Bus y la decisión de utilizar RabbitMQ como broker local. Solicité orientación para obtener la nueva versión del repositorio y comprender los cambios en la infraestructura.

- \***\*Qué se usó:\*\*** explicación de las diferencias entre ambas soluciones, identificación del exchange `grupo1-booking`, la cola `booking` y la cola de mensajes fallidos `booking.dead`; procedimientos para clonar el repositorio y preparar el entorno con Docker Compose.

- \***\*Mi aporte:\*\*** participé en la evaluación de la alternativa, apoyé la decisión del equipo y preparé una nueva copia local del proyecto, conservando la versión anterior como respaldo. La implementación de la migración estuvo a cargo de otro integrante; mi participación se concentró en preparar y verificar el nuevo entorno de pruebas.

## 10. Verificación del entorno local con RabbitMQ

- \***\*Consultas / prompts:\*\*** compartí los resultados de `docker compose up -d --build` y los errores de inicio de RabbitMQ. Solicité ayuda para interpretar los registros y comprobar el funcionamiento del broker y de las réplicas de Booking.

- \***\*Qué se usó:\*\*** análisis del error de permisos sobre `.erlang.cookie`, inspección del almacenamiento de Docker, recreación del contenedor y su volumen anónimo, comprobación de los servicios mediante `docker compose ps` y consulta de las colas con `rabbitmqctl`.

- \***\*Mi aporte:\*\*** compilé las imágenes de los microservicios, resolví el inconveniente local de inicio de RabbitMQ y comprobé que los ocho contenedores estuvieran en ejecución. Verifiqué que la cola `booking` registrara dos consumidores conectados, correspondientes a las dos réplicas de Booking.

## 11. Prueba de tratamiento de mensajes inválidos

- \***\*Consultas / prompts:\*\*** solicité instrucciones para utilizar el panel de administración de RabbitMQ y comprobar el tratamiento de un mensaje que no tuviera formato JSON válido.

- \***\*Qué se usó:\*\*** publicación manual desde el exchange `grupo1-booking`, consulta de las colas y verificación del mensaje almacenado en `booking.dead`.

- \***\*Mi aporte:\*\*** publiqué un mensaje de texto inválido, comprobé que la cola `booking.dead` registrara un mensaje y verifiqué que su contenido coincidiera con el enviado. Conservé capturas como respaldo de la prueba y registré el resultado como aprobado.

## Nota de alcance de la segunda etapa

La IA se utilizó como apoyo para comprender la arquitectura, interpretar errores, preparar los entornos de prueba, definir procedimientos y analizar resultados. La ejecución de comandos, las solicitudes HTTP/gRPC, las comprobaciones en PostgreSQL y las verificaciones de RabbitMQ fueron realizadas manualmente.

No se generó ni modificó código de los microservicios durante estas actividades. La migración a RabbitMQ fue implementada por otro integrante del equipo.

El registro prioriza las intervenciones relevantes para el desarrollo del trabajo práctico y omite las comprobaciones intermedias que no aportaron resultados significativos.

## 12. Actualización del repositorio y planificación de pruebas del frontend

- **Consultas / prompts:** solicité ayuda para incorporar los cambios recientes del grupo, compilar el frontend de React y preparar una batería de pruebas funcionales. Compartí resultados de `npm install`, `npm run build`, `npm run dev`, Git y Docker Compose; pedí que se documentaran los casos en `docs/frontend-tests.md`.
- **Qué se usó:** orientación para actualizar la copia local sin sobrescribir el trabajo del equipo; interpretación de la compilación, arranque de Vite y servicios en Docker; diseño de los casos FRONT-01 a FRONT-17 con objetivo, procedimiento, resultado esperado y estado.
- **Mi aporte:** actualicé y ejecuté el proyecto en mi computadora, realicé manualmente las pruebas desde Chrome y registré observaciones y estados en el documento del repositorio. El desarrollo de los componentes frontend estuvo a cargo de otros integrantes.

## 13. Diagnóstico de Availability y autenticación interna en Keycloak

- **Consultas / prompts:** informé que la página mostraba los eventos pero devolvía HTTP 503 al entrar a «Ver asientos». Compartí los registros del contenedor y los eventos de Keycloak que indicaban `401 Unauthorized`, `invalid_client_credentials` y `clientId=availability-service`. Consulté cómo corregir el entorno local sin modificar el repositorio ni borrar volúmenes.
- **Qué se usó:** comparación de `ServiceAuth__ClientSecret` entre Docker Compose y `infra/keycloak/seat-reservation-realm.json`; inspección del cliente en Keycloak Admin; comandos `kcadm.sh` para identificar y actualizar el cliente en el realm `seat-reservation`, conservando las demás propiedades mediante `--merge`.
- **Mi aporte:** identifiqué que el secreto almacenado en el Keycloak local era distinto al definido en los archivos del proyecto, apliqué la corrección únicamente en el cliente local `availability-service` y comprobé que la grilla de asientos empezó a cargar. No se eliminaron realms ni volúmenes.

## 14. Redirección al login y autenticación de usuarios

- **Consultas / prompts:** comuniqué el mensaje `Invalid parameter: redirect_uri` al presionar «Ingresar para reservar». Compartí la configuración del cliente `seat-web`, que autorizaba `http://localhost:5001/*`, mientras Vite servía el frontend en `http://localhost:5173`.
- **Qué se usó:** revisión de `Valid redirect URIs` y `Web origins` en Keycloak Admin; explicación de la diferencia entre la dirección del frontend y la del servicio Availability; análisis de los usuarios de ejemplo y del almacenamiento de contraseñas mediante Argon2, sin intentar recuperar las contraseñas desde sus hashes.
- **Mi aporte:** incorporé la dirección local del frontend a las permitidas para `seat-web`, comprobé que se abría el login y, cuando obtuve las credenciales de prueba del equipo, inicié sesión correctamente. También comprobé el cierre de sesión y la exigencia de volver a ingresar para reservar.

## 15. Diagnóstico de una reserva rechazada y corrección del acceso a Payment

- **Consultas / prompts:** reporté una reserva con estado «Rechazada» y compartí registros de Booking donde aparecían `401 Unauthorized` al obtener un token de servicio, `Payment no disponible` y `Resultado=Rechazada Motivo=PagoNoDisponible`.
- **Qué se usó:** identificación del cliente `booking-service` y comparación de su secreto entre Compose, el archivo del realm y la configuración efectiva de Keycloak; actualización controlada del cliente local con `kcadm.sh` y `--merge`.
- **Mi aporte:** detecté que la credencial en mi Keycloak local no coincidía con la configuración de Booking, apliqué la corrección local y volví a intentar la reserva. La nueva solicitud quedó confirmada, y el asiento apareció ocupado. La operación rechazada quedó registrada con el motivo «El servicio de pago no está disponible».

## 16. Ejecución de pruebas funcionales FRONT-01 a FRONT-17

- **Consultas / prompts:** solicité revisar los resultados de cada caso del plan original y compartí lo que aparecía en pantalla al navegar, consultar asientos, autenticarse, reservar y provocar errores controlados.
- **Qué se usó:** interpretación de respuestas HTTP 200 y 404; inspección de la solicitud `seats` desde las herramientas de desarrollador; comparación de `occupied: true` con el asiento bloqueado; prueba de caída controlada de Availability con `docker compose stop availability` y su restauración con `docker compose start availability`.
- **Mi aporte:** comprobé la carga de la página, el listado de eventos, la navegación, la grilla, la selección exclusiva de un asiento, el bloqueo de los ocupados, la redirección y el login, la reserva confirmada, su estado de seguimiento y la gestión visible de errores. En particular, el frontend mostró «El servicio no está disponible en este momento» cuando Availability estuvo detenido. También verifiqué que una reserva rechazada se mostrara como tal y con motivo legible.

## 17. Pruebas con distintos usuarios e historial de reservas (FRONT-18 a FRONT-24)

- **Consultas / prompts:** señalé que las pruebas iniciales no cubrían la conservación de reservas entre usuarios, el historial propio, las rechazadas y la consistencia de la información del evento. Pedí ampliar la cobertura funcional.
- **Qué se usó:** propuesta y seguimiento de los casos FRONT-18 a FRONT-24; criterios para evaluar privacidad del listado, historial vacío, persistencia al cerrar y volver a iniciar sesión y consistencia de datos entre evento e historial.
- **Mi aporte:** inicié sesión con dos cuentas de prueba; confirmé que ambas veían como ocupado un asiento reservado por una de ellas. En «Mis reservas» observé inicialmente el estado vacío del segundo usuario; después de reservar, aparecieron su asiento y estado «Confirmada». Verifiqué que el primer usuario solamente veía sus propias reservas, incluidas las rechazadas, y que los historiales persistían tras alternar sesiones. Comprobé que el listado incluía nombre, fecha y hora del evento, asiento y estado, y que coincidían con los datos originales.
- **Observación:** la vista «Ver más detalles» presentaba menos datos contextuales del evento que el listado «Mis reservas»; se registró como posible mejora de usabilidad, no como falla de la reserva.

## 18. Pruebas de concurrencia con dos sesiones (FRONT-25 a FRONT-32)

- **Consultas / prompts:** propuse utilizar simultáneamente dos sesiones para evaluar situaciones cercanas al uso real: reservas del mismo asiento, reservas de asientos distintos, actualización de la grilla mientras otra persona reserva y recarga durante el procesamiento.
- **Qué se usó:** diseño de pruebas con Chrome normal e incógnito, dos usuarios autenticados y el mismo evento; diferenciación entre consistencia del backend, actualización automática del frontend y actualización manual; seguimiento de reservas por la URL `/reservations/{id}`.
- **Mi aporte:** observé que ambos usuarios veían inicialmente la misma disponibilidad. Cuando el primero reservaba, la grilla del segundo **no se actualizaba automáticamente**. Al intentar reservar desde la segunda sesión ese mismo asiento, el sistema rechazó la solicitud con «Otro usuario reservó ese asiento», sin duplicar una confirmación. Dos reservas de asientos diferentes, enviadas con pocos instantes de diferencia, se confirmaron. Cuando el asiento permanecía seleccionado en una sesión desactualizada, presionar «Actualizar» permitía ver el nuevo bloqueo. También recargué la pantalla de seguimiento durante una solicitud y el estado avanzó hasta «Confirmada», y pude consultar los historiales simultáneamente.
- **Observaciones:** no se verificó concurrencia estrictamente simultánea al nivel de infraestructura; se probaron acciones manuales cercanas en el tiempo. La recarga no interrumpió el seguimiento, pero no se verificó con registros que no existiera una solicitud duplicada. La actualización de disponibilidad entre sesiones requiere intervención manual en el comportamiento observado.

## 19. Restricciones de acceso a reservas (FRONT-33 a FRONT-35)

- **Consultas / prompts:** solicité ampliar las pruebas de privacidad para comprobar qué sucedía al intentar abrir «Mis reservas» sin sesión y al utilizar enlaces directos a reservas ajenas o sin autenticación.
- **Qué se usó:** pruebas de navegación desde dos cuentas de ejemplo y una sesión anónima, utilizando rutas de seguimiento de reserva.
- **Mi aporte:** comprobé que «Mis reservas» sin autenticación mostraba «Tenés que iniciar sesión para ver tus reservas». Al abrir el enlace de una reserva de otra cuenta se mostró «No encontramos lo que buscabas»; sin sesión se mostró «Tenés que iniciar sesión para ver esto» y el botón «Ingresar». No se revelaron datos de la reserva desde esas vistas.
- **Alcance:** estos resultados verifican el comportamiento visible del frontend; no sustituyen una auditoría directa de autorización de todos los endpoints del backend.

## 20. Actualización y organización del registro de testing

- **Consultas / prompts:** pedí consolidar el archivo `docs/frontend-tests.md` con los 17 casos iniciales, las pruebas adicionales hasta FRONT-35 y las observaciones de los fallos de Keycloak, sin registrar como aprobadas verificaciones que no se hubieran realizado.
- **Qué se usó:** estructuración de evidencias por caso, distinción entre aprobado, observación y verificación parcial, y redacción de resultados reproducibles.
- **Mi aporte:** aporté cada resultado observado desde el navegador y los registros de Docker; corregí descripciones cuando advertí que la pantalla «Mis reservas» sí mostraba los datos del evento. Solicité conservar el historial de prompts con los nuevos avances del proyecto.

## Alcance general de la asistencia y responsabilidades

La IA se utilizó para formular hipótesis de diagnóstico, explicar configuraciones, proponer procedimientos de verificación, interpretar resultados, organizar casos de prueba y redactar documentación. Las pruebas, las comparaciones en Keycloak Admin, las modificaciones de configuración **del entorno local**, los comandos y las observaciones en el navegador fueron realizados manualmente por mí.

Las correcciones de los secretos de `availability-service` y `booking-service`, así como la habilitación del origen del frontend para `seat-web`, fueron ajustes de mi instancia local de Keycloak, no cambios al código fuente ni a las configuraciones compartidas del repositorio.

El registro resume interacciones relevantes y resultados reportados; no es una transcripción literal de todos los mensajes. Las pruebas con dos usuarios demuestran el comportamiento observado durante la ejecución manual, no una auditoría exhaustiva de seguridad, rendimiento o concurrencia.
