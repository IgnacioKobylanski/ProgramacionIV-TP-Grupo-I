# Documentación de Testing - Backend - Seat Reservation

## Criterio de documentación

Cada prueba se documenta siguiendo el siguiente ciclo:

**Prueba inicial → Resultado → Error detectado → Corrección → Re-test → Resultado final**

Cuando una prueba no presenta errores:

- Se registra el resultado como `PASS`.
- Se indica que no se encontraron errores.
- La corrección se marca como `No aplica`.
- Se indica que no fue necesario realizar un re-test.
- El resultado final permanece como `PASS`.

Cuando una prueba presenta un error:

- Se conserva el resultado inicial.
- Se documenta el error encontrado.
- Se registra la corrección realizada.
- Se documenta el re-test.
- Se registra el resultado final.

---

# A. Contrato y validación de entrada

## 1. Crear reserva con payload válido

**Qué se prueba:**  
Crear una reserva utilizando un payload completo y válido.

**Resultado esperado:**  
El backend debe aceptar la solicitud y crear correctamente la reserva.

**Problema que permite detectar:**  
Errores en el contrato de la API, validaciones incorrectas o fallos en el flujo normal de creación.

**Importancia:**  
Permite comprobar que el caso de uso principal funciona correctamente.

**Resultado inicial:**  
> PASS

**Observaciones / errores encontrados:**  
> No se encontraron errores.

**Corrección realizada:**  
> No aplica. La prueba no presentó errores.

**Re-test:**  
> No fue necesario realizar un re-test

**Resultado final:**  
> PASS

---

## 2. Body vacío o JSON malformado

**Qué se prueba:**  
Enviar una solicitud sin body, con un body vacío o con un JSON malformado.

**Resultado esperado:**  
El backend debe rechazar la solicitud de manera controlada y devolver un código de error apropiado.

**Problema que permite detectar:**  
Errores de parsing, excepciones no controladas o respuestas incorrectas ante entradas inválidas.

**Importancia:**  
Permite comprobar que el backend maneja correctamente solicitudes malformadas.

**Resultado inicial:**  
> REVISAR

**Observaciones / errores encontrados:**  
> Se detectó que el endpoint POST /reservations no valida campos obligatorios; ante campos ausentes responde 404 en vez de 400

**Corrección realizada:**  
> Pendiente

**Re-test:**  
> Pendiente

**Resultado final:**  
> REVISAR

---

## 3. Campos obligatorios ausentes

**Qué se prueba:**  
Enviar una solicitud omitiendo uno o varios campos obligatorios.

**Resultado esperado:**  
El backend debe rechazar la solicitud e indicar que faltan datos requeridos.

**Problema que permite detectar:**  
Validaciones incompletas o inexistentes.

**Importancia:**  
Evita que se creen reservas con información incompleta.

**Resultado inicial:**  
> REVISAR

**Observaciones / errores encontrados:**  
> Se detectó que el endpoint POST /reservations no valida campos obligatorios; ante 'eventId' o 'seatId' ausentes responde 404 en vez de 400

**Corrección realizada:**  
> PENDIENTE

**Re-test:**  
> PENDIENTE

**Resultado final:**  
> REVISAR

---

## 4. Tipos de datos incorrectos

**Qué se prueba:**  
Enviar campos con tipos de datos diferentes a los esperados.

**Resultado esperado:**  
La API debe rechazar los datos inválidos y devolver una respuesta controlada.

**Problema que permite detectar:**  
Errores de serialización, validación o conversión de tipos.

**Importancia:**  
Garantiza que el contrato de la API sea respetado.

**Resultado inicial:**  
> PASS

**Observaciones / errores encontrados:**  
> No se encontraron errores.

**Corrección realizada:**  
> No aplica. La prueba no presentó errores.

**Re-test:**  
> No fue necesario realizar un re-test

**Resultado final:**  
> PASS

---

## 5. Valores límite

**Qué se prueba:**  
Enviar valores en los límites permitidos por el sistema.

