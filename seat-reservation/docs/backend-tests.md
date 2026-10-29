# Documentación de Testing - Seat Reservation

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

**Observaciones finales:**  
> 

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

**Observaciones finales:**  
> El problema requiere una revisión.

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

**Observaciones finales:**  
> El problema requiere una revisión.

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

**Observaciones finales:**  
> 

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

**Observaciones finales:**  
> 

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

**Observaciones finales:**  
> 

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

**Observaciones finales:**  
> 

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

**Observaciones finales:**  
> 

---

# B. Reglas de negocio

## 9. Crear una reserva sobre un asiento disponible

**Qué se prueba:**  
Comprobar que una reserva pueda realizarse correctamente cuando el asiento se encuentra disponible.

**Resultado esperado:**  
La reserva debe crearse correctamente y el asiento debe quedar asociado a la reserva.

**Problema que permite detectar:**  
Fallos en la lógica principal de reservas.

**Importancia:**  
Es uno de los flujos principales del sistema.

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

## 10. Intentar reservar un asiento ya reservado

**Qué se prueba:**  
Intentar crear una segunda reserva para un asiento que ya fue reservado.

**Resultado esperado:**  
El sistema debe impedir la segunda reserva.

**Problema que permite detectar:**  
Fallas en las reglas de negocio que permiten reservas duplicadas.

**Importancia:**  
Evita que un mismo asiento sea asignado a más de una persona.

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

## 11. Reservar un asiento perteneciente a otro evento

**Qué se prueba:**  
Intentar utilizar un asiento que no corresponde al evento seleccionado.

**Resultado esperado:**  
La operación debe ser rechazada.

**Problema que permite detectar:**  
Inconsistencias entre las relaciones de eventos, asientos y reservas.

**Importancia:**  
Garantiza la integridad de los datos.

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

## 12. Cancelar una reserva válida

**Qué se prueba:**  
Cancelar una reserva existente.

**Resultado esperado:**  
La reserva debe cambiar al estado correspondiente y el asiento debe quedar disponible según las reglas del sistema.

**Problema que permite detectar:**  
Errores en la lógica de cancelación o actualización de estados.

**Importancia:**  
La cancelación forma parte del ciclo de vida de una reserva.

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

## 13. Cancelar una reserva inexistente

**Qué se prueba:**  
Intentar cancelar una reserva que no existe.

**Resultado esperado:**  
El backend debe rechazar la operación de manera controlada.

**Problema que permite detectar:**  
Manejo incorrecto de recursos inexistentes.

**Importancia:**  
Evita errores inesperados durante operaciones de cancelación.

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

## 14. Modificar una reserva que no corresponde al usuario

**Qué se prueba:**  
Intentar modificar una reserva perteneciente a otro usuario.

**Resultado esperado:**  
La operación debe ser rechazada.

**Problema que permite detectar:**  
Fallos en las reglas de autorización y propiedad de las reservas.

**Importancia:**  
Protege la integridad de las reservas de otros usuarios.

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

## 15. Realizar operaciones sobre una reserva en un estado no permitido

**Qué se prueba:**  
Intentar realizar una operación que no corresponde al estado actual de la reserva.

**Resultado esperado:**  
El sistema debe impedir la operación.

**Problema que permite detectar:**  
Transiciones de estado incorrectas.

**Importancia:**  
Garantiza que el ciclo de vida de una reserva respete las reglas del sistema.

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

## 16. Crear reservas con datos válidos pero inconsistentes

**Qué se prueba:**  
Enviar información individualmente válida pero que no sea consistente entre sí.

**Resultado esperado:**  
El backend debe validar también la coherencia entre los datos.

**Problema que permite detectar:**  
Validaciones únicamente a nivel de campo.

**Importancia:**  
Evita registros válidos sintácticamente pero incorrectos desde el punto de vista del negocio.

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

# C. Estados y flujo asincrónico

## 17. Consultar una reserva inmediatamente después de crearla

**Qué se prueba:**  
Crear una reserva y consultar su estado inmediatamente después.

**Resultado esperado:**  
El sistema debe devolver un estado coherente.

**Problema que permite detectar:**  
Problemas de sincronización entre servicios.

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

## 18. Consultar una reserva mientras se procesa

**Qué se prueba:**  
Consultar una reserva durante un proceso asincrónico.

**Resultado esperado:**  
El sistema debe devolver el estado actual sin generar inconsistencias.

**Problema que permite detectar:**  
Errores en el manejo de estados intermedios.

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

## 19. Reintentar una operación asincrónica

**Qué se prueba:**  
Repetir una solicitud mientras una operación anterior todavía está siendo procesada.

