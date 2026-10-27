<!--Documentacion realizada por Facundo Varela e Isidro Ferrero-->
# Arquitectura de Payment

Payment es el servicio que realiza el cobro de una reserva. Recibe la orden de cobro de Booking, decide si el pago se aprueba o se rechaza, guarda el resultado y lo devuelve a Booking. El cobro es una **simulación**: no se usa dinero real ni una pasarela de pagos externa.

## Guía de inicio

Una vez que *Docker Desktop* esté levantado, abrimos una terminal parados sobre la raíz del proyecto y escribimos:

```powershell
dotnet run --project src/Payment/Payment.Grpc --urls http://localhost:5003/
```

### Configuración necesaria

Estos datos se encuentran en el archivo `appsettings.json` de Payment.Grpc:

| Dato | Para qué sirve | Valor de ejemplo |
| --- | --- | --- |
| Base de datos | Dónde se guardan los pagos | `localhost:5432` |
| Monto máximo | Importe más alto que Payment aprueba | 100000 |
| Keycloak | Dirección del servicio de identificación | `http://localhost:8081` |
| Protocolo | Payment solo atiende llamadas gRPC (HTTP/2) | HTTP/2 |

Cuando se usa Docker, Payment **no se publica hacia afuera**: solo Booking puede llegar a él, por la red interna.

## Autorización y Autenticación

Payment solo acepta llamadas de Booking.

1. Booking se identifica ante *Keycloak* con el nombre `booking-service` y recibe un token.
2. Booking envía ese token junto con la orden de cobro.
3. Payment comprueba el token. Si no es de Booking, rechaza la llamada.

## Flujo del metodo *ChargeReservation*

Payment tiene un único método gRPC, llamado **ChargeReservation** (cobrar reserva).

### Datos que recibe

| Dato | Significado |
| --- | --- |
| reservation_id | Número de la reserva que se quiere cobrar |
| user_id | Usuario que hace la reserva |
| amount_cents | Monto a cobrar, expresado en centavos |
| correlation_id | Código para seguir una misma operación entre todos los servicios |

### Datos que devuelve

| Dato | Significado |
| --- | --- |
| approved | Indica si el cobro fue aprobado (sí o no) |
| payment_id | Número del pago registrado |
| reason | Motivo, solo si fue rechazado |

### Cómo se procesa el cobro

flowchart TD

    classDef io fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1,rx:8px,ry:8px;
    classDef decision fill:#fff8e1,stroke:#f57f17,stroke-width:2px,color:#e65100;
    classDef process fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1.5px,color:#4a148c,rx:6px,ry:6px;
    classDef db fill:#ede7f6,stroke:#4527a0,stroke-width:2px,color:#311b92;
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20,rx:6px,ry:6px;
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c,rx:6px,ry:6px;

    S["<b>Llega la orden de cobro</b><br/><i>Método: ChargeReservation</i><hr/><b>Datos que recibe:</b><br/>• <code>reservation_id</code>: número de reserva<br/>• <code>user_id</code>: usuario que reserva<br/>• <code>amount_cents</code>: monto en centavos<br/>• <code>correlation_id</code>: cód. seguimiento"]:::io

    S --> V{"¿El número de reserva<br/>es válido?"}:::decision

    V -->|"No"| E["<b>Error: dato inválido</b><br/><i>(No se devuelve ningún dato)</i>"]:::error
    
    V -->|"Sí"| M["Se pasa el monto<br/>de centavos a pesos"]:::process

    M --> A{"¿Monto > 0 y<br/>no supera el máximo?"}:::decision

    A -->|"Sí"| OK["<b>Pago Aprobado</b><hr/>• <code>approved</code>: verdadero<br/>• <code>reason</code>: <i>vacío</i>"]:::success
    A -->|"No"| NO["<b>Pago Rechazado</b><hr/>• <code>approved</code>: falso<br/>• <code>reason</code>: monto fuera de rango"]:::error


    OK --> G[("Se guarda el pago")]:::db
    NO --> G

    G --> R["<b>Se responde a Booking</b><br/><i>Método: ChargeReservation</i><hr/><b>Datos que devuelve:</b><br/>• <code>approved</code>: aprobado (sí / no)<br/>• <code>payment_id</code>: nro. pago guardado<br/>• <code>reason</code>: motivo del rechazo"]:::io

Puntos importantes:

- **Sin cobros repetidos:** si llega dos veces la orden de cobro de la misma reserva, Payment no cobra de nuevo y devuelve el resultado que ya había guardado.
- **Registro de auditoría:** Payment anota en el registro del sistema el inicio y el fin de cada cobro, junto con el `correlation_id`.
- **Respuestas posibles:** si el pago se rechaza, la respuesta es igualmente exitosa pero con `approved` en falso y el motivo. Solo se produce un error cuando el número de reserva no es válido.
- **Si Payment no responde:** Booking espera como máximo 5 segundos. Pasado ese tiempo, rechaza la reserva con el motivo "PagoNoDisponible".