# Historial de prompts – Nicolás Ferreyra

**Materia:** Programación IV – UTN  
**Proyecto:** Sistema de reserva de asientos – Grupo 1  
**Área de trabajo:** Microservicio Notifications y documentación de arquitectura

## 1. Comprensión del microservicio Notifications

**Consulta realizada:**

> ¿Cuál es la responsabilidad del microservicio Notifications dentro del sistema de reserva de asientos y cómo se comunica con Booking?

**Objetivo:** Comprender el funcionamiento del microservicio y su participación en el flujo de confirmación de reservas.

## 2. Análisis de la implementación

**Consulta realizada:**

> Revisemos la implementación de Notifications en .NET, sus endpoints, la persistencia con PostgreSQL y cómo se registran las notificaciones.

**Objetivo:** Analizar la estructura del servicio y verificar que sus responsabilidades estén correctamente identificadas.

## 3. Prevención de notificaciones duplicadas

**Consulta realizada:**

> ¿Cómo funciona la idempotencia en Notifications y qué papel cumple el identificador `ReservationId` para evitar registros duplicados?

**Objetivo:** Comprender el mecanismo utilizado para evitar múltiples notificaciones asociadas a una misma reserva.

## 4. Pruebas locales

**Consulta realizada:**

> ¿Cómo puedo probar los endpoints de Notifications y comprobar que las notificaciones se guardan correctamente en PostgreSQL?

**Objetivo:** Guiar las pruebas locales del servicio, incluyendo el registro, la consulta y la prevención de duplicados.

## 5. Autenticación con Keycloak

**Consulta realizada:**

> ¿Cómo afecta la incorporación de Keycloak al acceso a los endpoints de Notifications y qué pruebas deberían realizarse?

**Objetivo:** Revisar los requisitos de autenticación y autorización incorporados al proyecto.

## 6. Documentación de arquitectura

**Consulta realizada:**

> Ayudame a revisar y organizar el documento `docs/arq-notifications.md` para que explique la arquitectura, los endpoints, la persistencia, la idempotencia y la comunicación con Booking.

**Objetivo:** Elaborar una documentación técnica clara y consistente con la implementación del proyecto.

## 7. Validación final de la documentación

**Consulta realizada:**

> Revisemos si el documento de arquitectura de Notifications está completo y si hay afirmaciones que todavía requieren pruebas.

**Objetivo:** Diferenciar las funcionalidades verificadas localmente de aquellas cuya integración completa todavía no había sido validada.

---

## Uso de inteligencia artificial

La inteligencia artificial se utilizó como herramienta de apoyo para comprender la arquitectura del microservicio Notifications, analizar su funcionamiento, orientar las pruebas locales y elaborar la documentación técnica.

Las respuestas se contrastaron con el código y las pruebas disponibles. La IA no reemplazó la verificación de las funcionalidades ni el trabajo de integración realizado por el equipo.

**Documento relacionado:** `docs/arq-notifications.md`.