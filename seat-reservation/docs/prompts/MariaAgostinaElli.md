# Historial de prompts: Maria Agostina Elli

Herramienta: Claude (Anthropic)

## 1. Docker del frontend (Dockerfile, .dockerignore y docker-compose.yml)
Prompt: pedí armar el Dockerfile para que el front corra en un contenedor sin que quien corrige necesite Node, el .dockerignore y pedí qué agregar al compose, pasando el archivo completo.
Qué se usó: un Dockerfile de dos etapas (Node compila y nginx sirve dist), un nginx.conf con try_files hacia index.html para que las rutas de React Router no den 404 al refrescar, un .dockerignore con node_modules y dist, y un servicio frontend en el compose con el puerto 3000.
Mi aporte: elegí la versión de producción, verifiqué que el package.json tuviera el script build y el package-lock.json, revisé que el puerto 3000 no chocara con los otros y verifiqué que abriera en http://localhost:3000.

## 2. Revisión del backend para el frontend y lista de endpoint
Prompt: pedí la lista de endpoints disponibles.
Qué se usó: archivo exportado de backend
Mi aporte: exporté el archivo de backend (los .cs) actualizado desde la terminal

## 3. APIs
Prompt: pedí armar la capa de acceso a la API con el token de Keycloak y que todo fallo saliera como ApiError.
Qué resolvió: armó request y realApi, con el manejo de errores uniforme y las cabeceras condicionales.
Mi aporte: definí manejo de errores

## 4. Configuración
Prompt: pedí armar config.ts con la URL de la API y los datos de Keycloak, leyendo las URLs de variables de entorno de Vite (VITE_API_URL y VITE_KEYCLOAK_URL), y agregar las constantes del polling.
Qué resolvió: definió API_URL, KEYCLOAK_CONFIG, POLL_INTERVAL_MS y POLL_TIMEOUT_MS.
Mi aporte: dejé las URLs configurables para cambiarlas sin tocar el código al desarrollar y centralicé los valores del polling. En Docker, Vite fija las variables al compilar y el Dockerfile no las declara, por lo que el contenedor usa los valores por defecto de config.ts.

## 5. Keycloak
Prompt: pedí armar el cliente de Keycloak del front: una única instancia exportada, con la configuración de config.ts, y una función initKeycloak().
Qué resolvió: armó una instancia única que comparten api.ts y AuthContext, con init en check-sso y pkceMethod: 'S256', y explicó cómo Keycloak valida la URL de retorno.
Mi aporte: pedí un login que no fallara por una redirect URI inválida.

## 6. Login con Keycloak
Prompt: pedí armar el login del front con Keycloak y cómo probar que funciona después de agregar los puertos del front al cliente `seat-web`.
Qué se usó: la librería oficial keycloak-js instalada con npm, auth/keycloak.ts con la instancia del cliente seat-web y PKCE, y los botones de iniciar y cerrar sesión en Navbar.tsx.
Qué resolvió: armó el recorrido de prueba (iniciar sesión, volver al frontend, cerrar sesión) y explicó cómo interpretar los errores más comunes (redirect_uri inválido, orígenes web).
Mi aporte: agregué los puertos del front (5173 y 3000) al cliente `seat-web` desde el panel de Keycloak, probé el recorrido completo y, una vez que funcionó, exporté el realm para actualizar `infra/keycloak/seat-reservation-realm.json`.

## 7. Sesión de usuario
Prompt: pedí armar un contexto de React para la sesión de Keycloak (`AuthProvider` y `useAuth()`) cuyo estado se actualizara cuando Keycloak avisara que se cerró la sesión o falló la renovación del token, teniendo en cuenta que el login puede venir de un proveedor externo como Google.
Qué se usó: `auth/AuthContext.tsx` con `isLogged` y `username` en `useState` (valores iniciales tomados de `keycloak`), los callbacks `onAuthLogout` y `onAuthRefreshError` de keycloak-js registrados en un `useEffect` con limpieza, `login()` y `logout()` con `redirectUri`, y `useAuth()`. La UI se actualiza cuando Keycloak notifica. onAuthRefreshError salta al intentar renovar el token, es decir en la siguiente llamada autenticada de api.ts, y no en el momento exacto en que vence. Con Google no cambia el código, porque Keycloak hace de intermediario.
Mi aporte: definí que el Navbar y las páginas reflejaran el estado de la sesión, por ejemplo si se cierra la sesión o no se puede renovar el token.

