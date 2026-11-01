# Historial de prompts: Facundo Varela e Isidro Ferrero

Herramientas: Codex - ChatGPT. Google Gemini-Argon. Claude-Sonnet.

Componentes trabajados: documentación y diagrama de APIs.

# 1. Documentación y comparación - Availability.Api
Realizamos una documentación del nodo completo, registrando la entrada de datos, flujo y respuestas. Le pedimos a la IA que compare nuestra documentación con el código de manera que podamos cerciorarnos de que registramos el flujo de manera precisa y completa, y que agregue o modifique los detalles que nos hayamos pasado por alto. Posteriormente, se le solicitó a ChatGPT que nos realice un diagrama de la API basandose en la documentación realizada. 

# 2. Documentación y comparación - Booking.Api

Se realizo una documentacion hecha a mano, luego mandada dentro de un prompt a Gemini Argon con la instruccion de buscar errores de ortografia.

Se volvio a pedir asistencia en el armado del grafico con mermaid debido a la disconformidad con el diagrama de la API elegido en primera instancia.

# 3. Documentación y comparación - Payment.Grpc

Se documento en primera instancia a mano el gRPC. Luego se solicito contribucion a Claude Sonnet para la correccion eficiente de errores de ortografia. 
Por otro lado, se le pidio al mismo modelo sugerencias de informacion faltante sobre el flujo de datos dentro del servicio.

Armado de grafico con mermaid con la asistencia de Gemini Argon indicando los atributos de la respuesta y el metodo que es llamado. 

# 4. Modificaciones en los diagramas de arquitecturas de las APIS

Se analizaron los cambios con respecto al nuevo servicio de mensajería, y se le solicitó a la IA que realizara las modificaciones en los diagramas con respecto a las referencias a Microsoft Azure Service Bus, y las cambie por RabbitMQ 

# 5. Actualizacion de documentacion de endpoint de Availability.Api y Booking.Api

Se agrego a la documentacion el nuevo endpoint en Availability.Api y Booking.Api. Se le pidio a Claude asistencia en el nuevo armado de diagramas con mermaid.
Tambien se solicito asistencia para que explique el flujo entero de ese endpoint dentro del proyecto.