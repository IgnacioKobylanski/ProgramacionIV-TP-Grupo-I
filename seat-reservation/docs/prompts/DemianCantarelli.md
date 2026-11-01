# Historial de prompts: Demian Cantarelli

Herramienta: Codex - ChatGPT (OpenAI).

Trabajo realizado: análisis de la consigna, la implementación y la arquitectura del trabajo práctico, propuesta de tabla de componentes y documentación del frontend. Este historial se actualizará con las solicitudes y los cambios posteriores.

## 1. Análisis del estado inicial del trabajo práctico

- Prompts: pedí un análisis completo del código y la documentación del proyecto, tomando la consigna del PDF como referencia, para conocer el estado del trabajo y los pendientes sin modificar archivos.
- Qué se usó: la consigna de `Trabajo_practico.pdf`, el código de Availability, Booking, Payment y Notifications, el frontend, la configuración de infraestructura, los scripts de ejecución y prueba, y la documentación del repositorio.
- Resultado: se elaboró un informe en el chat que compara lo solicitado con lo implementado y describe la arquitectura, el flujo de reservas, los pendientes de interfaz y documentación, y las limitaciones del manejo de fallos. La revisión fue estática: no se modificaron archivos, no se compilaron proyectos ni se ejecutaron servicios o pruebas funcionales.
- Mi aporte: solicité una revisión integral antes de comenzar las modificaciones, proporcioné la consigna como referencia y definí que esta primera etapa debía limitarse al análisis del estado existente.

## 2. Análisis de la arquitectura del proyecto

- Prompts: pedí un análisis completo de la arquitectura actual como preparación para realizar, en el siguiente paso, un diagrama general y una tabla general de componentes.
- Qué se usó: la estructura y las referencias de los proyectos, los puntos de entrada de las APIs, los contratos compartidos, los adaptadores de comunicación, los procesos de Booking, la persistencia, la configuración de Keycloak y Docker Compose, y los documentos generales existentes.
- Resultado: se analizaron las responsabilidades y capas de cada servicio, las comunicaciones HTTP, gRPC y por Azure Service Bus, la propiedad de los datos, la autenticación, la concurrencia, la consistencia eventual y el despliegue. También se identificaron los límites de recuperación ante fallos y los elementos que deben representarse con precisión en el próximo diagrama. La revisión fue estática; no se modificaron el código ni los documentos del diagrama y la tabla existentes.
- Mi aporte: definí el objetivo de la documentación general y pedí comprender primero la arquitectura implementada para que el diagrama y la tabla posteriores reflejen el estado real del proyecto.

## 3. Comprensión y comparación del diagrama general del equipo

- Prompts: pedí comprender la primera versión del diagrama general realizada por un compañero y compararla con la arquitectura implementada, como base para preparar la tabla general de componentes y mantener la documentación ante futuras funcionalidades de frontend, backend o nuevos microservicios.
- Qué se usó: `docs/diagrama-general.md`, la tabla de componentes existente, los endpoints y políticas de autorización, el publicador y consumidor de Service Bus, las integraciones entre servicios, el frontend y Docker Compose.
- Resultado: se verificó que el diagrama representa las comunicaciones principales del backend y la zona de consistencia eventual. Se identificaron precisiones para su evolución: distinguir el cliente HTTP del frontend aún sin integración, aclarar las réplicas de Booking, diferenciar la emisión de tokens de su validación y mantener separadas la vista lógica y la de despliegue. También se reconoció la tabla existente como base para el próximo paso. No se modificaron el diagrama, la tabla ni el código.
- Mi aporte: propuse continuar sobre el trabajo compartido del equipo y preparar una documentación que pueda acompañar la incorporación de nuevas funcionalidades sin describir como implementadas conexiones o capacidades futuras.

## 4. Elaboración de una propuesta de tabla general de componentes

- Prompts: pedí una tabla general de componentes con la estructura del punto 1 de la consigna: componente, rol y justificación de su participación en el sistema. Solicité una redacción concreta, acorde con la arquitectura actual y que pudiera ser revisada por un compañero para detectar errores o proponer cambios.
- Qué se usó: el análisis de arquitectura, el diagrama general del equipo y la tabla existente como referencia para describir el cliente HTTP, los cuatro microservicios, Azure Service Bus, Keycloak y las bases de datos de cada servicio.
- Resultado: se elaboró en el chat una propuesta de tabla con las responsabilidades y justificaciones de los componentes, aclarando que las cuatro bases comparten un servidor PostgreSQL y que el frontend todavía no está integrado al flujo. El archivo de la tabla ya estaba subido y no se modificó en este paso.
- Mi aporte: definí la estructura y el nivel de detalle de la tabla, y establecí como criterio de elección que la versión propuesta representara la arquitectura actual y pudiera revisarse con mi compañero antes de incorporar cambios.

## 5. Primera versión del README del frontend

- Prompts: pedí una primera versión del README del frontend, tomando como guía el formato de la documentación existente e incluyendo los pasos necesarios para entender su funcionamiento, ejecución, puertos y componentes.
- Qué se usó: el README general y las guías del proyecto, las pantallas y rutas de React, los componentes, hooks y utilidades, el cliente HTTP, la integración con Keycloak, los contratos de Availability, la configuración de Vite y Nginx, las dependencias y Docker Compose.
- Resultado: se reemplazó el README inicial de la plantilla por una guía en español con requisitos, ejecución con Docker y Vite, puertos, configuración, autenticación, pantallas, flujo de reservas, seguimiento automático, endpoints, estructura, componentes, verificación manual y problemas frecuentes. La documentación refleja el frontend integrado actual y el backend con RabbitMQ; no se modificó el código ni el README general. La revisión se basó en los archivos del proyecto, sin ejecutar pruebas funcionales.
- Mi aporte: definí que el documento debía explicar el frontend completo y conservar un formato compatible con la documentación del equipo, como primera versión para revisión y ajustes posteriores.
