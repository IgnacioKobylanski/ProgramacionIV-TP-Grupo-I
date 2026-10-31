# Pruebas del frontend — Sistema de reserva de asientos

## 1. Objetivo

Verificar el funcionamiento de la interfaz web del sistema de reserva de asientos y su integración con Availability, Booking, Payment y Keycloak. Evaluar navegación, visualización de eventos y asientos, autenticación, solicitud y seguimiento de reservas, historial por usuario, errores y comportamiento con varias sesiones.

## 2. Entorno de pruebas

- **Aplicación:** React, TypeScript y Vite; ejecución local en `http://localhost:5173`.
- **Backend:** microservicios ejecutados con Docker Compose.
- **Autenticación:** Keycloak local (`seat-reservation`), con clientes `seat-web`, `availability-service` y `booking-service`.
- **Mensajería:** RabbitMQ local.
- **Navegador:** Google Chrome, sesión normal y ventana de incógnito.
- **Fecha de ejecución:** 31 de octubre de 2026 (pruebas descritas en esta sesión).
- **Commit probado:** no registrado en la evidencia; completar con `git rev-parse --short HEAD` en la copia probada.
- **Responsable:** Carla Andrea Colina Sosa.
- **Alcance:** pruebas manuales del frontend en entorno local. No reemplazan pruebas de carga, seguridad del backend ni pruebas automatizadas de concurrencia.

**Antecedente:** el plan original comprendía 17 casos. Tras completar el flujo principal se ampliaron las pruebas hasta FRONT-35, especialmente para cuentas distintas y consultas simultáneas. Los estados detallados reflejan la evidencia efectivamente observada, sin dar por verificadas condiciones que no se midieron.

## 3. Bloque A — Navegación y visualización de eventos

### FRONT-01 — Acceso a la página principal

**Objetivo:** Verificar que la aplicación cargue correctamente.

**Procedimiento:** Iniciar Vite; abrir http://localhost:5173.

**Resultado esperado:** Se muestra la página principal sin errores.

**Resultado obtenido:** La página principal cargó correctamente.

**Estado:** APROBADA.

### FRONT-02 — Listado de eventos

**Objetivo:** Comprobar la visualización de los eventos disponibles.

**Procedimiento:** Entrar a la página principal; observar los eventos.

**Resultado esperado:** Se muestran eventos y sus datos.

**Resultado obtenido:** Se visualizó el listado de eventos con los botones «Ver asientos».

**Estado:** APROBADA.

### FRONT-03 — Selección de un evento

**Objetivo:** Verificar la navegación desde el evento hasta sus asientos.

**Procedimiento:** Seleccionar «Ver asientos» en un evento.

**Resultado esperado:** Se abre la pantalla de asientos del evento seleccionado.

**Resultado obtenido:** Se abrió correctamente la pantalla de asientos. El primer intento estuvo bloqueado por un HTTP 503, resuelto al sincronizar el secreto local de availability-service.

**Estado:** APROBADA.

### FRONT-04 — Navegación a una ruta inexistente

**Objetivo:** Comprobar la respuesta ante rutas desconocidas.

**Procedimiento:** Ingresar una ruta inexistente.

**Resultado esperado:** Se muestra «Página no encontrada».

**Resultado obtenido:** Se mostró «Página no encontrada».

**Estado:** APROBADA.

## 4. Bloque B — Visualización y selección de asientos

### FRONT-05 — Visualización de la grilla

**Objetivo:** Verificar la presentación de asientos.

**Procedimiento:** Abrir un evento; observar las filas y asientos.

**Resultado esperado:** Los asientos se muestran agrupados por filas y ordenados numéricamente.

**Resultado obtenido:** La grilla se mostró correctamente y permitió reconocer asientos por fila y número.

**Estado:** APROBADA CON ALCANCE.

**Alcance / observación:** Se comprobó la visualización; no se registró una comprobación exhaustiva del orden de todas las filas.

### FRONT-06 — Identificación de asientos libres y ocupados

**Objetivo:** Comprobar que el frontend refleje el estado de Availability.

**Procedimiento:** Abrir el evento; inspeccionar Network > seats > Response; comparar con la grilla.

**Resultado esperado:** Los asientos con occupied=true figuran ocupados y el resto, disponibles.

**Resultado obtenido:** La solicitud seats respondió HTTP 200. El asiento reservado tenía occupied=true y aparecía bloqueado en la grilla.

**Estado:** APROBADA CON ALCANCE.

