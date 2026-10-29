// Configuración del frontend

export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:5001';

export const KEYCLOAK_CONFIG = {
  url: import.meta.env.VITE_KEYCLOAK_URL ?? 'http://localhost:8081',
  realm: 'seat-reservation',
  clientId: 'seat-web',
};

// Polling del estado de la reserva
export const POLL_INTERVAL_MS = 1000;
export const POLL_TIMEOUT_MS = 30000;
