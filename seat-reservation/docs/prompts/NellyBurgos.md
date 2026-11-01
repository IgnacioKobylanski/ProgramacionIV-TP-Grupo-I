# Historial de prompts: Nelly Burgos

Herramienta: Claude (Anthropic) 

Componentes trabajados: frontend (estructura inicial, pantallas, componentes y estilos)

## 1. Creación del proyecto
- Prompt: consulté los comandos para crear la estructura del front y levantarlo en local antes de subirlo al repo.
- Qué se usó: `npm create vite` con plantilla React + TypeScript.
- Mi aporte: creé el proyecto dentro de `seat-reservation`, lo levanté y verifiqué el placeholder en el navegador. Antes de subirlo, revisé con `git status` que no se incluyera `node_modules`.

## 2. Conexión provisoria con Availability
- Prompt: consulté cómo conectar el frontend con Availability para ver datos reales, y cómo levantar el backend sin el connection string de Azure.
- Qué se usó: `App.tsx` provisorio que llama a `GET /events` en `localhost:5001`, usando el CORS del backend.
- Mi aporte: levanté el backend con el override, para hacerlo sin el connection string de Azure, y verifiqué que el frontend mostrara los 3 eventos reales.

## 3. Pantallas y componentes
- Prompts: pedí asistencia para armar las tres pantallas (eventos, sala de asientos y estado de la reserva). Consulté cómo no perder el asiento elegido al ir al login de Keycloak.
- Qué se usó: `EventosPage`, `AsientosPage` y `ReservaPage`; componentes `Navbar`, `Asiento`, `EstadoBadge`, `PasosReserva` y `Estados`; `sessionStorage` para recordar el asiento.
- Mi aporte: integré las pantallas con la parte de María sin modificar sus archivos: la sala usa su `grilla.ts` para armar las filas (cuando se cambió ese archivo, pedí volverlo atrás y resolver el filtro en mis pantallas) y la pantalla de estado usa su hook `useReservationStatus`, que consulta cada 1 segundo, para mostrar el avance con la barra de pasos. Decidí que eventos y asientos se vean sin iniciar sesión y mostrar todos los asientos (los ocupados en rojo y sin poder tocarlos). Verifiqué que compilara con `npm run build`.

## 4. Estilos y paleta
- Prompts: consulté cómo organizar los estilos y pedí una versión más resumida del CSS.
- Qué se usó: `styles/index.css` con variables de color y secciones por pantalla.
- Mi aporte: elegí los colores por estado (verde libre, rojo ocupado, azul seleccionado), pedí sacar las reglas repetidas y revisé las tres pantallas para confirmar que se vieran igual.

## 5. Login con Keycloak
- Prompts: consulté los errores al iniciar sesión ("Invalid parameter: redirect_uri" e "Invalid username or password").
- Qué se usó: borrado del volumen viejo de Keycloak para que vuelva a importar el realm, y los usuarios de prueba del realm.
- Mi aporte: recreé el contenedor y el volumen, detecté que tenía que usar `usuario1` y no `admin`, y verifiqué que el login volviera a la pantalla con el asiento elegido.

## 6. Pruebas del flujo completo con RabbitMQ
- Prompts: pedí una guía para levantar todo con Docker después del cambio de Azure a RabbitMQ.
- Qué se usó: `docker compose` construyendo los servicios de a uno, el panel de RabbitMQ y el script `configurar-google.ps1` del grupo.
- Mi aporte: descomenté el servicio `frontend` solo en mi compu (sin subir ese cambio), probé el flujo completo con `usuario1` hasta llegar a Confirmada, verifiqué que el asiento quedara en rojo y que la cola `booking` tuviera 2 consumidores. También probé el login con Google usando la cuenta del grupo: detecté en los logs de Keycloak que el secret estaba mal cargado, lo corregí y verifiqué que la app mostrara el usuario de Google.