**Alcance / observación:** La comparación explícita con la API se hizo sobre el asiento reservado; no se auditó asiento por asiento.

### FRONT-07 — Selección de un asiento libre

**Objetivo:** Comprobar que pueda seleccionarse un asiento disponible.

**Procedimiento:** Abrir un evento; seleccionar un asiento libre.

**Resultado esperado:** Se señala la selección y se habilita la acción de reservar.

**Resultado obtenido:** Permitió elegir un asiento y mostró la opción «Reservar».

**Estado:** APROBADA.

### FRONT-08 — Intento de seleccionar un asiento ocupado

**Objetivo:** Verificar que un asiento ocupado no pueda elegirse.

**Procedimiento:** Intentar hacer clic en un asiento reservado.

**Resultado esperado:** No se permite seleccionarlo para reservar.

**Resultado obtenido:** El cursor mostró el símbolo de prohibido y el asiento no pudo seleccionarse.

**Estado:** APROBADA.

### FRONT-09 — Cambio del asiento seleccionado

**Objetivo:** Comprobar la selección única.

**Procedimiento:** Seleccionar un asiento libre; hacer clic en otro.

**Resultado esperado:** Solo el último asiento elegido permanece seleccionado.

**Resultado obtenido:** El primer asiento se desmarcó y permaneció seleccionado el último.

**Estado:** APROBADA.

## 5. Bloque C — Autenticación

### FRONT-10 — Intento de reservar sin iniciar sesión

**Objetivo:** Verificar que se exija autenticación.

**Procedimiento:** Sin sesión, seleccionar asiento; pulsar «Ingresar para reservar».

**Resultado esperado:** Se presenta el inicio de sesión de Keycloak.

**Resultado obtenido:** Apareció «Ingresar para reservar» y se abrió Keycloak. Inicialmente hubo redirect_uri inválido; se corrigió la configuración local de seat-web.

**Estado:** APROBADA.

### FRONT-11 — Inicio de sesión y regreso a la aplicación

**Objetivo:** Verificar la navegación posterior a la autenticación.

**Procedimiento:** Iniciar reserva sin sesión; iniciar sesión con un usuario de prueba.

**Resultado esperado:** Regresa autenticado y puede continuar la reserva.

**Resultado obtenido:** Se inició sesión exitosamente y se pudo continuar con la reserva.

**Estado:** APROBADA.

## 6. Bloque D — Solicitud y seguimiento de reservas

### FRONT-12 — Solicitud de reserva de un asiento libre

**Objetivo:** Verificar el envío de solicitud y seguimiento.

**Procedimiento:** Iniciar sesión; elegir un asiento; pulsar «Reservar».

**Resultado esperado:** Se envía la solicitud y se navega a /reservations/{identificador}.

**Resultado obtenido:** Se abrió una URL /reservations/ seguida de un identificador; la operación finalizó confirmada.

**Estado:** APROBADA.

### FRONT-13 — Prevención de envíos repetidos

**Objetivo:** Comprobar que la interfaz bloquee el botón durante el envío.

**Procedimiento:** Seleccionar un asiento; pulsar «Reservar» una sola vez; observar el botón.

**Resultado esperado:** El botón queda deshabilitado mientras se envía.

**Resultado obtenido:** El botón se inhabilitó al iniciar la solicitud y se abrió el seguimiento.

**Estado:** APROBADA CON ALCANCE.

**Alcance / observación:** No se provocó un doble clic ni se verificó idempotencia del backend.

### FRONT-14 — Visualización del estado de reserva

**Objetivo:** Comprobar que se muestre el resultado de la operación.

**Procedimiento:** Reservar y observar la pantalla de seguimiento.

**Resultado esperado:** Se presenta el estado de modo comprensible.

**Resultado obtenido:** Se mostró procesamiento temporal y luego «Confirmada»; la pantalla consulta el estado periódicamente.

**Estado:** APROBADA.

## 7. Bloque E — Manejo de errores

### FRONT-15 — Evento inexistente

**Objetivo:** Verificar el manejo de un evento que no existe.

**Procedimiento:** Ingresar la ruta de un evento con UUID válido pero inexistente.

**Resultado esperado:** Se informa que el evento no existe ante HTTP 404.

**Resultado obtenido:** La API devolvió HTTP 404 y la interfaz mostró «No encontramos lo que buscabas».

**Estado:** APROBADA.

### FRONT-16 — Availability no disponible

**Objetivo:** Verificar el error ante caída temporal del servicio.