**Resultado esperado:**  
Los valores válidos dentro del límite deben ser aceptados, mientras que los que superen las restricciones deben ser rechazados.

**Problema que permite detectar:**  
Errores de validación de rangos y problemas con valores extremos.

**Importancia:**  
Permite comprobar el comportamiento del sistema en los límites de sus reglas de validación.

**Resultado inicial:**  
> PASS

**Observaciones / errores encontrados:**  
> No se encontraron errores.

**Corrección realizada:**  
> No aplica. La prueba no presentó errores.

**Re-test:**  
> No fue necesario realizar un re-test

**Resultado final:**  
> PASS

---

## 6. Strings largos o con caracteres especiales

**Qué se prueba:**  
Enviar cadenas de texto excesivamente largas o que contengan caracteres especiales.

**Resultado esperado:**  
El backend debe validar correctamente los datos y evitar errores inesperados.

**Problema que permite detectar:**  
Problemas de validación, almacenamiento o procesamiento de caracteres especiales.

**Importancia:**  
Permite comprobar la robustez del backend frente a entradas no convencionales.

**Resultado inicial:**  
> PASS

**Observaciones / errores encontrados:**  
> No se encontraron errores.

**Corrección realizada:**  
> No aplica. La prueba no presentó errores.

**Re-test:**  
> No fue necesario realizar un re-test

**Resultado final:**  
> PASS

---

## 7. IDs que no existen

**Qué se prueba:**  
Enviar IDs correspondientes a recursos inexistentes.

**Resultado esperado:**  
El backend debe identificar que los recursos no existen y devolver una respuesta controlada.

**Problema que permite detectar:**  
Errores en las búsquedas de recursos o respuestas incorrectas ante referencias inexistentes.

**Importancia:**  
Evita que se procesen reservas asociadas a eventos o asientos inexistentes.

**Resultado inicial:**  
> PASS

**Observaciones / errores encontrados:**  
> No se encontraron errores.

**Corrección realizada:**  
> No aplica. La prueba no presentó errores.

**Re-test:**  
> No fue necesario realizar un re-test

**Resultado final:**  
> PASS

---

## 8. Verbo HTTP incorrecto

**Qué se prueba:**  
Enviar solicitudes utilizando métodos HTTP que no corresponden al endpoint.

**Resultado esperado:**  
El backend debe rechazar el método no permitido y responder con el código correspondiente.

**Problema que permite detectar:**  
Configuraciones incorrectas de rutas o métodos HTTP permitidos.

**Importancia:**  
Permite comprobar que el contrato HTTP de la API está correctamente definido.

**Resultado inicial:**  
> PASS

**Observaciones / errores encontrados:**  
> No se encontraron errores.

**Corrección realizada:**  
> No aplica. La prueba no presentó errores.

**Re-test:**  
> No fue necesario realizar un re-test

**Resultado final:**  
> PASS 

---

# B. Reglas de negocio

En este bloque se evaluaron las reglas de negocio relacionadas con la creación y procesamiento de reservas.
Las reservas son asincrónicas: POST /reservations (Availability) responde 202 Accepted y publica la solicitud en RabbitMQ. Booking la consume, retiene el asiento, cobra mediante Payment (gRPC) y deja la reserva en estado `Confirmada` o `Rechazada`. El resultado se consulta después en GET /reservations/{requestId}. Un asiento se considera ocupado únicamente mientras tenga una reserva en estado `Retenida` o `Confirmada`.

---

### Prueba 9 - Reservar un asiento libre

**Qué se prueba:**  
Crear una reserva con un usuario autenticado utilizando un asiento que se encuentra disponible.

**Resultado esperado:**  
El endpoint `POST` responde con **202 Accepted** y devuelve `requestId` y `correlationId`. La reserva se procesa de forma asincrónica y posteriormente alcanza el estado **`Confirmada`**. El asiento utilizado debe aparecer como **`occupied: true`** en `GET /events/{eventId}/seats`. Además, Notifications debe registrar el aviso de confirmación (visible en `GET /notifications`).

