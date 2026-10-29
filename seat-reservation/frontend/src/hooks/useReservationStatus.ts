// Consulta el estado de una reserva cada 1 s hasta que llegue un estado final
// (Confirmada, Rechazada o Vencida) o pasen 30 s.
import { useEffect, useState } from 'react';
import { POLL_INTERVAL_MS, POLL_TIMEOUT_MS } from '../config';
import { api, FINAL_STATUSES, type ApiError, type ReservationResult } from '../services';

export function useReservationStatus(requestId: string | undefined) {
  const [result, setResult] = useState<ReservationResult | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [timedOut, setTimedOut] = useState(false);

useEffect(() => {
  if (!requestId) return;
  setResult(null);
  setError(null);
  setTimedOut(false);

  let activo = true;
  let timer: ReturnType<typeof setTimeout>;
  const inicio = Date.now();

  const consultar = async () => {
    try {
      const r = await api.getReservation(requestId);
      if (!activo) return;
      setResult(r);
      if (FINAL_STATUSES.includes(r.status)) return;
    } catch (e) {
      if (!activo) return;
      const err = e as ApiError;
      const transitorio = err.status === 0 || err.status >= 500;
      if (!transitorio) {
        setError(err); // 401/404: no reintentar
        return
    }
    if (Date.now() - inicio > POLL_TIMEOUT_MS) {
      setTimedOut(true);
      return;
    }}
    timer = setTimeout(consultar, POLL_INTERVAL_MS);
  };

  consultar();
  return () => {
    activo = false;
    clearTimeout(timer);
  };
}, [requestId]);

  const loading = !result && !error && !timedOut;
  return { result, error, timedOut, loading };
}
