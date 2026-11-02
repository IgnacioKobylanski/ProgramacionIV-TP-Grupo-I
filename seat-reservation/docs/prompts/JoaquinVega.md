## Historial de prompts: Joaquín Vega

**Herramienta:** Claude (Anthropic)  
**Componentes trabajados:** Testing del proyecto Seat Reservation.

---

# Prompt 1: Generación de casos de prueba

Estoy trabajando como tester en un proyecto llamado **Seat Reservation**, que cuenta con un backend encargado de gestionar reservas de asientos.

Necesito realizar pruebas sobre el backend desde el rol de tester. Quiero que me propongas entre **20 y 40 casos de prueba**, cubriendo diferentes tipos de escenarios y no solamente el flujo exitoso.

Organizá las pruebas por categorías, por ejemplo:

- Validación de entradas y contrato de la API.
- Reglas de negocio relacionadas con las reservas.
- Estados y flujos asincrónicos.
- Concurrencia y solicitudes simultáneas.
- Comunicación entre microservicios y tolerancia a fallos.
- Seguridad y manejo de datos.

Para cada prueba, indicá:

1. **Qué se debería probar.**
2. **Qué comportamiento se espera del sistema.**
3. **Qué problema o comportamiento incorrecto permitiría detectar esa prueba.**
4. **Por qué es importante realizarla.**

También incluí casos límite y situaciones de error, como datos inválidos, recursos inexistentes, solicitudes duplicadas, fallos de servicios, problemas de concurrencia y estados inconsistentes.

El objetivo es obtener una lista de pruebas que pueda utilizar como guía durante el testing real del backend y que me permita detectar y documentar posibles errores del sistema.

---

# Prompt 2: Generación de scripts para el bloque A

Generame los scripts necesarios para poder realizar estas 8 pruebas iniciales sobre el backend. Los scripts deben permitir ejecutar cada caso de prueba de forma clara y reproducible, indicando qué solicitud se realiza, qué datos se envían y qué respuesta se espera obtener.

Las pruebas a cubrir son:

1. Crear reserva con payload válido.
2. Body vacío o JSON malformado.
3. Campos obligatorios ausentes.
4. Tipos de datos incorrectos.
5. Valores límite.
6. Strings largos o con caracteres especiales.
7. IDs que no existen.
8. Verbo HTTP incorrecto.

Organizá los scripts de manera que pueda identificar fácilmente a qué prueba corresponde cada uno y utilizarlos para comprobar el comportamiento del backend.

---

## Script generado para el bloque A

**Archivo:** `tests_back_bloque_A.py`

El script fue generado en Python para ejecutar las ocho pruebas correspondientes al bloque A.

Permite ejecutar todas las pruebas o seleccionar casos específicos mediante parámetros de línea de comandos.

La configuración utilizada en el script corresponde al backend real del proyecto y fue verificada previamente, incluyendo:

- URL y puerto del backend.
- Endpoint utilizado para crear reservas.
- Estructura real del JSON.
- Nombres reales de los campos.
- Autenticación mediante Keycloak.
- Configuración utilizada para obtener el token de autenticación. 

El script implementa los ocho casos de prueba definidos para este bloque y permite seleccionar pruebas individuales mediante `--only`.

---

# Prompt 3: Solicitud de documentación de los tests

**Objetivo del prompt:**

Solicité generar la **documentación formal de los tests realizados**, separando esta información del registro de prompts y del código de los scripts.

La documentación debía permitir registrar, para cada prueba:

1. Qué se prueba.
2. Resultado esperado.
3. Problema que permite detectar.
4. Importancia de la prueba.
5. Resultado inicial de la ejecución.
6. Observaciones o errores encontrados.
7. Corrección realizada.
8. Re-test realizado.
9. Resultado final.
10. Observaciones finales.

También se estableció que, cuando una prueba detecte un error, se debe conservar el resultado inicial y documentar el ciclo:

**Prueba inicial → Resultado → Error detectado → Corrección → Re-test → Resultado final**

De esta manera, la documentación permite evidenciar tanto el trabajo de testing como la posterior verificación de las correcciones realizadas.

### Resultado

Se generó el archivo:

**`documentacion-tests.md`**

Este archivo contiene la documentación de los casos de prueba del backend de **Seat Reservation**, incluyendo los resultados obtenidos, los errores encontrados, las correcciones aplicadas y los re-tests correspondientes.

---
# Prompt 4: Generación de scripts para el Bloque B

**Prompt utilizado:**

> Generame los scripts necesarios para poder realizar las pruebas correspondientes al **Bloque B: Reglas de negocio** sobre el backend.
>
> Las pruebas a cubrir son:
>
> 9. Reservar un asiento libre.
> 10. Reservar un asiento ya reservado.
> 11. Varios asientos en solicitudes consecutivas.
> 12. Mismo asiento reservado dos veces por el mismo usuario.
> 13. Reservas sobre eventos y asientos inválidos, pago rechazado y vencimiento.
>
> Los scripts deben permitir ejecutar cada prueba de forma clara y reproducible y registrar el resultado obtenido para poder documentarlo posteriormente.

### Resultado

Se generó el script:

**`tests_back_bloque_B.py`**

El script contiene las pruebas correspondientes al Bloque B y permite ejecutarlas individualmente o en conjunto.

# Próximos prompts

Para cada bloque restante se generará un prompt específico destinado a obtener los scripts necesarios para ejecutar las pruebas correspondientes.


## Bloque C

> [Agregar aquí el prompt utilizado para generar los scripts del bloque C]

**Script generado:**  
> [Nombre del archivo]

## Bloque D

> [Agregar aquí el prompt utilizado para generar los scripts del bloque D]

**Script generado:**  
> [Nombre del archivo]

## Bloque E

> [Agregar aquí el prompt utilizado para generar los scripts del bloque E]

**Script generado:**  
> [Nombre del archivo]

## Bloque F

> [Agregar aquí el prompt utilizado para generar los scripts del bloque F]

**Script generado:**  
> [Nombre del archivo]

---

# Mi aporte

Mi aporte en el proceso consistió en utilizar los prompts para obtener herramientas y casos de prueba que permitieran realizar el testing del backend del proyecto.

Las tareas realizadas incluyen:

- Definir junto con la herramienta los escenarios a probar.
- Analizar los casos de prueba generados.
- Solicitar scripts para ejecutar las pruebas de forma reproducible.
- Verificar que los scripts correspondan al funcionamiento real del backend.
- Ejecutar las pruebas correspondientes.
- Analizar los resultados obtenidos.
- Detectar y documentar errores.
- Informar los errores encontrados.
- Realizar nuevamente las pruebas luego de las correcciones.
- Verificar los resultados finales.

Este archivo funciona como **historial del proceso de trabajo y de los prompts utilizados**, mientras que los resultados y la documentación detallada de las pruebas se encuentran en `backend-tests.md`.