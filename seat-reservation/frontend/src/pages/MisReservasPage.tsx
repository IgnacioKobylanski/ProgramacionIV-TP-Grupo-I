// Pantalla: Mis reservas ( /mis-reservas )
// Trae todas las reservas del usuario logueado y las filtra por estado en el front.
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAsync } from '../hooks/useAsync';
import { api, type ReservationStatus } from '../services';

type Filtro = ReservationStatus | 'Todas';
const FILTROS: Filtro[] = ['Todas', 'Confirmada', 'Retenida', 'Rechazada', 'Vencida'];

export function MisReservasPage() {
  const { data, error, loading } = useAsync(() => api.getMyReservations(), []);
  const [filtro, setFiltro] = useState<Filtro>('Todas');

  if (loading) return <p className="cargando">Cargando tus reservas…</p>;
  if (error?.status === 401) return <p className="mensaje-error">Tenés que iniciar sesión para ver tus reservas.</p>;
  if (error) return <p className="mensaje-error">No se pudieron cargar tus reservas. Reintentá en unos segundos.</p>;

  const reservas = data ?? [];
  const visibles = filtro === 'Todas' ? reservas : reservas.filter((r) => r.status === filtro);

  return (
    <section>
      <h2>Mis reservas</h2>

      <div className="filtros">
        {FILTROS.map((f) => (
          <button
            key={f}
            className={f === filtro ? 'btn btn-primary' : 'btn btn-outline'}
            onClick={() => setFiltro(f)}
          >
            {f}
          </button>
        ))}
      </div>

      {reservas.length === 0 && <p className="muted">Todavía no hiciste reservas.</p>}
      {reservas.length > 0 && visibles.length === 0 && <p className="muted">No hay reservas con ese estado.</p>}

      {visibles.map((r) => (
        <article key={r.requestId} className="card">
          <h3>{r.eventName}</h3>
          <span className="muted">
            {new Date(r.eventDateUtc).toLocaleString('es-AR', { dateStyle: 'full', timeStyle: 'short' })}
          </span>
          <div className="detalle">
            <div><span>Asiento</span><b>{r.seatLabel}</b></div>
            <div><span>Estado</span><b>{r.status}</b></div>
          </div>
          <Link to={`/reservations/${r.requestId}`} state={{ label: r.seatLabel }} className="btn btn-primary">
            Ver detalle →
          </Link>
        </article>
      ))}

      <Link to="/" className="volver">← Volver a eventos</Link>
    </section>
  );
}