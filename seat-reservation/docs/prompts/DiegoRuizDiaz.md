# Historial de prompts: Diego Ruiz Diaz

Herramienta: Claude (Anthropic) / Gemini. 
Componentes trabajados: Creación iterativa de la documentación principal, diagramas y manual de ejecución (`README.md`) e índice de navegación del proyecto.

## 1. Documentación de la Arquitectura Base
- **Prompts:** Comparti la estructura base con los servicios Availability y Payment y le pedi que arme la estructura inicial del README y diseñe la tabla de componentes de arquitectura.
- **Qué se usó:** Formato Markdown estándar para los títulos principales y una tabla para definir los roles de cada microservicio.
- **Mi aporte:** Revisé la tabla generada para asegurarme de que los puertos (5001 para Availability y 5003 para Payment) y los estilos arquitectónicos (Clean Architecture y N-Layer) fueran exactamente los que estábamos usando en el código.

## 2. Diagrama de Arquitectura y Service Bus 
- **Prompts:** Solicité que cree un diagrama visual de la arquitectura.
- **Qué se usó:** Un bloque de código `mermaid` (graph TD) para generar el diagrama visual de las interacciones entre los microservicios, el broker y las bases de datos.
- **Mi aporte:** Modifiqué los nodos del diagrama para que reflejaran correctamente el patrón de publicación/suscripción (PUBLISH/SUBSCRIBE). También agregue la redaccion de las decisiones de diseño sobre la consistencia eventual y los estados de la reserva (Retenida, Confirmada, Rechazada y Vencida).

## 3. Notificaciones y Flujos de Prueba
- **Prompts:** Solicité que me detalle paso a paso cómo levantar la infraestructura con Docker y cómo estructurar los comandos para los flujos de prueba en consola.
- **Qué se usó:** Listas ordenadas para los requisitos y bloques de código `powershell` para ilustrar los comandos de ejecución (como `docker compose up -d` e `Invoke-RestMethod`).
- **Mi aporte:** Ejecuté los scripts de PowerShell (`./scripts/levantar-servicios.ps1`) para verificar que la sintaxis documentada funcionara correctamente. 

## 4. Autenticación, Secretos y Limitaciones
- **Prompts:** Solicité que explique cómo funciona la autenticación entre servicios, cómo manejar los secretos fuera del repositorio y a redactar las limitaciones conocidas del proyecto.
- **Qué se usó:** Listas de viñetas para las decisiones de diseño y las limitaciones, junto con texto en negrita para resaltar credenciales de desarrollo y rutas de directorios (estructura del repositorio).
- **Mi aporte:** Agregue la advertencia sobre no subir el string de conexión de Azure al repositorio y se documentó manualmente las limitaciones conocidas del sistema, como la falta de validación de la audiencia en los tokens JWT y la degradación en caso de que Notifications falle al confirmar.

## 5 Integración de Docker, Frontend y Troubleshooting
- **Prompts:** Solicité que actualice la sección de ejecución para recomendar docker compose up -d --build, añadir el Frontend a la arquitectura y estructurar una tabla de "Problemas frecuentes".   
- **Qué se usó:** Una tabla en Markdown para esquematizar los síntomas y soluciones de la sección "Problemas frecuentes", junto con bloques de 
código powershell actualizados que incluyen el uso de Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force.   
- **Mi aporte:**  Revisé las soluciones de la tabla de problemas frecuentes para garantizar su claridad, como recomendar docker compose down -v si el realm de Keycloak cambia sin reflejarse. También documenté el funcionamiento de las réplicas de Booking en Docker, verificando que los mensajes se repartan 
en los logs como booking-1 y booking-2.  

## 6. Migración a RabbitMQ, Google OAuth y Reorganización
- **Prompts:** Solicité actualizar el diagrama Mermaid, eliminar las referencias a los scripts de secretos, redactar la nueva configuración de mensajería y estructurar la tabla final de integrantes y responsabilidades.
- **Qué se usó:** Actualización de sintaxis en el bloque `mermaid` para los nodos del exchange de RabbitMQ. Uso de enlaces Markdown `[texto](ruta)` para indexar la documentación en listas, y creación de tablas Markdown para roles y responsabilidades.
- **Mi aporte:** Verifiqué la eliminación de las dependencias de Azure en la sección de ejecución para simplificar el despliegue con Docker. Se agregó la advertencia de seguridad sobre no incluir el `Client Secret` de Google en Git, y estructuré la tabla de integrantes asegurándome de plasmar cada responsabilidad.

## 7. Creación del Índice de Navegación
- **Prompts:** Solicité la creación de un archivo `README.md` que funcione como un mapa o punto de entrada principal, que incluya una guía de inicio rápido con Docker, una tabla con todas las credenciales de desarrollo y enlaces organizados a toda la documentación, infraestructura y código fuente.
- **Qué se usó:** Tablas en Markdown para estructurar claramente las credenciales, la documentación y los módulos de código. Enlaces relativos (`[texto](ruta)`) para conectar este índice con el resto de los archivos del repositorio (como `README.md`). Bloques de código `bash` para los comandos de inicio rápido.
- **Mi aporte:** Estructuré la información teniendo en cuenta un orden lógico (cómo levantar el sistema y las credenciales). Apliqué formato Markdown para jerarquizar los títulos, estructurar el texto y organizar la información en tablas. Además, verifiqué manualmente que todos los puertos descritos (`3000` para frontend, `8081` para Keycloak, `15672` para RabbitMQ) y las rutas de los archivos coincidieran exactamente con la estructura real del repositorio.

## 8. Actualización del README del Backend
- **Prompts:** " Solicité que actualice el README del backend, que documente los nuevos endpoints que agregamos (`GET /reservations/mine`), la configuración de variables de entorno y los 3 eventos sembrados en `DbSeeder.cs`."
- **Qué se usó:** Tablas Markdown y bloques de código Mermaid para documentar la arquitectura.
- **Mi aporte:** Verifiqué que la documentación en general como que incluyera los endpoints que no estaban documentados, el detalle de la lógica de siembra de datos y restructure el punto Autenticación con Google mediante Keycloake.

## 9. Corrección del README índice
- **Prompts:** Solicité que actualizara el índice general del proyecto, que corrija los enlaces rotos hacia la carpeta de testing, que incorpore el ingreso a traves de Acceso web en desarrollo Vite (5173)."
- **Qué se usó:** Enlaces relativos en Markdown (`[texto](ruta)`). Flujo completo de control de versiones (`git add`, `git commit`, `git push`).
- **Mi aporte:** Controle el documento en general, que estuvieran correctos los enalces generados, y corregi la descripcion del fronted.