**Procedimiento:** En entorno local, detener availability; abrir asientos y recargar; restaurar servicio.

**Resultado esperado:** Aparece un error comprensible; la página no queda cargando indefinidamente.

**Resultado obtenido:** Se mostró «El servicio no está disponible en este momento».

**Estado:** APROBADA.

**Alcance / observación:** Se indicó restaurar el servicio con docker compose start availability; verificar que esté operativo antes de futuras pruebas.

### FRONT-17 — Error al solicitar una reserva

**Objetivo:** Comprobar el tratamiento visible de una solicitud fallida.

**Procedimiento:** Intentar una reserva durante una falla controlada o previamente observada.

**Resultado esperado:** Se informa el rechazo sin mostrar una confirmación falsa.

**Resultado obtenido:** Se mostró «La reserva fue rechazada» y «El servicio de pago no está disponible»; estado «Rechazada», con etapas Recibida, Asiento retenido y Rechazada. Los logs de Booking registraron PagoNoDisponible.

**Estado:** APROBADA.

## 8. Bloque F — Usuarios, historial y persistencia

### FRONT-18 — Persistencia de asientos ocupados entre usuarios

**Objetivo:** Comprobar que una reserva afecte la disponibilidad compartida.

**Procedimiento:** Usuario 1 reserva; usuario 2 abre el mismo evento.

**Resultado esperado:** El asiento permanece ocupado e inhabilitado para el segundo usuario.

**Resultado obtenido:** El usuario 2 vio ocupado el asiento del usuario 1 y no pudo seleccionarlo.

**Estado:** APROBADA.

### FRONT-19 — Consulta de reservas propias

**Objetivo:** Comprobar la vista «Mis reservas».

**Procedimiento:** Usuario 2 consulta sin reservas; realiza una reserva; regresa al historial.

**Resultado esperado:** Se muestra estado vacío inicialmente y después la reserva propia.

**Resultado obtenido:** Mostró «Todavía no tiene reservas» antes de reservar y luego el asiento confirmado con opción «Ver más detalles».

**Estado:** APROBADA.

### FRONT-20 — Separación de historiales por usuario

**Objetivo:** Verificar que cada usuario vea solo sus reservas en la lista.

**Procedimiento:** Alternar las sesiones de usuarios 1 y 2; consultar «Mis reservas».

**Resultado esperado:** Las reservas del usuario 2 no aparecen en el listado del usuario 1 y viceversa.

**Resultado obtenido:** El listado del usuario 1 mostró solo sus reservas; el usuario 2 vio las suyas.

**Estado:** APROBADA CON ALCANCE.

**Alcance / observación:** La restricción de acceso directo se probó por separado en FRONT-34.

### FRONT-21 — Historial de reservas confirmadas

**Objetivo:** Comprobar el registro de confirmaciones.

**Procedimiento:** Realizar reserva confirmada; abrir «Mis reservas».

**Resultado esperado:** Se muestra la reserva con estado «Confirmada».

**Resultado obtenido:** El historial mostró la reserva confirmada, con evento, fecha, hora, asiento y estado.

**Estado:** APROBADA.

### FRONT-22 — Historial de reservas rechazadas

**Objetivo:** Comprobar la conservación de operaciones rechazadas.

**Procedimiento:** Consultar la reserva rechazada generada por falta de pago.

**Resultado esperado:** El rechazo se conserva e indica estado y motivo.

**Resultado obtenido:** Se recuperó la reserva rechazada del asiento B9; figuró «El servicio de pago no está disponible», «Rechazada» y el número de solicitud.

**Estado:** APROBADA.

### FRONT-23 — Persistencia del historial tras cerrar sesión

**Objetivo:** Verificar continuidad de las reservas registradas.

**Procedimiento:** Cerrar sesión, ingresar con la otra cuenta, volver a la primera y revisar sus reservas.

**Resultado esperado:** Cada cuenta conserva sus reservas y estados.

**Resultado obtenido:** Los historiales persistieron al alternar las cuentas y volver a iniciar sesión.

**Estado:** APROBADA.

### FRONT-24 — Consistencia entre evento e historial

**Objetivo:** Verificar coincidencia de datos de reservas.

**Procedimiento:** Comparar el evento original con la información de «Mis reservas».

**Resultado esperado:** Nombre, fecha, hora, asiento y estado corresponden a la operación.

**Resultado obtenido:** Se verificó coincidencia del nombre, fecha y hora del evento. El listado muestra la información principal; la vista de detalles contiene menos contexto.

