// Refleja lo que devuelve Availability (ver AvailabilityService.cs en el backend).

export interface EventDto {
  id: string;
  name: string;
  dateUtc: string; // texto ISO; convertir con new Date(dateUtc)
}

// GET /events/{id}/seats devuelve TODOS los asientos; occupied indica si está tomado.
export interface SeatDto {
  id: string;
  label: string; // "A1" … "B10"
  occupied: boolean;  
}

export interface ReservationCreated {
  requestId: string;
  correlationId: string;
}

export type ReservationStatus =
  | 'EnProceso'
  | 'Retenida'
  | 'Confirmada'
  | 'Rechazada'
  | 'Vencida';

export type RejectionReason = 'AsientoOcupado' | 'PagoFallido' | 'PagoNoDisponible';

export interface ReservationResult {
  requestId: string;
  status: ReservationStatus;
  reason: RejectionReason | null;
}

export interface ApiError {
  status: number; // 0 sin conexión · 401 sin login · 404 no existe · 503 servicio caído
}

// Interfaz que implementa api.ts.
export interface SeatApi {
  getEvents(): Promise<EventDto[]>;
  getSeats(eventId: string): Promise<SeatDto[]>;
  createReservation(eventId: string, seatId: string): Promise<ReservationCreated>;
  getReservation(requestId: string): Promise<ReservationResult>;
}

export const FINAL_STATUSES: ReservationStatus[] = ['Confirmada', 'Rechazada', 'Vencida'];
