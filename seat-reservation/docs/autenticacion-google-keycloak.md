# Autenticación de usuarios: Google y Keycloak


## Objetivo

Documentar los dos métodos de inicio de sesión del proyecto Seat Reservation: usuarios locales de Keycloak (`usuario1` y `usuario2`) y Google como proveedor externo de identidad mediante Keycloak.

Google utiliza OpenID Connect (OIDC) y se integra como proveedor externo de identidad en Keycloak. Los usuarios locales siguen disponibles para las pruebas del sistema.

**Alcance:** esta guía explica el flujo de usuarios; la comunicación entre Availability, Booking, Payment y Notifications conserva sus tokens de servicio.

## 1. Arquitectura

El flujo de autenticación se organiza de la siguiente manera:

1. El usuario entra al frontend de Seat Reservation.
    
2. React redirige al usuario a Keycloak.
    
3. Keycloak muestra su página de inicio de sesión, con usuarios locales y la opción de Google.
    
4. El usuario puede iniciar sesión con `usuario1` o `usuario2`, o seleccionar Google para autenticarse con su cuenta externa.
    
5. Si elige Google, el proveedor devuelve el navegador a Keycloak.
    
6. Keycloak completa la autenticación local o federada y emite sus propios tokens para el cliente `seat-web`.
    
7. React utiliza el access token de Keycloak para acceder a los endpoints protegidos de Availability.
    

Google no reemplaza a Keycloak: es el proveedor externo de identidad. El backend continúa validando los tokens emitidos por el realm del proyecto.

## 2. Datos conocidos del proyecto

|Elemento|Valor|
|---|---|
|Frontend local con Docker|`http://localhost:3000`|
|Keycloak público|`http://localhost:8081`|
|Realm|`seat-reservation`|
|Cliente del frontend|`seat-web`|
|Availability API|`http://localhost:5001`|
|Archivo del realm|`infra/keycloak/seat-reservation-realm.json`|

Estos valores provienen de la configuración conocida del proyecto y deben verificarse si el equipo hizo cambios.

## 3. Crear el proyecto de Google Cloud

