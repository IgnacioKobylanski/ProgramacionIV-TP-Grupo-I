# Historial de prompts: Nelly Burgos

Herramienta: Claude (Anthropic). Componentes trabajados: estructura inicial del frontend.

## 1. Creación del proyecto
- Prompt: consulté los comandos para crear la estructura del front y levantarlo en local antes de subirlo al repo.
- Qué se usó: `npm create vite` con plantilla React + TypeScript.
- Mi aporte: creé el proyecto dentro de `seat-reservation`, lo levanté y verifiqué el placeholder en el navegador, antes de subirlo, revisé con `git status` que no se incluyera `node_modules`.

## 2. Conexión provisoria con Availability
- Prompt: consulté cómo conectar el frontend con Availability para ver datos reales, y cómo levantar el backend sin el connection string de Azure.
- Qué se usó: `App.tsx` provisorio que llama a `GET /events` en `localhost:5001`, usando el CORS del backend.
- Mi aporte: levanté el backend con el override, para hacerlo sin el connection string de Azure, y verifiqué que el frontend mostrara los 3 eventos reales.