# Pruebas del frontend — Sistema de reserva de asientos

## 1. Objetivo

Verificar el funcionamiento de la interfaz web del sistema de reserva de asientos y su integración con los servicios de Availability, Booking y Keycloak.

Las pruebas abarcarán navegación, visualización de eventos, selección de asientos, autenticación, solicitud de reservas y consulta de resultados.

## 2. Entorno de pruebas

- **Aplicación:** frontend desarrollado con React, TypeScript y Vite.
- **Backend:** microservicios ejecutados mediante Docker Compose.
- **Autenticación:** Keycloak.
- **Mensajería:** RabbitMQ local.
- **Navegador:** pendiente de registrar.
- **Fecha de ejecución:** pendiente.
- **Commit probado:** pendiente de registrar.
- **Responsable:** Carla Andrea Colina Sosa.

**Estado inicial:** pruebas pendientes de ejecución. Al preparar este documento, el frontend todavía no compila debido a componentes faltantes que están siendo desarrollados por otro integrante.

## 3. Bloque A — Navegación y visualización de eventos

### FRONT-01 — Acceso a la página principal

**Objetivo:** verificar que la aplicación cargue correctamente.

**Procedimiento:**

1. Iniciar el frontend.
2. Abrir su dirección local desde el navegador.

**Resultado esperado:** se muestra la página principal sin errores de carga.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

### FRONT-02 — Listado de eventos

**Objetivo:** comprobar que se visualicen los eventos disponibles.

**Procedimiento:**

1. Ingresar a la página principal.
2. Observar los eventos mostrados.

**Resultado esperado:** se muestran los eventos obtenidos desde Availability con sus datos correspondientes.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

### FRONT-03 — Selección de un evento

**Objetivo:** verificar la navegación desde un evento hasta sus asientos.

**Procedimiento:**

1. Ingresar al listado de eventos.
2. Seleccionar uno de ellos.

**Resultado esperado:** se abre la pantalla de asientos correspondiente al evento seleccionado.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

### FRONT-04 — Navegación a una ruta inexistente

**Objetivo:** comprobar el comportamiento de la aplicación ante una dirección no reconocida.

**Procedimiento:**

1. Ingresar una ruta inexistente dentro de la aplicación.

**Resultado esperado:** se muestra el mensaje «Página no encontrada».

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

## 4. Bloque B — Visualización y selección de asientos

### FRONT-05 — Visualización de la grilla

**Objetivo:** verificar la presentación de los asientos del evento.

**Procedimiento:**

1. Abrir un evento con asientos.
2. Observar su distribución.

**Resultado esperado:** los asientos se muestran agrupados por filas y ordenados numéricamente.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

### FRONT-06 — Identificación de asientos libres y ocupados

**Objetivo:** comprobar que la interfaz represente correctamente el estado de cada asiento.

**Procedimiento:**

1. Abrir un evento que tenga asientos libres y ocupados.
2. Comparar los estados mostrados con los datos obtenidos de Availability.

**Resultado esperado:** los asientos cuyo campo `occupied` sea `true` aparecen como ocupados y los demás como libres.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

### FRONT-07 — Selección de un asiento libre

**Objetivo:** comprobar que el usuario pueda elegir un asiento disponible.

**Procedimiento:**

1. Abrir un evento.
2. Seleccionar un asiento libre.

**Resultado esperado:** el asiento cambia al estado seleccionado y aparece la opción de reservarlo.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

### FRONT-08 — Intento de seleccionar un asiento ocupado

**Objetivo:** verificar que un asiento ocupado no pueda seleccionarse para reservar.

**Procedimiento:**

1. Abrir un evento con asientos ocupados.
2. Intentar seleccionar uno de ellos.

**Resultado esperado:** el asiento ocupado no puede seleccionarse ni utilizarse para iniciar una reserva.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

### FRONT-09 — Cambio del asiento seleccionado

**Objetivo:** comprobar el comportamiento al cambiar de selección.

**Procedimiento:**

1. Seleccionar un asiento libre.
2. Seleccionar otro asiento libre.

**Resultado esperado:** solamente el segundo asiento permanece seleccionado.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

## 5. Bloque C — Autenticación

### FRONT-10 — Intento de reservar sin iniciar sesión

**Objetivo:** verificar que se solicite autenticación antes de reservar.

**Procedimiento:**

1. Acceder a la aplicación sin iniciar sesión.
2. Seleccionar un asiento libre.
3. Presionar «Ingresar para reservar».

