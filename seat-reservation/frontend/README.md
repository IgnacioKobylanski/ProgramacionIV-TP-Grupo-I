# Frontend - Sistema de reserva de asientos

Interfaz web **SeatReserve** del trabajo práctico de Programación IV (UTN), Grupo 1. Permite consultar eventos, elegir un asiento, iniciar sesión, solicitar una reserva, seguir su resultado y consultar las reservas propias.

El frontend utiliza React, TypeScript y Vite. React Router administra la navegación y `keycloak-js` integra el inicio y cierre de sesión.

> Los comandos de Docker se ejecutan desde `seat-reservation`, donde está `docker-compose.yml`. Los comandos de npm se ejecutan desde `seat-reservation/frontend`.

## Arquitectura y conexión con el backend

La aplicación se ejecuta en el navegador y realiza solicitudes HTTP a Availability. Para autenticarse, redirige al usuario a Keycloak y utiliza el token recibido en las operaciones protegidas.

- **Availability:** entrega eventos y asientos, recibe solicitudes de reserva y permite consultar resultados y reservas propias.
- **Keycloak:** administra la sesión mediante el realm `seat-reservation` y el cliente público `seat-web`.
- **Booking, Payment, Notifications y RabbitMQ:** participan en el procesamiento del backend. El frontend consulta los resultados de las reservas a través de Availability; no llama directamente a estos componentes.

La reserva es asíncrona: Availability responde `202 Accepted` con un `requestId` y un `correlationId`. Esto indica que recibió la solicitud, no que el asiento ya esté confirmado. La pantalla de seguimiento consulta después el resultado.

Los datos provienen de las APIs reales. No hay un modo de datos de ejemplo independiente del backend.

## Requisitos

- Repositorio clonado y navegador web.
- Docker Desktop iniciado, con Docker Compose disponible, para ejecutar el sistema completo o el backend.
- Para desarrollar el frontend fuera de Docker: Node.js 22.12 o posterior y npm. El Dockerfile utiliza Node.js 22 para compilar y Nginx para servir el resultado.
- Puertos indicados en la siguiente sección disponibles.

La ejecución completa con Docker no requiere instalar Node.js ni el SDK de .NET en la máquina. El broker actual es RabbitMQ local; no hace falta una cuenta de Azure ni configurar un connection string de Service Bus.

## Puertos y direcciones