1. Entrar en [https://console.cloud.google.com/](https://console.cloud.google.com/)
    
2. Crear o seleccionar un proyecto, por ejemplo `Seat Reservation`.
    
3. Abrir Google Auth Platform.
    
4. Configurar la pantalla de consentimiento.
    
5. Para una prueba con cuentas personales, seleccionar el tipo de usuario externo (`External`) cuando corresponda.
    
6. Si la aplicación está en modo de prueba, agregar la cuenta de Google que se utilizará para probar el login como usuario de prueba.
    
7. Ir a la sección de clientes (`Clients`) y crear un cliente OAuth.
    
8. Seleccionar el tipo de aplicación `Web application`.
    
9. Asignar un nombre, por ejemplo `Keycloak Seat Reservation`.
    

Documentación oficial:

- [https://www.keycloak.org/docs/latest/server_admin/](https://www.keycloak.org/docs/latest/server_admin/)
    
- [https://developers.google.com/identity/protocols/oauth2/web-server](https://developers.google.com/identity/protocols/oauth2/web-server)
    

## 4. Configurar la URL de retorno

Antes de terminar la configuración en Google, abrir la consola de administración de Keycloak.

1. Entrar al realm `seat-reservation`.
    
2. Ir a `Identity Providers`.
    
3. Seleccionar `Add provider` y elegir `Google`.
    
4. Copiar el valor que Keycloak muestra en el campo `Redirect URI`.
    

En Google Cloud, agregar esa URL en `Authorized redirect URIs` del cliente OAuth.

La URL tendrá una forma similar a:

`http://localhost:8081/realms/seat-reservation/broker/google/endpoint`

**No asumir que ese ejemplo es la URL definitiva.** Copiar siempre la URL que muestre la instalación real de Keycloak.

La URL debe coincidir exactamente: esquema, host, puerto, ruta y barra final, si corresponde. Una diferencia puede provocar el error `redirect_uri_mismatch`.

## 5. Copiar las credenciales

Al crear el cliente OAuth, Google proporciona:

- `Client ID`
    
- `Client Secret`
    

Copiar ambos valores a la configuración del proveedor Google en Keycloak.

No guardar el `Client Secret` en:

- Git o el repositorio.
    
- Archivos públicos del frontend.
    
- Variables `VITE_*` expuestas al navegador.
    
- Documentación compartida de Obsidian.
    
- Capturas de pantalla o mensajes grupales innecesarios.
    

El secreto pertenece a la configuración del proveedor en Keycloak, no al frontend React.

## 6. Guardar la configuración en Keycloak

En `Identity Providers` → `Google`, completar:

- **Alias:** `google`.
    
- **Client ID:** el valor obtenido de Google Cloud.
    
- **Client Secret:** el valor obtenido de Google Cloud.
    
- **Default Scopes:** `openid profile email`, salvo que la versión/configuración actual indique otra cosa.
    

Guardar los cambios.

Los scopes anteriores permiten solicitar identidad básica, perfil y correo. No solicitar acceso a Gmail, Drive ni otros servicios porque no son necesarios para el login.

El alias `google` también interviene en la URL de retorno que genera Keycloak. Si se cambia, hay que comprobar nuevamente la URL.

## 7. Verificar ambas modalidades de autenticación

1. Abrir la aplicación.
    
2. Iniciar el flujo de login.
    
3. Verificar que el navegador llegue al realm `seat-reservation` de Keycloak.
    
4. Confirmar que aparezca la opción Google.
    
5. Seleccionarla y autenticar la cuenta de prueba.
    
6. Confirmar que Google devuelva el navegador a Keycloak.
    
7. Confirmar que Keycloak redirija al frontend y finalice el inicio de sesión.
    
8. Verificar que el frontend tenga una sesión válida y pueda llamar a Availability con el access token de Keycloak.
    
9. Repetir el inicio de sesión con los usuarios locales `usuario1` y `usuario2` y comprobar que siguen funcionando.
    

La integración de Google se puede validar antes de completar toda la interfaz de reservas, siempre que el cliente de prueba y su redirect URI estén correctamente configurados.

## 8. Diagnóstico de errores comunes

### `redirect_uri_mismatch`

- Comparar la URL que envía Keycloak con `Authorized redirect URIs` en Google Cloud.
    
- Verificar puerto, esquema, host, ruta y barra final.
    
- Usar la URL que muestra Keycloak, no una inventada.
    

### Google no aparece en el login

- Confirmar que el proveedor Google esté habilitado y guardado.
    
- Verificar que no esté configurado para ocultarse en la página de login.
    
- Confirmar que el usuario realmente esté entrando al realm `seat-reservation`.
    

### Google autentica, pero falla el retorno

- Revisar los logs de Keycloak.
    
- Verificar las credenciales del cliente OAuth.
    
- Comprobar la URL de retorno y la configuración del primer inicio de sesión del proveedor.
    

### El login funciona, pero Availability devuelve 401

- Confirmar que React esté enviando el access token de Keycloak.
    
- Revisar `Authorization: Bearer <token>`.
    
- Verificar la autoridad/issuer que utiliza Availability y el emisor del token.
    
- Revisar expiración y configuración del cliente.
    

### El navegador bloquea la llamada al backend

- Revisar CORS en Availability.
    
- Confirmar que el origen real del frontend esté permitido, por ejemplo `http://localhost:3000` si se usa Docker.
    
- No confundir el origen del frontend con la URL de retorno de Google.
    

## 9. Seguridad y coordinación del equipo

- No modificar ni reemplazar el realm compartido sin revisar primero los cambios del grupo.
    
- No subir secretos de Google al repositorio.
    
- Mantener los usuarios locales para que continúen disponibles.
    
- No configurar Google directamente desde React: la federación se realiza en Keycloak.
    
- Las credenciales de Google OAuth se utilizan exclusivamente para configurar el proveedor de identidad en Keycloak y no deben compartirse con otros servicios ni incluirse en el frontend.
    
- No ejecutar `docker compose down -v` por rutina, porque puede borrar volúmenes y datos locales.
    

## 10. Lista de verificación de la integración

- El profesor confirma que Google cumple la consigna de proveedor externo.
    
- Existe un cliente OAuth de Google para desarrollo.
    
- La URL de retorno coincide con la que muestra Keycloak.
    
- El proveedor Google está configurado y habilitado en `seat-reservation`.
    
- El botón de Google aparece en el login de Keycloak.
    
- El usuario puede autenticarse con Google.
    
- Keycloak emite el token que utiliza el frontend.
    
- El frontend puede acceder a un endpoint protegido de Availability.
    
- Los usuarios locales siguen funcionando.
    
- No se subieron secretos al repositorio.
    

## Referencias oficiales

- Keycloak Server Administration Guide: [https://www.keycloak.org/docs/latest/server_admin/](https://www.keycloak.org/docs/latest/server_admin/)
    
- Google OAuth 2.0 para aplicaciones web: [https://developers.google.com/identity/protocols/oauth2/web-server](https://developers.google.com/identity/protocols/oauth2/web-server)
    
- Google Cloud Console: [https://console.cloud.google.com/](https://console.cloud.google.com/)