**Resultado esperado:**  
El sistema debe manejar correctamente el reintento sin generar datos duplicados o inconsistentes.

**Problema que permite detectar:**  
Problemas de idempotencia o procesamiento duplicado.

**Importancia:**  
Los reintentos son habituales en sistemas distribuidos.

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

## 20. Verificar estados inconsistentes

**Qué se prueba:**  
Comprobar que el estado de la reserva y el estado del asiento permanezcan sincronizados.

**Resultado esperado:**  
Ambos recursos deben reflejar correctamente la operación realizada.

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

## 21. Dos usuarios reservando el mismo asiento simultáneamente

**Qué se prueba:**  
Enviar dos solicitudes de reserva para el mismo asiento al mismo tiempo.

**Resultado esperado:**  
Solamente una solicitud debe poder completar la reserva.

**Problema que permite detectar:**  
Condiciones de carrera.

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

## 22. Múltiples solicitudes simultáneas sobre un mismo asiento

**Qué se prueba:**  
Enviar varias solicitudes concurrentes para reservar el mismo asiento.

**Resultado esperado:**  
El sistema debe permitir solamente la cantidad de reservas correspondiente a la disponibilidad real.

**Problema que permite detectar:**  
Fallos de sincronización y problemas de concurrencia.

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

## 23. Crear reservas simultáneas para diferentes asientos

**Qué se prueba:**  
Enviar múltiples reservas simultáneas sobre asientos diferentes.

**Resultado esperado:**  
Las operaciones independientes deberían procesarse correctamente.

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

## 24. Repetir solicitudes concurrentes del mismo usuario

**Qué se prueba:**  
Enviar varias solicitudes simultáneas equivalentes desde un mismo usuario.

**Resultado esperado:**  
El sistema debe evitar la creación de reservas duplicadas cuando corresponda.

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

## 25. Fallo del servicio encargado de reservas

**Qué se prueba:**  
Simular o provocar la indisponibilidad del servicio relacionado con las reservas.

**Resultado esperado:**  
El sistema debe responder de forma controlada.

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

## 26. Fallo de un servicio dependiente

**Qué se prueba:**  
Simular un fallo en uno de los servicios de los que depende la operación.

**Resultado esperado:**  
El backend debe manejar correctamente la falla y evitar estados inconsistentes.

**Problema que permite detectar:**  
Problemas de comunicación entre microservicios.

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

## 27. Timeout de un microservicio

**Qué se prueba:**  
Simular una respuesta demasiado lenta de un servicio dependiente.

**Resultado esperado:**  
El backend debe aplicar el comportamiento definido para timeouts.

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

## 28. Respuesta inválida de un servicio dependiente

**Qué se prueba:**  
Simular que un servicio dependiente devuelve una respuesta inesperada o inválida.

**Resultado esperado:**  
El sistema debe manejar la respuesta sin producir errores no controlados.

**Problema que permite detectar:**  
Falta de validación de respuestas entre servicios.

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

## 29. Recuperación después de un fallo

**Qué se prueba:**  
Comprobar el comportamiento del sistema después de que un servicio vuelva a estar disponible.

**Resultado esperado:**  
El sistema debe recuperar su funcionamiento correctamente y no generar datos duplicados o inconsistentes.

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

## 30. Validación de autenticación, autorización y datos maliciosos

**Qué se prueba:**  
Comprobar el acceso al backend utilizando diferentes condiciones de autenticación y datos potencialmente maliciosos.

Entre los escenarios se incluyen:

- Solicitudes sin autenticación.
- Tokens inválidos.
- Tokens expirados.
- Acceso a recursos no pertenecientes al usuario.
- Datos con caracteres especiales.
- Entradas diseñadas para comprobar el correcto tratamiento de información potencialmente peligrosa.

**Resultado esperado:**  
El backend debe rechazar accesos no autorizados y tratar las entradas de forma segura.

**Problema que permite detectar:**  
Fallos de autenticación, autorización o validación de entradas.

**Importancia:**  
Las reservas contienen información que debe estar protegida y las operaciones deben ejecutarse únicamente cuando el usuario tenga los permisos correspondientes.

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
| B | Reglas de negocio | 8 | [ ] | [ ] | [ ] |
| C | Estados y flujo asincrónico | 4 | [ ] | [ ] | [ ] |
| D | Concurrencia | 4 | [ ] | [ ] | [ ] |
| E | Microservicios y tolerancia a fallos | 5 | [ ] | [ ] | [ ] |
| F | Seguridad y manejo de datos | 1 | [ ] | [ ] | [ ] |
| **Total** | | **30** | **6** | **[ ]** | **2** |