## 8. Hook de estado de la reserva
Prompt: pedí armar un hook useReservationStatus(requestId) que consultara GET /reservations/{id} cada 1 s hasta un estado final (Confirmada, Rechazada o Vencida) o hasta 30 s. Que reintentara en silencio los errores transitorios (sin conexión o 5xx), que cortara con 401 y 404, que no hiciera dos peticiones a la vez, que cancelara todo al desmontar o cambiar el requestId y que devuelviera { result, error, timedOut, loading }.
Qué resolvió: armó el polling con setTimeout recursivo, clasificó los errores transitorios y definitivos, puso un tope de 30 s evaluado después de cada respuesta (solo frena la pantalla, no el backend), reinició los estados al cambiar el requestId y agregó la limpieza con una bandera activo.
Mi aporte: planteé el caso del backend levantando, definí que la pantalla de reserva muestre el estado sin recargar, aunque el backend tarde en levantar o falle un momento.

## 9. Revisión del backend por el endpoint de asientos que solo devolvía los libres
Prompt: pedí revisar, teniendo el endpoint que solo trae asientos libres, si había forma de deducir los ocupados.
Qué resolvió: localizó con grep los archivos relevantes. Al leer AvailabilityService.cs vio que GetSeatsAsync descartaba los asientos ocupados y que SeatDto solo tenía Id y Label. También se revisó la entidad Event, la cantidad de filas y columnas no se guarda en ningún lado, así que el frontend no podía deducir los asientos ocupados.
Mi aporte: agregué un flag Occupied al DTO para que devolviera todos los asientos. Apliqué el cambio en AvailabilityService.cs, busqué con grep que no hubiera otros usos de SeatDto, actualicé el comentario de la función y di aviso, porque el cambio modifica lo que devuelve un endpoint compartido.

## 10. Vista de la grilla de asientos y reserva
Prompt: pedí armar el dibujo de la grilla de asientos del evento con la información del backend, usando occupied para distinguir libres de ocupados, y la función reservar con su botón (oculto hasta seleccionar un asiento).
Qué resolvió: pidió keycloak.ts para saber cómo se obtiene el token y pasó cambios para App.tsx y código de la grilla, que se arma con lo que manda el backend, agrupando por la letra del label, y AsientosPage usa fila.letra.
Mi aporte: definí los requisitos de la funcionalidad, revisé el código entregado. Controlé con DbSeeder que la visualización fuera correcta y que al reservar se mostrara como ocupado.

## 11. Endpoint de reservas por usuario en el backend
Prompt: pedí el código para agregar el endpoint para obtener el listado de reservas por usuario
Qué se usó: GetByUserIdAsync en ReservationRepository.cs (EF Core: AsNoTracking, Where, OrderByDescending, ToListAsync), UserReservationDto y GetByUserAsync en ReservationService.cs, y GET /reservations?userId=... en Program.cs con la política AvailabilityOnly.
BookingReservation y GetReservationsByUserAsync en IBookingClient.cs y HttpBookingClient.cs (GetFromJsonAsync y Uri.EscapeDataString), y GetMyReservationsAsync con MyReservationDto en AvailabilityService.cs, que completa el nombre del evento y la etiqueta del asiento con una consulta por evento distinto. Endpoint GET /reservations/mine con RequireAuthorization, el userId sale del token.
Mi aporte: definí los requisitos de la funcionalidad, revisé el código entregado y modifiqué el backend.

## 12. Pantalla "Mis reservas"
Prompt: pedí armar el front de "Mis reservas" una vez terminado el endpoint `GET /reservations/mine` del backend, con su ruta, un link para entrar y un filtro por estado.
Qué se usó: tipo MyReservation en types.ts, getMyReservations en SeatApi y realApi (api.ts), MisReservasPage.tsx con useAsync y un filtro por estado hecho en memoria (Todas, Confirmada, Retenida, Rechazada, Vencida), ruta /mis-reservas en App.tsx y link en Navbar.tsx cuando hay sesión.
Mi aporte: definí los requisitos para el frontend, revisé y apliqué el código entregado. Probé la pantalla y confirmé que funciona.

## 13. Código para cambiar el estilo del front
Prompt: pasé una imagen del componente y el código del .css y pedí corregir que los botones para filtrar el estado de las reservas no se veían.
Qué resolvió: pasó código para agregar al archivo de estilo
Mi aporte: inspeccioné la página del front para encontrar el nombre del componente a modificar.

## 14. Exportación de código
Prompt: pedí un script para poder exportar todos los archivos .cs, .ts y .tsx del proyecto
Qué resolvió: pasó el código con find, while read y la exportación
Mi aporte: usé este código continuamente para verificar la integración y buscar endpoints o código obsoleto.

## 15. Resumen e integración de archivos de otros chats
Prompt: pedí hacer un resumen de las conversaciones para el proyecto con el formato dado e integrarlo con los archivos adjuntos
Qué resolvió: armó un resumen de prompts de todas las conversaciones
Mi aporte: sumé las conversaciones con otros chats