| Componente | Dirección o puerto local | Uso |
| --- | --- | --- |
| Frontend con Docker | [http://localhost:3000](http://localhost:3000) | Nginx sirve la aplicación compilada; puerto interno `80`. |
| Frontend con Vite | [http://localhost:5173](http://localhost:5173) | Desarrollo con actualización al guardar cambios. |
| Availability | [http://localhost:5001](http://localhost:5001) | API utilizada por el navegador. |
| Keycloak | [http://localhost:8081](http://localhost:8081) | Inicio de sesión y consola de administración. |
| Booking en Docker | `5002` y `5003` | Puertos publicados para sus dos réplicas; el frontend no los utiliza. |
| Payment en Docker | `payment:8080`, dentro de la red de contenedores | Servicio gRPC utilizado por Booking; no publica un puerto local. |
| Notifications | `5004` | Servicio de avisos utilizado por Booking. |
| PostgreSQL | `5432` | Persistencia del backend. |
| RabbitMQ | `5672`; panel en [http://localhost:15672](http://localhost:15672) | Mensajería del backend y administración del broker. |

El puerto `5003` de Payment mencionado en otras guías corresponde a la ejecución con `dotnet run`. En el Compose actual ese puerto local pertenece a una réplica de Booking. Las instrucciones de este README utilizan el backend en Docker.

## Cómo ejecutarlo

### Opción A: sistema completo con Docker

1. Abrir Docker Desktop y esperar a que esté iniciado.
2. Desde `seat-reservation`, construir y levantar los servicios:

   ```powershell
   docker compose up -d --build
   docker compose ps
   ```

3. Esperar a que terminen de iniciar PostgreSQL, RabbitMQ, Keycloak y las APIs. En el primer arranque se crean las bases, se aplican migraciones y se importa el realm. Para revisar el inicio:

   ```powershell
   docker compose logs --tail=80 frontend availability booking keycloak
   ```

4. Abrir [http://localhost:3000](http://localhost:3000). Debe mostrarse el listado de eventos.
5. Para comprobar que Availability responde, abrir [http://localhost:5001/events](http://localhost:5001/events); devuelve JSON.

Si se modifica el frontend, reconstruir su imagen desde `seat-reservation`:

```powershell
docker compose up -d --build frontend
```

Nginx sirve archivos compilados; guardar un cambio en el código no actualiza automáticamente el contenedor. Su configuración devuelve `index.html` para las rutas de React Router, permitiendo abrir o recargar una ruta como `/mis-reservas`.

### Opción B: frontend con Vite y backend en Docker

1. Desde `seat-reservation`, levantar el backend y su infraestructura:

   ```powershell
   docker compose up -d --build postgres rabbitmq keycloak availability booking payment notifications
   ```

2. Entrar a la carpeta del frontend, instalar las dependencias según `package-lock.json` e iniciar Vite:

   ```powershell
   cd frontend
   npm ci
   npm run dev
   ```

3. Abrir [http://localhost:5173](http://localhost:5173).
4. Mantener esa terminal abierta. Para detener Vite, presionar `Ctrl+C`.

Vite tiene `strictPort: true`: si `5173` está ocupado, termina con un error en lugar de elegir otro puerto. Esta modalidad permite trabajar sobre React sin reconstruir una imagen por cada cambio. El backend sigue ejecutándose en Docker.

### Detener el entorno

Desde `seat-reservation`, `docker compose stop` detiene los servicios. `docker compose down` detiene y elimina los contenedores conservando los volúmenes de PostgreSQL y Keycloak.

## Configuración del frontend

Los valores se definen en `src/config.ts`. Con la configuración local predeterminada no hace falta crear un archivo de entorno.

| Configuración | Valor predeterminado | Función |
| --- | --- | --- |
| `VITE_API_URL` | `http://localhost:5001` | Dirección base de Availability, sin barra final. |
| `VITE_KEYCLOAK_URL` | `http://localhost:8081` | Dirección pública de Keycloak, sin agregar `/realms/...`. |
| `KEYCLOAK_CONFIG.realm` | `seat-reservation` | Realm del login; se configura en el código. |
| `KEYCLOAK_CONFIG.clientId` | `seat-web` | Cliente público del frontend; se configura en el código. |
| `POLL_INTERVAL_MS` | `1000` | Espera entre consultas del seguimiento, en milisegundos. |
| `POLL_TIMEOUT_MS` | `30000` | Límite de espera del seguimiento; se comprueba entre consultas. |

Para cambiar las direcciones, crear opcionalmente `frontend/.env.local`:

```dotenv
VITE_API_URL=http://localhost:5001
VITE_KEYCLOAK_URL=http://localhost:8081
```

Las direcciones las utiliza el navegador, incluso cuando la aplicación se sirve desde Docker. Deben ser accesibles desde la máquina del usuario; nombres internos como `availability` o `keycloak` corresponden a la red de contenedores.

Después de cambiar `.env.local`, reiniciar Vite o reconstruir la imagen del frontend. Vite incorpora estas variables durante el desarrollo o la compilación: definirlas únicamente como variables de ejecución del contenedor Nginx no cambia una aplicación ya compilada. Las variables `VITE_*` son públicas y no deben contener secretos.

### CORS y direcciones autorizadas en Keycloak

La configuración actual admite los orígenes `http://localhost:3000` y `http://localhost:5173`:

- Availability los declara en `Cors:AllowedOrigins`, en `src/Availability/Availability.Api/appsettings.json`.
- El cliente `seat-web` del realm exportado los incluye en `webOrigins` y permite sus rutas mediante `redirectUris` terminadas en `/*`.

Si se cambia el host, el puerto o el protocolo del frontend, actualizar ambos lugares y comprobar también el retorno al cerrar sesión. Abrir la aplicación con `127.0.0.1` en lugar de `localhost` cambia el origen.

Keycloak importa el realm al inicializar el entorno. Editar el JSON del repositorio no actualiza automáticamente un realm que ya existe en el volumen: para una instalación existente, revisar y modificar el cliente desde su consola de administración.

## Inicio y cierre de sesión

La aplicación comprueba la sesión al iniciar con `check-sso`, sin exigir autenticación para consultar eventos y asientos. El login utiliza el flujo de autorización con PKCE `S256` y redirige a la página de Keycloak. El frontend no necesita un secreto de cliente.

Usuarios locales de desarrollo:

| Usuario | Contraseña |
| --- | --- |
| `usuario1` | `usuario1` |
| `usuario2` | `usuario2` |

La consola de administración de Keycloak utiliza `admin` / `admin` en el entorno local. Estas credenciales son para desarrollo.

El botón **Ingresar** devuelve al usuario a la dirección donde estaba. Si había elegido un asiento antes del login, se guarda su identificador en `sessionStorage`. Al volver, se recupera la selección si sigue disponible; el usuario debe presionar **Reservar** para enviar la solicitud.

Antes de cada solicitud protegida, el cliente intenta renovar el token si vence en menos de 30 segundos. Lo adjunta como `Authorization: Bearer ...`. Al presionar **Salir**, se cierra la sesión en Keycloak y se regresa al inicio del frontend.

El acceso con Google depende de que el proveedor esté configurado en la instancia de Keycloak. El realm exportado actualmente no incluye ese proveedor. Su preparación está documentada en [Integración Google OAuth con Keycloak](../docs/autenticacion-google-keycloak.md); las credenciales de Google no se configuran en React.

## Pantallas y navegación

| Ruta del frontend | Página | Funcionamiento |
| --- | --- | --- |
| `/` | `EventosPage` | Lista eventos y consulta sus asientos para contar los libres. Si falla ese conteo, muestra el evento sin contador. Acceso público. |
| `/events/:eventId` | `AsientosPage` | Muestra la grilla, permite elegir un asiento y solicitar su reserva. Consultar es público; reservar requiere sesión. |
| `/reservations/:requestId` | `ReservaPage` | Consulta el resultado de una solicitud propia y representa su avance. Requiere sesión para obtener los datos. |
| `/mis-reservas` | `MisReservasPage` | Lista las reservas del usuario, permite filtrarlas por estado y abrir su detalle. Requiere sesión. |
| Cualquier otra ruta | Mensaje de ruta desconocida | Muestra «Página no encontrada». |

La grilla agrupa asientos por letra de fila y los ordena por número. Los libres se muestran en verde, el seleccionado en azul y los ocupados en rojo, deshabilitados. Solo se selecciona un asiento por solicitud. El botón **Actualizar** vuelve a consultar su disponibilidad.

**Mis reservas** obtiene los datos al abrir la pantalla y filtra localmente por Todas, Confirmada, Retenida, Rechazada o Vencida. No se actualiza periódicamente; para refrescar el listado hay que volver a entrar o recargar. Las solicitudes todavía no registradas en Booking pueden no aparecer en esa lista.

## Flujo de uso

1. Abrir el frontend y elegir **Ver asientos** en un evento.
2. Seleccionar un asiento libre. Seleccionarlo otra vez lo desmarca.
3. Si no hay sesión, presionar **Ingresar para reservar** y autenticarse en Keycloak.
4. Al regresar, comprobar la selección y presionar **Reservar**. El botón queda deshabilitado mientras se envía la solicitud.
5. Cuando Availability responde con el `requestId`, la aplicación abre la pantalla de seguimiento.
6. Observar el resultado. La selección visual no retiene el asiento: otro usuario puede obtenerlo antes de que Booking procese el pedido.
7. Abrir **Mis reservas** desde la barra superior para consultar el historial disponible y sus detalles.

### Estados y seguimiento automático

| Estado | Significado para el usuario |
| --- | --- |
| `EnProceso` | La solicitud fue recibida y todavía no tiene una reserva registrada en Booking. |
| `Retenida` | El asiento está apartado mientras se resuelve el pago. |
| `Confirmada` | Se aprobó el pago y se confirmó la reserva. |
| `Rechazada` | El asiento estaba ocupado, el pago falló o el servicio de pago no estuvo disponible. |
| `Vencida` | Terminó el tiempo de retención sin llegar a un resultado. |

`useReservationStatus` realiza una consulta inicial y, si el estado no es final, programa otra un segundo después de terminar la anterior. Se detiene al recibir Confirmada, Rechazada o Vencida. Ante errores de red o respuestas `5xx`, vuelve a intentar dentro del mismo período de seguimiento; ante otros errores, informa el problema y detiene las consultas.

Si transcurren aproximadamente 30 segundos sin resultado final, deja de consultar y pide recargar la página. Este límite se verifica entre solicitudes y no cancela una petición que siga esperando respuesta. Tampoco cancela ni vence la reserva: el backend continúa su procesamiento y administra su propio tiempo de retención.

## Operaciones utilizadas de Availability

Todas las rutas de esta tabla se agregan a `VITE_API_URL`. Son rutas de la API, distintas de las pantallas de React.

| Método | Ruta de API | Sesión | Uso en el frontend |
| --- | --- | --- | --- |
| GET | `/events` | No | Listado de eventos y datos del evento seleccionado. |
| GET | `/events/{eventId}/seats` | No | Grilla y conteo de asientos libres. Cada asiento incluye `id`, `label` y `occupied`. |
| POST | `/reservations` | Sí | Envía `{ eventId, seatId }`; recibe `requestId` y `correlationId`. |
| GET | `/reservations/{requestId}` | Sí | Obtiene `requestId`, `status` y `reason` de una solicitud propia. |
| GET | `/reservations/mine` | Sí | Obtiene las reservas del usuario autenticado con los datos de evento y asiento. |

El usuario se identifica mediante el token; no se envía un `userId` en el cuerpo de la reserva. La aplicación no solicita datos de tarjeta: el cobro está simulado en Payment.

## Organización y componentes

```text
frontend/
├── public/                 # Recursos estáticos
├── src/
│   ├── auth/               # Keycloak y contexto de sesión
│   ├── components/         # Elementos visuales reutilizables
│   ├── hooks/              # Carga de datos y seguimiento de reservas
│   ├── pages/              # Eventos, asientos, reserva y mis reservas
│   ├── services/           # Cliente HTTP y contratos TypeScript
│   ├── styles/index.css    # Estilos de la interfaz
│   ├── utils/              # Fechas, grilla y selección temporal
│   ├── App.tsx             # Rutas y estructura de la aplicación
│   ├── config.ts           # URLs y tiempos de seguimiento
│   └── main.tsx            # Inicialización de sesión, router y React
├── Dockerfile              # Compilación con Node y publicación con Nginx
├── nginx.conf              # Soporte para las rutas de la aplicación
├── package.json            # Dependencias y comandos
├── package-lock.json       # Versiones de dependencias para npm ci
└── vite.config.ts          # React, puerto 5173 y strictPort
```

| Componente o módulo | Responsabilidad |
| --- | --- |
| `Navbar` | Navegación, nombre del usuario y botones Ingresar, Mis reservas y Salir. |
| `Asiento` | Botón de un asiento libre, seleccionado u ocupado. |
| `EstadoBadge` | Mensaje e indicador del estado de la reserva y su motivo de rechazo. |
| `PasosReserva` | Avance visual: recibida, asiento retenido y resultado. |
| `Cargando` y `ErrorMensaje` | Mensajes reutilizables de espera, error, login o reintento. |
| `AuthProvider` y `useAuth` | Comparten el estado de sesión y las acciones de login y logout. |
| `useAsync` | Carga datos de las pantallas y expone carga, error y recarga. |
| `useReservationStatus` | Consulta periódicamente el resultado de una reserva. |
| `services/api.ts` | Centraliza las llamadas con `fetch`, el token y los errores HTTP. |
| `services/types.ts` | Define eventos, asientos, reservas, estados y motivos de rechazo. |
| `utils/grilla.ts` | Agrupa y ordena los asientos devueltos por la API. |
| `utils/seleccion.ts` | Conserva temporalmente el asiento elegido durante el login. |
| `utils/formato.ts` | Presenta fechas con formato `es-AR` según la zona horaria del navegador. |

## Compilación y revisión del código

Desde `seat-reservation/frontend`, con las dependencias instaladas mediante `npm ci`:

| Comando | Función |
| --- | --- |
| `npm run dev` | Inicia Vite en `5173`. |
| `npm run build` | Ejecuta la comprobación de TypeScript y genera la aplicación en `dist/`. |
| `npm run lint` | Revisa el código con Oxlint. |
| `npm run preview -- --port 5173` | Sirve una compilación existente para revisarla localmente. Ejecutar antes `npm run build` y detener Vite para liberar `5173`. |

La previsualización usa aquí `5173` para conservar el origen ya autorizado en Availability y Keycloak. Comprobar la dirección que muestra la terminal. El servidor `preview` se utiliza para revisión local; la imagen Docker publica la aplicación con Nginx.

Si PowerShell bloquea `npm.ps1`, se pueden ejecutar los mismos comandos con `npm.cmd`, por ejemplo `npm.cmd ci` y `npm.cmd run dev`.

## Verificación manual

Con el sistema levantado:

1. Sin iniciar sesión, comprobar que aparecen eventos y que se abre la grilla de uno de ellos.
2. Ingresar con `usuario1`, elegir un asiento y comprobar que la solicitud llega a un resultado final.
3. Volver al evento, actualizar la grilla y verificar que el asiento confirmado aparece ocupado.
4. Abrir **Mis reservas**, localizar la reserva y consultar su detalle.
5. Cerrar sesión y comprobar que el sitio sigue permitiendo consultas públicas.
6. Abrir o recargar directamente `/mis-reservas` para comprobar la navegación de la aplicación; sin sesión, debe solicitar autenticación para mostrar los datos.

Para observar un fallo de Payment desde la interfaz, ejecutar desde `seat-reservation`:

```powershell
docker compose stop payment
```

Solicitar otro asiento libre. El resultado esperado es **Rechazada**, con motivo **PagoNoDisponible**. Al terminar, restaurar el servicio:

```powershell
docker compose start payment
```

Estos son procedimientos de verificación, no resultados de pruebas ejecutadas al redactar el README. Los casos y las evidencias del equipo se registran en [Pruebas del frontend](../docs/frontend-tests.md).

## Problemas frecuentes

| Síntoma | Qué revisar |
| --- | --- |
| No abre `localhost:3000` | Comprobar Docker Desktop, `docker compose ps` y `docker compose logs --tail=80 frontend`. |
| Vite informa que `5173` está ocupado | Detener la otra instancia. Cambiar de puerto exige revisar CORS y las direcciones admitidas en Keycloak. |
| Hay eventos, pero no aparece el contador o fallan los asientos | Availability necesita consultar a Booking. Revisar `docker compose logs --tail=80 availability booking keycloak`; un problema de credenciales entre servicios también puede producir un `503`. |
| El navegador informa un error de CORS o de conexión | Comprobar `VITE_API_URL`, la disponibilidad de Availability y que el origen del navegador figure en `Cors:AllowedOrigins`. |
| Keycloak muestra `Invalid parameter: redirect_uri` | Revisar las direcciones de retorno del cliente `seat-web` y usar el host y puerto autorizados. |
| Se solicita ingresar otra vez o aparece un `401` | Volver a iniciar sesión y comprobar que Keycloak esté disponible y permita renovar el token. |
| No aparece la opción de Google | Revisar la configuración del proveedor en Keycloak siguiendo la guía de autenticación; no depende de un botón propio de React. |
| Aparece «No encontramos lo que buscabas» | El recurso no existe o se está consultando una solicitud que no pertenece al usuario conectado. |
| El seguimiento tarda más de 30 segundos | Recargar para volver a consultar y revisar los logs de Availability, Booking, Payment y RabbitMQ. El mensaje de espera no implica un rechazo. |
| Mis reservas no refleja un cambio reciente | Volver a entrar o recargar: el listado no tiene seguimiento automático. |
| Docker muestra una versión anterior de la interfaz | Ejecutar `docker compose up -d --build frontend`. |
| Recargar una ruta interna devuelve `404` del servidor web | Comprobar que la imagen incluya `nginx.conf`, que redirige las rutas de React a `index.html`. |

## Alcance y limitaciones actuales

- La grilla se consulta al abrir la pantalla o al presionar **Actualizar**. No recibe actualizaciones en tiempo real.
- El seguimiento usa consultas HTTP periódicas; no utiliza WebSockets ni notificaciones push.
- La pantalla de detalle obtiene el estado por `requestId`, pero el nombre del evento y la etiqueta del asiento dependen de los datos de navegación disponibles. La consulta del estado funciona sin ellos.
- No hay formularios de administración de eventos, selección de varios asientos por solicitud, cancelaciones ni ingreso de datos de pago.
- No hay una pantalla de notificaciones. Los avisos se registran y simulan en el backend.
- El repositorio no define un comando `npm test`; las pruebas funcionales del frontend se documentan por separado.
- La configuración de URLs y autenticación descrita corresponde al entorno local de desarrollo.
