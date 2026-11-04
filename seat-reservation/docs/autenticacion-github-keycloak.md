# Autenticación con GitHub (respaldo de Google)

## Por qué existe este documento

GitHub se agrega **como medida de prevención**. El proveedor de identidad externo del proyecto es Google, pero Google suspendió la cuenta con la que se creó el cliente OAuth y el cliente quedó deshabilitado (`disabled_client`). Hasta que Google levante la suspensión, se deja GitHub como alternativa.

- No reemplaza a Google ni a los usuarios locales: los tres métodos conviven.
- Es **opcional**: sin configurarlo, el sistema funciona igual con `usuario1` y `usuario2`.

## Cómo funciona

Es el mismo mecanismo que con Google. El frontend siempre habla con Keycloak, y Keycloak delega la autenticación en GitHub cuando el usuario elige ese botón. Los servicios validan solamente tokens emitidos por Keycloak.

1. El usuario entra a `http://localhost:3000` y es redirigido a Keycloak.
2. Elige "GitHub" y se autentica allí.
3. GitHub devuelve el navegador a Keycloak.
4. Keycloak emite sus propios tokens para el cliente `seat-web`.

## Por qué no está en el realm exportado

El proveedor lleva un Client Secret. Si se exportara el realm con GitHub cargado, el secret saldría enmascarado y el import en otra máquina quedaría roto, o el secreto real terminaría en el repositorio. Por eso se carga en tiempo de ejecución con un script y queda solo en el volumen de Keycloak de cada máquina.

**Nunca exportar el realm después de configurar GitHub (ni Google).**

## Paso 1: crear la OAuth App en GitHub

Lo hace quien administre la cuenta de GitHub del proyecto.

1. GitHub > Settings > Developer settings > OAuth Apps > New OAuth App.
2. Application name: `Seat Reservation TP`.
3. Homepage URL: `http://localhost:3000`.
4. Authorization callback URL, exactamente:

```
http://localhost:8081/realms/seat-reservation/broker/github/endpoint
```

5. Registrar y luego **Generate a new client secret**.

Resultado esperado: GitHub muestra el Client ID y el secret. El secret se ve una sola vez.

Una OAuth App admite una sola callback URL. Al ser `localhost:8081`, sirve en cualquier máquina.

## Paso 2: ejecutar el script

Con el sistema levantado (`docker compose up -d --build`) y Keycloak ya iniciado (cerca de 1 minuto), desde la carpeta `seat-reservation`:

```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/configurar-github.ps1
```

El script pide el Client ID y el Client Secret por consola (el secret no se muestra), elimina espacios al inicio y al final, y registra el proveedor `github` en el realm mediante la API de administración de Keycloak. No guarda las credenciales en ningún archivo.

Resultado esperado: `OK  Proveedor github creado.` (o `actualizado` si ya existía) y la callback URL impresa.

## Paso 3: probar

1. Abrir `http://localhost:3000` en una ventana de incógnito.
2. En el login de Keycloak debe aparecer el botón **GitHub**.
3. Elegirlo y autorizar la aplicación con una cuenta de GitHub.
4. Debe volver al frontend con la sesión iniciada.
5. En el admin de Keycloak (`http://localhost:8081`, admin / admin), realm `seat-reservation`, Users, debe aparecer el usuario federado.
6. Comprobar que `usuario1` y `usuario2` siguen funcionando.

## Qué se probó

- El botón GitHub aparece en el login tras correr el script: [confirmado].
- Login completo con una cuenta de GitHub y vuelta al frontend: [pendiente de confirmar].
- Reserva de un asiento con un usuario de GitHub: [pendiente].
- Username que asigna Keycloak al usuario federado: [pendiente].
- `usuario1` y `usuario2` tras configurar GitHub: [pendiente].

## Cuándo volver a correr el script

La configuración vive en el volumen de Keycloak. Si se ejecuta `docker compose down -v`, se borra y hay que volver a correr el script.

## Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| 404 en `github.com/login/oauth/authorize` con `client_id=+...` en la URL | El Client ID se guardó con un espacio al inicio (el `+` es un espacio codificado) | Volver a correr el script y pegar el Client ID sin espacios |
| Error de `redirect_uri` en GitHub | La callback URL de la OAuth App no es idéntica a la de Keycloak | Verificar que sea exactamente `http://localhost:8081/realms/seat-reservation/broker/github/endpoint`, sin espacios ni barra final |
| `Missing state parameter` en Keycloak | Se abrió la URL del endpoint a mano, o se recargó o volvió atrás durante el login | Empezar de nuevo desde `http://localhost:3000`, en incógnito, tocando el botón GitHub |
| No aparece el botón GitHub | El script no corrió o falló | Volver a correrlo y revisar Identity providers en el admin |
| Keycloak: "Invalid parameter: redirect_uri" antes del login | [Posible volumen viejo de Keycloak con un realm anterior] | `docker compose down -v`, levantar de nuevo y volver a correr el script |

## Seguridad

- El Client Secret de GitHub no va en el repositorio, ni en el frontend, ni en capturas o chats grupales.
- Se entrega por privado a quien lo necesite y solo lo usa Keycloak.
- Quien pruebe necesita una cuenta de GitHub propia.
- No exportar el realm después de configurar GitHub.