**Estado:** APROBADA CON OBSERVACIÓN.

**Alcance / observación:** Mejora de usabilidad: «Ver más detalles» debería incluir nombre, fecha y hora del evento.

## 9. Bloque G — Sesiones simultáneas y concurrencia

### FRONT-25 — Dos usuarios consultan el mismo evento

**Objetivo:** Verificar la coherencia inicial entre sesiones simultáneas.

**Procedimiento:** Abrir Chrome normal con usuario 1 e incógnito con usuario 2, en el mismo evento.

**Resultado esperado:** Ambos ven la misma disponibilidad inicial.

**Resultado obtenido:** Ambos visualizaron los mismos asientos disponibles al iniciar la comparación.

**Estado:** APROBADA.

### FRONT-26 — Actualización automática de disponibilidad

**Objetivo:** Comprobar si otra sesión refleja una nueva reserva sin recargar.

**Procedimiento:** Mantener abierta la grilla del usuario 2; usuario 1 confirma una reserva; observar sin actualizar.

**Resultado esperado:** Si existe actualización automática requerida, el asiento cambia a ocupado sin intervención.

**Resultado obtenido:** El asiento continuó apareciendo disponible en la ventana del usuario 2 hasta usar «Actualizar».

**Estado:** OBSERVACIÓN / REQUISITO A CONFIRMAR.

**Alcance / observación:** No se comprobó actualización automática. Aclarar con el equipo si se exige tiempo real, polling o solo actualización manual.

### FRONT-27 — Dos usuarios intentan reservar el mismo asiento

**Objetivo:** Comprobar exclusividad.

**Procedimiento:** Usuario 1 reserva B3; usuario 2, con vista desactualizada, intenta reservar B3.

**Resultado esperado:** Solo se confirma una reserva para ese asiento.

**Resultado obtenido:** La reserva del primer usuario quedó confirmada; la del segundo se rechazó con «Otro usuario reservó ese asiento».

**Estado:** APROBADA.

### FRONT-28 — Mensaje de rechazo por asiento ocupado

**Objetivo:** Comprobar que el conflicto de disponibilidad sea comprensible.

**Procedimiento:** Usar la solicitud rechazada del usuario 2 al intentar reservar B3.

**Resultado esperado:** La interfaz muestra rechazo y explicación.

**Resultado obtenido:** Mostró «La reserva fue rechazada», «Otro usuario reservó ese asiento», asiento B3 y estado «Rechazada».

**Estado:** APROBADA.

### FRONT-29 — Reservas cercanas en el tiempo para asientos diferentes

**Objetivo:** Verificar que dos usuarios puedan reservar asientos distintos sin interferir.

**Procedimiento:** Seleccionar dos asientos distintos en sesiones separadas; enviar las solicitudes con clics muy próximos.

**Resultado esperado:** Ambas reservas pueden confirmarse.

**Resultado obtenido:** Las dos reservas se confirmaron en el orden de los clics.

**Estado:** APROBADA CON ALCANCE.

**Alcance / observación:** No se trató de concurrencia estrictamente simultánea; fue una prueba de solicitudes sucesivas cercanas.

### FRONT-30 — Asiento seleccionado que otro usuario reserva

**Objetivo:** Observar qué ocurre con una selección desactualizada.

**Procedimiento:** Seleccionar el mismo asiento en ambas sesiones; usuario 1 lo reserva; observar usuario 2 sin recargar.

**Resultado esperado:** La interfaz debería reflejar el cambio, si se requiere sincronización automática; en todo caso, impedir confirmación duplicada.

**Resultado obtenido:** El asiento permaneció seleccionado en usuario 2 hasta presionar «Actualizar»; luego apareció bloqueado.

**Estado:** OBSERVACIÓN / REQUISITO A CONFIRMAR.

**Alcance / observación:** Se relaciona con FRONT-26. La exclusividad del backend se verificó en FRONT-27, no se volvió a enviar aquí.

### FRONT-31 — Recarga durante el procesamiento

**Objetivo:** Comprobar continuidad del seguimiento al actualizar.

**Procedimiento:** Crear una reserva; en /reservations/{id}, presionar F5 durante «Procesando».

**Resultado esperado:** La pantalla retoma el mismo seguimiento sin perder la operación.

**Resultado obtenido:** Tras F5, continuó el seguimiento hasta el estado «Confirmada».

**Estado:** APROBADA CON ALCANCE.