**Resultado esperado:** el usuario es redirigido a Keycloak para autenticarse.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

### FRONT-11 — Inicio de sesión y regreso a la aplicación

**Objetivo:** comprobar la continuidad de la navegación después de autenticarse.

**Procedimiento:**

1. Iniciar una reserva sin estar autenticado.
2. Completar el inicio de sesión en Keycloak.

**Resultado esperado:** el usuario regresa a la aplicación autenticado y puede continuar el proceso de reserva.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

## 6. Bloque D — Solicitud y seguimiento de reservas

### FRONT-12 — Solicitud de reserva de un asiento libre

**Objetivo:** verificar el envío de una solicitud válida desde la interfaz.

**Procedimiento:**

1. Iniciar sesión.
2. Seleccionar un asiento libre.
3. Presionar «Reservar».

**Resultado esperado:** la aplicación envía la solicitud a Availability y, al obtener un `requestId`, navega a la pantalla de seguimiento de la reserva.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

### FRONT-13 — Prevención de envíos repetidos

**Objetivo:** comprobar que la interfaz evite solicitudes duplicadas mientras se procesa una reserva.

**Procedimiento:**

1. Seleccionar un asiento libre.
2. Presionar «Reservar».
3. Intentar presionar nuevamente el botón durante el envío.

**Resultado esperado:** el botón permanece deshabilitado mientras se envía la solicitud.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

### FRONT-14 — Visualización del estado de reserva

**Objetivo:** comprobar que la interfaz muestre el resultado de una solicitud.

**Procedimiento:**

1. Realizar una solicitud de reserva.
2. Acceder a la pantalla correspondiente al `requestId`.
3. Observar el estado presentado.

**Resultado esperado:** se muestra el estado devuelto por el sistema de forma comprensible para el usuario.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

## 7. Bloque E — Manejo de errores

### FRONT-15 — Evento inexistente

**Objetivo:** comprobar el tratamiento de un evento que no existe.

**Procedimiento:**

1. Ingresar a una ruta de evento con un identificador UUID válido pero inexistente.

**Resultado esperado:** la aplicación muestra «El evento no existe» cuando Availability responde HTTP 404.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

### FRONT-16 — Availability no disponible

**Objetivo:** verificar el comportamiento de la interfaz cuando no puede consultar los asientos.

**Procedimiento:**

1. Preparar una situación controlada en la que Availability no responda.
2. Abrir la pantalla de asientos.

**Resultado esperado:** se muestra un mensaje de error comprensible y la aplicación no queda bloqueada indefinidamente.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

### FRONT-17 — Error al solicitar una reserva

**Objetivo:** comprobar que la interfaz maneje correctamente el fallo de una solicitud.

**Procedimiento:**

1. Iniciar sesión y seleccionar un asiento libre.
2. Provocar o reproducir de forma controlada un error al enviar la reserva.
3. Observar el comportamiento de la interfaz.

**Resultado esperado:** se informa el error al usuario y no se muestra falsamente una reserva confirmada.

**Resultado obtenido:** pendiente.

**Estado:** PENDIENTE.

## 8. Resumen de resultados

| Bloque                      | Casos    | Aprobados  | Fallidos   | Pendientes  |
| --------------------------- | -------- | ---------- | ---------- | ----------- |
| A — Navegación y eventos    | 4        | 0          | 0          | 4           |
| B — Asientos                | 5        | 0          | 0          | 5           |
| C — Autenticación           | 2        | 0          | 0          | 2           |
| D — Reservas                | 3        | 0          | 0          | 3           |
| E — Errores                 | 3        | 0          | 0          | 3           |
| --------------------------- | -------- | ---------- | ---------- | ----------- |
| **Total**                   | **17**   | **0**      | **0**      | **17**      |

## 9. Observaciones

- Los casos fueron preparados a partir de la estructura y del código disponible del frontend.
- Los resultados deberán completarse exclusivamente después de ejecutar cada prueba.
- Las pruebas que requieran detener servicios deberán realizarse de forma controlada en el entorno local.
- No se duplicarán las pruebas internas de los microservicios documentadas por el responsable del backend.
- La ejecución comenzará cuando el frontend esté completo y compile correctamente.

## 10. Conclusión

La planificación comprende 17 casos de prueba funcionales del frontend, distribuidos en cinco bloques.

Al momento de elaborar el documento, todos los casos permanecen pendientes de ejecución. No se registran funcionalidades como aprobadas ni fallidas sin haberlas probado.