**Problema que permite detectar:**  
Permite detectar problemas en la creación y procesamiento de reservas, en la cadena Availability → RabbitMQ → Booking → Payment → Notifications, así como inconsistencias entre el estado de la reserva y el estado final del asiento.

**Importancia:**  
Es la validación principal del flujo de reserva y sirve como base para varias de las pruebas posteriores.

**Resultado inicial:**  
> PASS

**Observaciones / errores encontrados:**  
> No se encontraron errores.

**Corrección realizada:**  
> [No aplica]

**Re-test:**  
> [No fue necesario realizar un re-test]

**Resultado final:**  
> PASS

---

### Prueba 10 - Reservar un asiento ya reservado

**Qué se prueba:**  
Intentar reservar un asiento que ya fue reservado previamente por otro usuario (por ejemplo, `usuario1` lo reserva y luego `usuario2` intenta reservarlo).

**Resultado esperado:**  
El `POST` no devuelve un `409 Conflict` de forma inmediata. El sistema responde **202 Accepted** y la solicitud debe ser procesada posteriormente por Booking hasta alcanzar el estado **`Rechazada`**, con motivo **`AsientoOcupado`**.

La primera reserva debe permanecer **`Confirmada`** y no debe ser reemplazada ni modificada por la segunda solicitud. La segunda solicitud rechazada no debe generar una notificación ni un cobro.

**Problema que permite detectar:**  
Permite detectar dobles reservas o situaciones en las que una nueva solicitud pueda modificar o pisar una reserva existente.

**Importancia:**  
Es una prueba fundamental para verificar la integridad de la disponibilidad de los asientos.

**Resultado inicial:**  
> PASS

**Observaciones / errores encontrados:**  
> No se encontraron errores.

**Corrección realizada:**  
> [No aplica]

**Re-test:**  
> [No fue necesario realizar un re-test]

**Resultado final:**  
> PASS

---

### Prueba 11 - Varios asientos en solicitudes consecutivas

**Qué se prueba:**  
Verificar la posibilidad de reservar varios asientos mediante solicitudes individuales consecutivas del mismo usuario.

**Resultado esperado:**  
Las tres solicitudes responden con **202 Accepted** y cada reserva alcanza posteriormente el estado **`Confirmada`**. Los tres asientos deben aparecer como ocupados y las tres reservas deben figurar en `GET /reservations/mine`.

**Problema que permite detectar:**  
Permite detectar problemas en la creación de múltiples reservas consecutivas o inconsistencias en la actualización del estado de los asientos y del historial del usuario.

**Importancia:**  
Permite comprobar el comportamiento del sistema cuando un usuario necesita reservar varios asientos, aunque la API no disponga de una operación por lote.

**Resultado inicial:**  
> PASS

**Observaciones / errores encontrados:**  
> No se encontraron errores.

**Corrección realizada:**  
> [No aplica]

**Re-test:**  
> [No fue necesario realizar un re-test]

**Resultado final:**  
> PASS

---

### Prueba 12 - Mismo asiento reservado dos veces por el mismo usuario

**Qué se prueba:**  
Intentar reservar dos veces el mismo asiento utilizando el mismo usuario, una a continuación de la otra.

**Resultado esperado:**  
Una de las reservas debe alcanzar el estado **`Confirmada`** y la segunda debe alcanzar el estado **`Rechazada`** con motivo **`AsientoOcupado`**.

Si ambas reservas alcanzaran el estado `Confirmada`, existiría una situación de **doble reserva**, lo que representaría un error grave de integridad del sistema.

**Problema que permite detectar:**  
Permite detectar la posibilidad de generar dos reservas confirmadas para un mismo asiento.

**Importancia:**  
Es una prueba crítica para verificar que las reglas de disponibilidad se mantengan incluso ante solicitudes repetidas sobre el mismo recurso.

**Resultado inicial:**  
> PASS

**Observaciones / errores encontrados:**  
> No se encontraron errores.

**Corrección realizada:**  
> [No aplica]