**Alcance / observación:** No se cotejó el número de solicitudes persistidas para demostrar ausencia absoluta de duplicados.

### FRONT-32 — Consulta simultánea de historiales

**Objetivo:** Verificar que cada sesión pueda consultar «Mis reservas».

**Procedimiento:** Abrir «Mis reservas» en ambas cuentas al mismo tiempo.

**Resultado esperado:** Cada sesión muestra su historial propio.

**Resultado obtenido:** Las dos sesiones mostraron sus respectivos historiales correctamente.

**Estado:** APROBADA.

## 10. Bloque H — Acceso protegido a reservas

### FRONT-33 — Acceso a «Mis reservas» sin iniciar sesión

**Objetivo:** Verificar protección de la vista privada.

**Procedimiento:** Abrir «Mis reservas» sin autenticación.

**Resultado esperado:** No se muestra un historial; se solicita iniciar sesión.

**Resultado obtenido:** Se mostró «Tenés que iniciar sesión para ver tus reservas».

**Estado:** APROBADA.

### FRONT-34 — Acceso directo a una reserva ajena

**Objetivo:** Comprobar que conocer la URL no permita ver información de otra cuenta.

**Procedimiento:** Abrir desde usuario 2 la URL /reservations/{id} de una reserva del usuario 1.

**Resultado esperado:** No se revelan detalles de la reserva ajena.

**Resultado obtenido:** Se mostró «No encontramos lo que buscabas» y no se exhibieron los datos privados.

**Estado:** APROBADA CON ALCANCE.

**Alcance / observación:** Resultado validado desde el frontend; no sustituye una auditoría de autorización directa de API.

### FRONT-35 — Acceso directo a una reserva sin autenticación

**Objetivo:** Verificar protección de detalles por URL.

**Procedimiento:** En una sesión sin login, abrir la URL de una reserva existente.

**Resultado esperado:** Se pide autenticación y no se muestran los detalles privados.

**Resultado obtenido:** Apareció «Tenés que iniciar sesión para ver esto» y el botón «Ingresar».

**Estado:** APROBADA CON ALCANCE.

**Alcance / observación:** Validación de comportamiento de interfaz; no se realizó una auditoría de seguridad del backend.

## 11. Resumen de resultados

| Bloque                                    |  Casos | Aprobadas | Aprobadas con alcance / observación | Observaciones pendientes de requisito |
| ----------------------------------------- | -----: | --------: | ----------------------------------: | ------------------------------------: |
| A — Navegación y visualización de eventos |      4 |         4 |                                   0 |                                     0 |
| B — Visualización y selección de asientos |      5 |         3 |                                   2 |                                     0 |
| C — Autenticación                         |      2 |         2 |                                   0 |                                     0 |
| D — Solicitud y seguimiento de reservas   |      3 |         2 |                                   1 |                                     0 |
| E — Manejo de errores                     |      3 |         3 |                                   0 |                                     0 |
| F — Usuarios, historial y persistencia    |      7 |         5 |                                   2 |                                     0 |
| G — Sesiones simultáneas y concurrencia   |      8 |         4 |                                   2 |                                     2 |
| H — Acceso protegido a reservas           |      3 |         1 |                                   2 |                                     0 |
| **Total**                                 | **35** |    **24** |                               **9** |                                 **2** |

**Lectura de los estados:** «Aprobada» implica evidencia funcional directa para el criterio observado; «Aprobada con alcance» reconoce condiciones no verificadas exhaustivamente; «Observación / requisito a confirmar» señala un comportamiento real cuyo carácter obligatorio depende de la especificación del equipo. Por ello, **no corresponde afirmar que las 35 pruebas quedaron aprobadas sin observaciones**.

## 12. Incidencias detectadas y resolución en el entorno local

### INC-01 — HTTP 503 al consultar asientos

**Síntoma:** al abrir un evento, la grilla devolvía un error HTTP 503. **Evidencia:** Availability no conseguía un token de Keycloak; los logs registraban HTTP 401 e `invalid_client_credentials` para `availability-service`. **Causa identificada:** el secreto persistido en Keycloak local difería del configurado en Docker Compose y el archivo de importación del realm. **Acción:** sincronizar el secreto del cliente local mediante `kcadm.sh update ... --merge`, sin eliminar volúmenes. **Resultado:** la grilla comenzó a cargar con normalidad.

### INC-02 — `Invalid parameter: redirect_uri`

