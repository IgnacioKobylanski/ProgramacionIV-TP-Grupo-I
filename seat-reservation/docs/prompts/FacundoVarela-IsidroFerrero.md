# Historial de prompts: Facundo Varela e Isidro Ferrero

Herramientas: Codex - ChatGPT. Google Gemini-Argo. Claude-Sonnet.

Componentes trabajados: documentación y diagrama de APIs.

# 1. Documentación y comparación - Availability.Api
Realizamos una documentación del nodo completo, registrando la entrada de datos, flujo y respuestas. Le pedimos a la IA que compare nuestra documentación con el código de manera que podamos cerciorarnos de que registramos el flujo de manera precisa y completa, y que agregue o modifique los detalles que nos hayamos pasado por alto. Posteriormente, se le solicitó a ChatGPT que nos realice un diagrama de la API basandose en la documentación realizada. 

# 2. Documentación y comparación - Booking.Api

Se realizo una documentacion hecha a mano, luego mandada dentro de un prompt a Gemini Argo con la instruccion de buscar errores de ortografia.

Se volvio a pedir asistencia en el armado del grafico con mermaid debido a la disconformidad con el diagrama de la API elegido en primera instancia.

# 3. Documentación y comparación - Payment.Grpc

Se documento en primera instancia a mano el gRPC. Luego se solicito contribucion a Claude Sonnet para la correccion eficiente de errores de ortografia. 
Por otro lado, se le pidio al mismo modelo sugerencias de informacion faltante sobre el flujo de datos dentro del servicio.

Armado de grafico con mermaid con la asistencia de Gemini Argo indicando los atributos de la respuesta y el metodo que es llamado. 