**Re-test:**  
> [No fue necesario realizar un re-test]

**Resultado final:**  
> PASS

---

### Prueba 13 - Reservas sobre eventos y asientos inválidos, pago rechazado y vencimiento

**Qué se prueba:**  
Validar el comportamiento del backend frente a diferentes situaciones relacionadas con eventos, asientos y reglas de cobro y vencimiento.

La prueba cubre las siguientes variantes:

- **13a:** Evento inexistente.
- **13b:** Asiento inexistente.
- **13c:** Asiento perteneciente a otro evento.
- **13d:** Pago rechazado por Payment (monto fuera del rango permitido, configurando `Booking__SeatPriceCents` por encima de `Payment__MaxAmount`).

**Resultado esperado:**  
Las variantes 13a, 13b y 13c deben ser rechazadas por Availability con **404 Not Found**, sin publicar ningún mensaje en RabbitMQ.

En la variante 13d, el `POST` responde 202 y la reserva alcanza el estado **`Rechazada`** con motivo **`PagoFallido`**; el asiento debe quedar libre y no debe enviarse ninguna notificación.

**Problema que permite detectar:**  
Permite detectar validaciones incompletas sobre eventos y asientos, y errores en las reglas de rechazo por pago, vencimiento y liberación de asientos.

**Importancia:**  
Permite verificar que las reglas de negocio se apliquen correctamente más allá del caso de reserva de un asiento disponible.

**Resultado inicial:**  
> PASS

**Observaciones / errores encontrados:**  
> No se encontraron errores.

**Corrección realizada:**  
> [No aplica]

**Re-test:**  
> [No fue necesario realizar un re-test]

**Resultado final:**  
> PASS

---

# C. Estados y flujo asincrónico

## 14. Consultar una reserva inmediatamente después de crearla

**Qué se prueba:**  
Crear una reserva y consultar su estado en `GET /reservations/{requestId}` inmediatamente después de recibir el 202.

**Resultado esperado:**  
El sistema debe devolver un estado coherente: **`EnProceso`** si Booking todavía no registró la solicitud, o el estado que Booking ya haya decidido (`Retenida`, `Confirmada` o `Rechazada`). Nunca debe responder 404 ni 500 para una solicitud propia recién creada.

**Problema que permite detectar:**  
Problemas de sincronización entre Availability y Booking en la zona de consistencia eventual.

**Importancia:**  
Permite comprobar la consistencia del sistema después de una operación.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

## 15. Consultar una reserva mientras se procesa

**Qué se prueba:**  
Consultar repetidamente (polling) una reserva durante el procesamiento asincrónico, desde que se crea hasta que alcanza un estado final.

**Resultado esperado:**  
El sistema debe devolver el estado actual sin generar inconsistencias. La secuencia observada debe respetar un orden válido (`EnProceso` → `Retenida` → `Confirmada` o `Rechazada`) y no debe retroceder de un estado final a uno anterior. Una solicitud ajena o inexistente debe responder **404**.

**Problema que permite detectar:**  
Errores en el manejo de estados intermedios y filtraciones de información entre usuarios.

**Importancia:**  
Permite comprobar el comportamiento del sistema durante procesos que no son instantáneos.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

## 16. Reintentar una operación asincrónica

**Qué se prueba:**  
Repetir una solicitud mientras una operación anterior todavía está siendo procesada, y reentregar al consumidor el mismo mensaje (mismo `requestId`) de la cola `booking`.

**Resultado esperado:**  
El sistema debe manejar correctamente el reintento sin generar datos duplicados o inconsistentes. Booking es idempotente por `RequestId`: una solicitud duplicada se ignora y existe una única reserva por solicitud. Payment es idempotente por `ReservationId` (un único cobro) y Notifications es idempotente por `ReservationId` (una única notificación).

**Problema que permite detectar:**  
Problemas de idempotencia o procesamiento duplicado en Booking, Payment o Notifications.

**Importancia:**  
Los reintentos y las reentregas del broker son habituales en sistemas distribuidos.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

