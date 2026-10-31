# Pruebas de RabbitMQ

## Objetivo

Verificar el funcionamiento del broker RabbitMQ utilizado por el sistema de reserva de asientos, especialmente la conexión de los consumidores y el tratamiento de mensajes inválidos.

## Entorno de pruebas

- Fecha: 30/10/2026.
- Sistema operativo: Windows.
- Ejecución mediante Docker Desktop y Docker Compose.
- Broker: RabbitMQ 4 con interfaz de administración.
- Exchange: `grupo1-booking`.
- Cola principal: `booking`.
- Cola de mensajes fallidos: `booking.dead`.
- Dos réplicas del microservicio Booking.

Las pruebas se realizaron en un entorno local, independiente del utilizado por los demás integrantes del grupo.

## Prueba RAB-01: Verificar consumidores de Booking

**Objetivo:** comprobar que las dos réplicas de Booking estén conectadas a la misma cola de RabbitMQ.

**Procedimiento:**

1. Iniciar los servicios mediante Docker Compose.
2. Verificar que RabbitMQ esté funcionando.
3. Ejecutar el siguiente comando:

```bash
docker compose exec rabbitmq rabbitmqctl list_queues name messages consumers
```

**Resultado esperado:**

- La cola `booking` debe presentar dos consumidores.
- La cola `booking.dead` debe existir.

**Resultado obtenido:**

```text
name          messages  consumers
booking.dead  0         0
booking       0         2
```

**Estado: APROBADA.**

Se comprobó que las dos réplicas de Booking estaban conectadas como consumidores de la cola `booking`.

## Prueba RAB-02: Tratamiento de mensaje inválido

**Objetivo:** comprobar que un mensaje que no contiene un JSON válido termine en la cola `booking.dead`.

**Procedimiento:**

1. Ingresar al panel de administración de RabbitMQ en `http://localhost:15672/`.
2. Abrir la sección Exchanges.
3. Seleccionar el exchange `grupo1-booking`.
4. Publicar el siguiente contenido:

```text
ESTE MENSAJE NO ES UN JSON VALIDO
```

5. Consultar las colas mediante:

```bash
docker compose exec rabbitmq rabbitmqctl list_queues name messages consumers
```

6. Ingresar a la cola `booking.dead` desde el panel de RabbitMQ.
7. Consultar el mensaje almacenado sin eliminarlo.

**Resultado esperado:**

El mensaje inválido debe terminar en la cola `booking.dead`.

**Resultado obtenido:**

La consulta mostró:

```text
name          messages  consumers
booking.dead  1         0
```

Posteriormente, desde el panel de administración, se verificó que el contenido del mensaje almacenado era:

```text
ESTE MENSAJE NO ES UN JSON VALIDO
```

**Estado: APROBADA.**

Se comprobó que el mensaje inválido terminó en la cola de mensajes fallidos.

## Conclusiones

Las dos pruebas ejecutadas obtuvieron los resultados esperados:

- RabbitMQ registró dos consumidores conectados a la cola principal `booking`.
- Un mensaje inválido publicado en el exchange `grupo1-booking` terminó en la cola `booking.dead`.

Estas pruebas verifican aspectos específicos del broker. No sustituyen las pruebas funcionales del proceso completo de reserva ni las pruebas de los demás microservicios.

## Evidencias

Se conservaron capturas locales del panel de RabbitMQ correspondientes a la cola `booking.dead` y al contenido del mensaje inválido. No se incorporaron imágenes al repositorio.
