// Llamadas al backend.
import { keycloak } from '../auth/keycloak';
import { API_URL } from '../config';
import type {
  ApiError,
  EventDto,
  MyReservation,
  ReservationCreated,
  ReservationResult,
  SeatApi,
  SeatDto,
} from './types';

async function request<T>(path: string, options: RequestInit = {}, auth = false): Promise<T> {
  const headers: Record<string, string> = {};
  if (options.body) headers['Content-Type'] = 'application/json';

  if (auth) {
    // Sin sesión: ni intentamos renovar, devolvemos 401 como espera ApiError.
    if (!keycloak.authenticated) {
      const error: ApiError = { status: 401 };
      throw error;
    }
    try {
      await keycloak.updateToken(30); // renueva el token si vence en menos de 30 s
    } catch {
      // No se pudo renovar (sesión vencida, Keycloak caído): tratamos como "sin login".
      const error: ApiError = { status: 401 };
      throw error;
    }
    headers.Authorization = `Bearer ${keycloak.token}`;
  }

  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch {
    // Sin conexión o backend apagado
    const error: ApiError = { status: 0 };
    throw error;
  }
  if (!res.ok) {
    const error: ApiError = { status: res.status };
    throw error;
  }
  try {
    return (await res.json()) as T;
  } catch {
    // Respuesta que no es JSON válido: la tratamos como falla del servicio
    const error: ApiError = { status: 500 };
    throw error;
  }}

export const realApi: SeatApi = {
  getEvents: () => request<EventDto[]>('/events'),

  getSeats: (eventId) => request<SeatDto[]>(`/events/${eventId}/seats`),

  createReservation: (eventId, seatId) =>
    request<ReservationCreated>(
      '/reservations',
      { method: 'POST', body: JSON.stringify({ eventId, seatId }) },
      true,
    ),

  getReservation: (requestId) => request<ReservationResult>(`/reservations/${requestId}`, {}, true),

  getMyReservations: () => request<MyReservation[]>('/reservations/mine', {}, true),  

};
