# Autenticación de usuarios: usuarios locales y Google

## Resumen

El sistema permite iniciar sesión de dos formas, siempre a través de Keycloak (realm `seat-reservation`):

- **Usuarios locales** `usuario1` y `usuario2` (contraseña igual al usuario). Vienen en el realm exportado y funcionan en cualquier máquina sin configurar nada.
- **Google** como proveedor de identidad externo (OpenID Connect). Es **opcional** y requiere un paso adicional, porque sus credenciales son secretos y no pueden estar en el repositorio.

Google no reemplaza a Keycloak. El frontend siempre habla con Keycloak, y Keycloak delega la autenticación en Google cuando el usuario elige ese botón. Los servicios validan únicamente tokens emitidos por Keycloak.

## Flujo

1. El usuario entra a `http://localhost:3000` y el frontend lo redirige a Keycloak (`http://localhost:8081`).
2. Keycloak muestra usuario/contraseña y, si Google está configurado, el botón "Google".
3. Si elige Google, se autentica allí y Google devuelve el navegador a Keycloak.
4. Keycloak emite sus propios tokens para el cliente `seat-web`, y el frontend los usa para llamar a Availability.

## Por qué Google no está en el realm exportado

El proveedor de Google lleva un Client Secret. Si se exportara el realm con Google cargado, el secret saldría enmascarado y el import en otra máquina quedaría roto, o el secreto real terminaría en el repositorio. Por eso Google se carga en tiempo de ejecución con un script, y la configuración queda solo en el volumen de Keycloak de cada máquina.

**Nunca exportar el realm después de configurar Google.**

## Activar Google (para quien clone el repo)

Requisitos:
- El sistema levantado con `docker compose up -d --build` y Keycloak ya iniciado (tarda cerca de 1 minuto).
- El **Client ID** y el **Client Secret** del cliente OAuth de Google, que el equipo entrega por privado.
- Una cuenta de Google habilitada como usuario de prueba (ver "Modo de prueba de Google").

Desde la carpeta `seat-reservation`:

```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/configurar-google.ps1
```

El script pide el Client ID y el Client Secret por consola (el secret no se muestra) y registra el proveedor `google` en el realm mediante la API de administración de Keycloak. No guarda las credenciales en ningún archivo.

Resultado esperado: `OK  Proveedor google creado.` (o `actualizado` si ya existía) y la Redirect URI impresa.

Para probar, abrir `http://localhost:3000` en una ventana de incógnito. El login de Keycloak debe mostrar el botón "Google". Al elegirlo, se ingresa con la cuenta de prueba. En el primer ingreso, Keycloak puede pedir completar nombre y apellido.

Si no se configura Google, el sistema funciona igual con `usuario1` y `usuario2`.

## Cuándo hay que volver a correr el script

La configuración de Google vive en el volumen de Keycloak. Si se ejecuta `docker compose down -v`, se borra y hay que volver a correr el script.

## Cómo se creó el cliente OAuth en Google Cloud (referencia del equipo)

1. En https://console.cloud.google.com/ crear o elegir un proyecto.
2. En Google Auth Platform configurar la pantalla de consentimiento, tipo `External`.
3. En Data Access dejar solo los scopes `openid`, `email` y `profile`.
4. En Clients crear un cliente OAuth de tipo `Web application`.
5. En "Authorized redirect URIs" cargar exactamente:

```
http://localhost:8081/realms/seat-reservation/broker/google/endpoint
```

Es una dirección `localhost`, así que sirve en cualquier máquina. Debe coincidir carácter por carácter con la que muestra Keycloak en Identity providers > google.

## Modo de prueba de Google

Mientras el proyecto de Google esté en modo "Testing", solo pueden ingresar las cuentas cargadas como "Test users". Cualquier otra ve un error de acceso bloqueado. Además, Google puede pedir verificación adicional (SMS, correo o doble factor) al ingresar desde un dispositivo o ubicación nuevos. [Confirmar con una prueba desde otra máquina.]

## Qué se probó

- Ingreso con la cuenta de Google de prueba desde una máquina del equipo.
- Reserva de un asiento con el usuario de Google.
- Username que asigna Keycloak al usuario federado.
- Ingreso con `usuario1` y `usuario2` tras configurar Google.
- Prueba desde una máquina que nunca haya iniciado sesión con esa cuenta.

## Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `redirect_uri_mismatch` (pantalla de Google) | La URI de Google Cloud no es idéntica a la de Keycloak | Comparar esquema, puerto, ruta y barra final. Google puede tardar unos minutos en aplicar el cambio |
| "Acceso bloqueado" o `access_denied` | La cuenta no está en Test users | Agregarla en Google Auth Platform > Audience |
| No aparece el botón Google | El script no corrió o falló | Volver a correrlo y revisar Identity providers en el admin |
| Keycloak: "Invalid parameter: redirect_uri" antes del login | [Posible volumen viejo de Keycloak con un realm anterior] | `docker compose down -v` y levantar de nuevo; después volver a correr el script |
| Keycloak no arranca y el log dice `MIGRATION_MODEL already exists` | Volumen de Keycloak a medio inicializar | `docker compose down -v` y levantar de nuevo |
| Login correcto pero Availability responde 401 | Token ausente o emisor distinto | Revisar `Authorization: Bearer` y el emisor `http://localhost:8081` |
| El navegador bloquea las llamadas a la API | CORS | Verificar `Cors__AllowedOrigins__0: http://localhost:3000` en Availability |

## Seguridad

- El Client Secret de Google no va en el repositorio, ni en el frontend (`VITE_*`), ni en capturas o chats grupales.
- Solo lo usa Keycloak, y se carga con el script.
- Las credenciales de los servicios (`availability-service`, `booking-service`) son otra cosa: son secretos de desarrollo del realm.
- No exportar el realm después de configurar Google.