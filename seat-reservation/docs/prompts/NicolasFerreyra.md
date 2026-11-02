# Historial de prompts: Nicolás Ferreyra

Herramienta: ChatGPT (OpenAI). Componentes trabajados: Notifications, referencia del plan y documentación técnica del frontend.

## 1. Comprensión del microservicio Notifications
- **Prompts:** consulté cuál era la responsabilidad de Notifications y cómo se comunicaba con Booking.
- **Qué se usó:** explicación del flujo de confirmación y del envío de avisos mediante una llamada HTTP desde Booking.
- **Mi aporte:** analicé el lugar que ocupa Notifications dentro del sistema y distinguí su función de la de los demás microservicios.

## 2. Análisis de la implementación de Notifications
- **Prompts:** pedí revisar la estructura del servicio en .NET, sus endpoints y la persistencia con PostgreSQL.
- **Qué se usó:** revisión de la API mínima, del registro de notificaciones y de las responsabilidades de sus componentes.
- **Mi aporte:** revisé el funcionamiento del servicio para poder explicarlo y documentarlo de forma consistente con la implementación.

## 3. Idempotencia y notificaciones duplicadas
- **Prompts:** pregunté cómo se evita registrar varias notificaciones para una misma reserva y qué función cumple `ReservationId`.
- **Qué se usó:** explicación de la idempotencia y del índice único por `ReservationId`.
- **Mi aporte:** identifiqué por qué el sistema debe tolerar solicitudes repetidas sin duplicar registros y lo incorporé a la documentación de Notifications.

## 4. Pruebas locales de Notifications
- **Prompts:** consulté cómo probar los endpoints y comprobar la persistencia y la prevención de duplicados.
- **Qué se usó:** orientación para revisar respuestas HTTP, registros de la base de datos y comportamiento ante solicitudes repetidas.
- **Mi aporte:** utilicé estas indicaciones para revisar el servicio y diferenciar las comprobaciones locales de la integración completa del sistema.

## 5. Autenticación y autorización de Notifications
- **Prompts:** pregunté cómo afectaba Keycloak al acceso a Notifications y qué debía tenerse en cuenta para sus endpoints.
- **Qué se usó:** explicación de los tokens JWT y de la autorización para las llamadas internas desde Booking.
- **Mi aporte:** revisé cómo debía describirse la seguridad del servicio sin confundir el acceso de usuarios con la comunicación entre microservicios.

## 6. Documentación de arquitectura de Notifications
- **Prompts:** pedí ayuda para organizar y revisar `docs/arq-notifications.md`, incluyendo endpoints, persistencia, idempotencia y comunicación con Booking.
- **Qué se usó:** sugerencias de estructura, claridad técnica y consistencia entre secciones.
- **Mi aporte:** trabajé en la documentación de arquitectura de Notifications y revisé que sus explicaciones coincidieran con el funcionamiento del proyecto.

## 7. Revisión final de la documentación
- **Prompts:** consulté si la documentación de Notifications estaba completa y qué afirmaciones necesitaban verificarse.
- **Qué se usó:** revisión de coherencia y distinción entre funcionalidades implementadas, probadas y pendientes de validación.
- **Mi aporte:** revisé el documento antes de compartirlo con el equipo, prestando atención a no presentar como comprobado algo que aún no estuviera validado.

## 8. Actualización de la referencia del plan
- **Prompts:** pedí ayuda para contrastar `docs/referencia-del-plan.md` con la arquitectura actual y con el README general, especialmente tras el cambio de Azure Service Bus a RabbitMQ.
- **Qué se usó:** revisión de los servicios, el broker, el flujo de reservas, los estados, la consistencia eventual y Keycloak.
- **Mi aporte:** trabajé en la actualización de la referencia del plan y revisé su coherencia con las decisiones vigentes del equipo.

## 9. Documentación técnica del frontend
- **Prompts:** consulté cómo organizar `docs/documentacion-frontend.md`, explicar las rutas, componentes y comunicación con Availability, y diferenciarlo del `frontend/README.md`.
- **Qué se usó:** asistencia para estructurar el documento, revisar las explicaciones del flujo de reserva y representar interacciones mediante Mermaid.
- **Mi aporte:** elaboré y revisé la documentación técnica del frontend, corregí descripciones y comprobé que no duplicara innecesariamente el README de instalación.

## 10. Autenticación del frontend con Keycloak y Google
- **Prompts:** pedí explicaciones sobre Keycloak, el inicio de sesión con Google, los tokens JWT y el flujo Authorization Code con PKCE.
- **Qué se usó:** explicación del cliente `seat-web`, de la autenticación de usuarios y de las solicitudes protegidas a Availability.
- **Mi aporte:** revisé la forma de explicar la autenticación en la documentación del frontend y la diferencié de la autenticación entre servicios.

---

## Uso de inteligencia artificial

Utilicé ChatGPT como apoyo para comprender conceptos técnicos, contrastar documentación y revisar la claridad de las explicaciones. Mi trabajo se centró en el análisis y la documentación; la IA no sustituyó la revisión del proyecto ni las decisiones tomadas por el equipo.