## 17. Verificar estados inconsistentes

**Qué se prueba:**  
Comprobar que el estado de la reserva, el estado del asiento, el historial del usuario y la notificación permanezcan sincronizados tras una operación.

**Resultado esperado:**  
Para una reserva `Confirmada`, el asiento debe figurar como ocupado, la reserva debe aparecer en `GET /reservations/mine` con el mismo estado y debe existir exactamente una notificación. Para una reserva `Rechazada` o `Vencida`, el asiento debe figurar libre y no debe existir notificación.

**Problema que permite detectar:**  
Inconsistencias entre microservicios o bases de datos.

**Importancia:**  
Evita situaciones donde el sistema muestre información contradictoria.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

# D. Concurrencia

## 18. Dos usuarios reservando el mismo asiento simultáneamente

**Qué se prueba:**  
Enviar dos solicitudes de reserva para el mismo asiento al mismo tiempo, con `usuario1` y `usuario2`, de modo que las procesen las dos réplicas de Booking.

**Resultado esperado:**  
Solamente una solicitud debe alcanzar el estado **`Confirmada`**. La otra debe quedar **`Rechazada`** con motivo **`AsientoOcupado`**. Debe existir una sola reserva activa para ese asiento (lo garantiza el índice único parcial de la base de datos de Booking).

**Problema que permite detectar:**  
Condiciones de carrera entre las réplicas de Booking.

**Importancia:**  
Es fundamental en un sistema de reservas.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

## 19. Múltiples solicitudes simultáneas sobre un mismo asiento

**Qué se prueba:**  
Enviar varias solicitudes concurrentes (por ejemplo, 10 a 20) para reservar el mismo asiento, con distintos usuarios y repartidas entre las réplicas de Booking.

**Resultado esperado:**  
Exactamente una solicitud debe quedar **`Confirmada`** y todas las demás **`Rechazadas`** con motivo **`AsientoOcupado`**. No debe haber respuestas 5xx y debe generarse una sola notificación y un solo cobro.

**Problema que permite detectar:**  
Fallos de sincronización y problemas de concurrencia bajo alta competencia por un recurso.

**Importancia:**  
Permite evaluar el comportamiento bajo alta competencia por un recurso.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

## 20. Crear reservas simultáneas para diferentes asientos

**Qué se prueba:**  
Enviar múltiples reservas simultáneas sobre asientos diferentes del mismo evento.

**Resultado esperado:**  
Todas las operaciones independientes deben procesarse correctamente y alcanzar el estado **`Confirmada`**, sin rechazos por `AsientoOcupado` ni errores. Los mensajes deben repartirse entre las dos réplicas de Booking (consumidores competidores).

**Problema que permite detectar:**  
Bloqueos innecesarios o problemas de concurrencia general.

**Importancia:**  
Permite evaluar el comportamiento del sistema bajo carga concurrente.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

## 21. Repetir solicitudes concurrentes del mismo usuario

**Qué se prueba:**  
Enviar varias solicitudes simultáneas equivalentes (mismo usuario, mismo evento y mismo asiento), como ocurriría con múltiples clics.

**Resultado esperado:**  
Debe confirmarse una única reserva; las solicitudes restantes deben quedar **`Rechazadas`** con motivo **`AsientoOcupado`**. El asiento no debe quedar con más de una reserva activa y el usuario debe recibir una sola notificación.

**Problema que permite detectar:**  
Fallos de idempotencia y duplicación de operaciones.

**Importancia:**  
Permite detectar problemas producidos por múltiples clics, reintentos o solicitudes duplicadas.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

# E. Microservicios y tolerancia a fallos

## 22. Fallo del servicio encargado de reservas (Booking)

**Qué se prueba:**  
Detener Booking (`docker compose stop booking`) y probar los endpoints de Availability que dependen de él, y luego enviar una nueva solicitud de reserva.

