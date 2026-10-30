// Recuerda el asiento elegido mientras el usuario va al login de Keycloak y vuelve.
// (sessionStorage puede fallar en modo privado: por eso el try/catch)
const clave = (eventId: string) => `asiento-elegido-${eventId}`;

export function guardarSeleccion(eventId: string, seatId: string) {
  try { sessionStorage.setItem(clave(eventId), seatId); } catch { /* sin storage: no pasa nada */ }
}

export function leerSeleccion(eventId: string): string | undefined {
  try { return sessionStorage.getItem(clave(eventId)) ?? undefined; } catch { return undefined; }
}

export function borrarSeleccion(eventId: string) {
  try { sessionStorage.removeItem(clave(eventId)); } catch { /* nada */ }
}