**Síntoma:** al elegir «Ingresar para reservar», Keycloak rechazaba la redirección. **Evidencia:** `seat-web` autorizaba `http://localhost:5001/*`, mientras Vite estaba en `http://localhost:5173`. **Acción:** incorporar `http://localhost:5173/*` a los redirect URIs y `http://localhost:5173` a Web Origins de `seat-web`, manteniendo los valores existentes. **Resultado:** se abrió correctamente el login y se pudo iniciar sesión.

### INC-03 — Reserva rechazada por pago no disponible

**Síntoma:** la pantalla informó «La reserva fue rechazada» / «El servicio de pago no está disponible». **Evidencia:** Booking registró HTTP 401 al pedir un token para la comunicación con Payment; auditoría `Resultado=Rechazada Motivo=PagoNoDisponible`. **Acción:** sincronizar el secreto local de `booking-service` con Docker Compose. **Resultado:** se pudieron confirmar reservas posteriores. **Valor de prueba:** la solicitud rechazada quedó registrada con estado y motivo, sin presentarse como confirmada.

**Precaución:** los ajustes se hicieron en la instancia local de Keycloak; un realm persistente puede conservar valores diferentes del JSON importado. No se eliminó el volumen ni se modificó el código del equipo por estas incidencias. No publicar contraseñas, tokens ni secretos reales en este documento.

## 13. Hallazgos y recomendaciones

1. **Disponibilidad sin actualización automática entre sesiones (FRONT-26):** cuando otro usuario reserva un asiento, la grilla abierta permanece desactualizada hasta pulsar «Actualizar». Recomendar actualización periódica, notificación en tiempo real o señalización de datos posiblemente desactualizados, según el alcance acordado.
2. **Selección desactualizada (FRONT-30):** un asiento previamente seleccionado puede permanecer marcado después de haber sido reservado por otro usuario. Recomendar limpiar o invalidar la selección al actualizar disponibilidad, y mantener el control definitivo de exclusividad en el backend.
3. **Exclusividad correcta en el caso probado:** Booking rechazó un segundo intento sobre B3 y mostró «Otro usuario reservó ese asiento». Conservar esta validación del lado del servidor.
4. **Vista de detalles menos informativa:** «Mis reservas» sí muestra nombre, fecha y hora del evento, asiento y estado; la vista «Ver más detalles» mostró asiento, estado y número de solicitud, pero no repitió toda la información del evento. Mejora de usabilidad, no fallo del listado.
5. **Filtros de historial:** se observó el botón «Todas» como opción disponible. No se confirmó que filtros «Confirmadas» o «Rechazadas» estén implementados ni sean requisito; aclararlo con el equipo antes de clasificarlo como defecto.
6. **Recarga durante procesamiento:** se comprobó continuidad visual de la operación al hacer F5; una verificación de idempotencia estricta exigiría consultar registros o almacenamiento.
7. **Autorización:** las URL de reservas ajenas o sin sesión no exhibieron detalles privados desde el frontend. Esto no sustituye probar directamente la seguridad de los endpoints de la API.

## 14. Comprobaciones adicionales recomendadas (fuera de los 35 casos)

- Pruebas automatizadas con solicitudes concurrentes realmente simultáneas al mismo asiento y a asientos distintos.
- Revisión de idempotencia mediante `requestId` y número de reservas persistidas tras reintentos, doble clic y recarga.
- Comprobación de que el asiento reservado por un usuario sigue ocupado después de reiniciar servicios (en entorno controlado).
- Comportamiento de token o sesión expirados durante el seguimiento de una reserva.
- Prueba de restricciones de autorización directamente sobre los endpoints de reserva y consulta.
- Validar con el equipo si el inicio de sesión con Google, los filtros de historial o la actualización en tiempo real forman parte del alcance exigido.

## 15. Conclusión

El frontend completó exitosamente el flujo esencial **evento → asientos → autenticación → reserva → confirmación → asiento ocupado** y mostró protección básica de historiales por usuario. Se observaron reservas confirmadas, rechazos con motivos claros y persistencia entre sesiones. En situaciones con dos usuarios, el backend impidió una reserva duplicada del mismo asiento y permitió confirmar reservas de asientos distintos.

Quedaron documentadas dos observaciones centrales sobre falta de sincronización automática de disponibilidad en pantallas abiertas, junto con límites de algunas verificaciones manuales. Los 35 casos constituyen un **registro de ejecución funcional con observaciones**, no una certificación exhaustiva de seguridad, carga o concurrencia.