**Resultado esperado:**  
Las consultas que dependen de Booking (`GET /events/{eventId}/seats`, `GET /reservations/{requestId}` y `GET /reservations/mine`) deben responder **503 Service Unavailable** de forma controlada, sin 500 ni asientos mostrados como libres por error. `GET /events` debe seguir funcionando. Un `POST /reservations` debe seguir respondiendo 202, porque el mensaje queda encolado en RabbitMQ hasta que Booking vuelva.

**Problema que permite detectar:**  
Fallos en el manejo de errores entre microservicios.

**Importancia:**  
Permite comprobar la resiliencia del sistema.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

## 23. Fallo de un servicio dependiente (Payment, Notifications y RabbitMQ)

**Qué se prueba:**  
Simular el fallo de cada dependencia de la operación, una por vez:

- **23a:** Detener Payment (`docker compose stop payment`) y crear una reserva.
- **23b:** Detener Notifications (`docker compose stop notifications`) y crear una reserva.
- **23c:** Detener RabbitMQ (`docker compose stop rabbitmq`) y crear una reserva.

**Resultado esperado:**  
En 23a, la reserva debe quedar **`Rechazada`** con motivo **`PagoNoDisponible`** y el asiento debe quedar libre.

En 23b, la reserva debe quedar igualmente **`Confirmada`**: la falla de Notifications no debe deshacer ni demorar la confirmación (degradación elegante) y solo debe registrarse una advertencia en el log.

En 23c, `POST /reservations` debe responder **503 Service Unavailable** de forma rápida (alrededor de 5 segundos como máximo) y no debe quedar ninguna reserva confirmada.

**Problema que permite detectar:**  
Problemas de comunicación entre microservicios y estados inconsistentes cuando falla una dependencia.

**Importancia:**  
Los servicios distribuidos deben contemplar la posibilidad de que una dependencia no esté disponible.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

## 24. Timeout de un microservicio

**Qué se prueba:**  
Simular una respuesta demasiado lenta de un servicio dependiente. Por ejemplo, pausar el contenedor de Payment (`docker compose pause payment`) mientras se procesa una reserva, y pausar Notifications (`docker compose pause notifications`) mientras se confirma otra.

**Resultado esperado:**  
Booking aplica un plazo máximo de 5 segundos al cobro por gRPC: al vencerlo, la reserva debe quedar **`Rechazada`** con motivo **`PagoNoDisponible`**. Notifications tiene un timeout de 3 segundos: al vencerlo, la reserva debe seguir **`Confirmada`**. En ambos casos no debe haber solicitudes colgadas indefinidamente.

**Problema que permite detectar:**  
Solicitudes bloqueadas, tiempos de respuesta excesivos o falta de manejo de timeout.

**Importancia:**  
Evita que una dependencia lenta afecte indefinidamente al sistema.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

## 25. Respuesta inválida de un servicio dependiente

**Qué se prueba:**  
Simular que un servicio dependiente o el broker entrega información inesperada o inválida:

- **25a:** Publicar en la cola `booking` (desde el panel de RabbitMQ) un mensaje con JSON ilegible.
- **25b:** Invocar a Payment con un `reservation_id` que no sea un GUID válido.

**Resultado esperado:**  
En 25a, el consumidor de Booking debe rechazar el mensaje sin reencolarlo y este debe aparecer en la cola de mensajes fallidos `booking.dead`; el consumidor debe seguir procesando mensajes normales. En 25b, Payment debe responder con un error gRPC `InvalidArgument` y no debe caerse.

**Problema que permite detectar:**  
Falta de validación de respuestas y mensajes entre servicios.

**Importancia:**  
Los microservicios deben validar la información recibida de sus dependencias.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

## 26. Recuperación después de un fallo

**Qué se prueba:**  
Comprobar el comportamiento del sistema después de que un servicio vuelva a estar disponible: reiniciar Booking (`docker compose start booking`) con solicitudes pendientes en la cola, y reiniciar Payment, Notifications y RabbitMQ.

**Resultado esperado:**  
Al volver Booking, debe procesar las solicitudes que quedaron encoladas durante la caída, sin duplicar reservas ni cobros. Si Booking cae a mitad de un procesamiento, el mensaje no confirmado vuelve a la cola y se procesa de nuevo sin duplicados. Las consultas de Availability deben volver a responder con normalidad y el consumidor de Booking debe reconectarse al broker.

**Problema que permite detectar:**  
Problemas de recuperación y manejo de reintentos.

**Importancia:**  
Permite evaluar la resiliencia del sistema frente a fallos temporales.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

# F. Seguridad y manejo de datos

## 27. Validación de autenticación, autorización y datos maliciosos

**Qué se prueba:**  
Comprobar el acceso al backend utilizando diferentes condiciones de autenticación y datos potencialmente maliciosos.

Entre los escenarios se incluyen:

- Solicitudes a `POST /reservations`, `GET /reservations/{requestId}` y `GET /reservations/mine` sin token.
- Tokens inválidos o con firma alterada, y tokens expirados.
- Intento de ver el resultado de una solicitud de otro usuario.
- Intento de reservar a nombre de otro usuario enviando un `userId` en el cuerpo.
- Llamadas directas a Booking, Payment o Notifications con un token de usuario (`seat-web`) o con el token de un servicio no autorizado (por ejemplo, `availability-service` sobre `POST /notifications`).
- Datos con caracteres especiales (inyección SQL, HTML/script) en los campos enviados.
- Acceso a los servicios internos (Payment) desde fuera de la red de Docker.

**Resultado esperado:**  
Availability debe responder **401 Unauthorized** ante la falta de token, un token inválido o un token expirado. Una solicitud ajena debe responder **404**, igual que una inexistente. El usuario de la reserva siempre debe salir del token, nunca del cuerpo.

Booking y Notifications deben responder **401/403** ante tokens que no correspondan al servicio permitido por su política (`AvailabilityOnly` y `BookingOnly`, respectivamente). Payment no debe ser accesible desde el exterior.

Las entradas maliciosas deben ser rechazadas o tratadas como datos, sin ejecutarse ni provocar errores 5xx.

**Problema que permite detectar:**  
Fallos de autenticación, autorización entre usuarios y entre servicios, o de validación de entradas.

**Importancia:**  
Las reservas contienen información que debe estar protegida y las operaciones deben ejecutarse únicamente cuando el usuario o el servicio tengan los permisos correspondientes.

**Resultado inicial:**  
> [PASS / FAIL / REVISAR]

**Observaciones / errores encontrados:**  
> [Completar]

**Corrección realizada:**  
> [Completar / No aplica]

**Re-test:**  
> [Completar / No fue necesario realizar un re-test]

**Resultado final:**  
> [PASS / FAIL / REVISAR]

**Observaciones finales:**  
> [Completar]

---

# Registro de errores y correcciones

Esta sección permite tener una vista general de los errores encontrados durante el testing.

| ID | Prueba | Error encontrado | Corrección | Re-test | Resultado final |
|---|---|---|---|---|---|
| BUG-001 | 2. Body vacío o JSON malformado y 3. Campos obligatorios ausentes | Se detectó que el endpoint POST /reservations no valida campos obligatorios; ante campos ausentes responde 404 en vez de 400 | Pendiente | Pendiente | REVISAR |

> Las pruebas que no presenten errores no necesitan aparecer en este registro.

---

# Resumen de resultados

| Bloque | Área | Cantidad de pruebas | PASS | FAIL | REVISAR |
|---|---|---:|---:|---:|---:|
| A | Contrato y validación de entrada | 8 | 6 |  | 2 |
| B | Reglas de negocio | 5 | 5 |  |  |
| C | Estados y flujo asincrónico | 4 | [ ] | [ ] | [ ] |
| D | Concurrencia | 4 | [ ] | [ ] | [ ] |
| E | Microservicios y tolerancia a fallos | 5 | [ ] | [ ] | [ ] |
| F | Seguridad y manejo de datos | 1 | [ ] | [ ] | [ ] |
| **Total** | | **27** | **11** | **[ ]** | **2** |
