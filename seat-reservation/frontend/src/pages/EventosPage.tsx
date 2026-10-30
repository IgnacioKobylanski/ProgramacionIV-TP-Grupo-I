// Pantalla 1 ( ruta: / )
// Muestra la lista de eventos con la cantidad de asientos libres de cada uno.

import { Link } from 'react-router-dom';
import { api, type EventDto } from '../services';
import { Cargando, ErrorMensaje } from '../components/Estados';
import { useAsync } from '../hooks/useAsync';
import { dia, fechaLarga, mesCorto } from '../utils/formato';

interface EventoConLibres extends EventDto {
  libres: number | null; // null = no se pudo saber (por ejemplo, si Booking no responde)
}
// Pide los eventos y, para cada uno, sus asientos para contar los libres.
// Promise.all hace esas consultas en paralelo.
async function cargarEventos(): Promise<EventoConLibres[]> {
  const eventos = await api.getEvents();
  return Promise.all(
    eventos.map(async (ev) => {
      try {
        const asientos = await api.getSeats(ev.id);
        return { ...ev, libres: asientos.filter((s) => !s.occupied).length };
      } catch {
        // Si falla la consulta de asientos, el evento se muestra igual pero sin el contador
        return { ...ev, libres: null };
      }
    }),
  );
}

export function EventosPage() {
  const { data: eventos, error, loading, reload } = useAsync(cargarEventos, []);

  return (
    <section>
      <h2>Próximos eventos</h2>
      <p className="muted">Elegí un evento para ver los asientos disponibles. No hace falta iniciar sesión.</p>

      {loading && <Cargando texto="Cargando eventos..." />}
      {error && <ErrorMensaje error={error} onRetry={reload} />}
      {eventos?.length === 0 && <p className="card vacio">No hay eventos disponibles por ahora.</p>}

      {eventos?.map((ev) => (
        <article key={ev.id} className="card evento">
          <div className="fecha">
            <b>{dia(ev.dateUtc)}</b>
            <small>{mesCorto(ev.dateUtc)}</small>
          </div>

          <div className="evento-info">
            <h3>{ev.name}</h3>
            <span className="muted capitalizar">{fechaLarga(ev.dateUtc)}</span>
            {ev.libres !== null && (
              <span className={`pill ${ev.libres === 0 ? 'pill-agotado' : ''}`}>
                {ev.libres === 0 ? 'Agotado' : `${ev.libres} asientos libres`}
              </span>
            )}
          </div>

          <Link to={`/events/${ev.id}`} className="btn btn-primary">Ver asientos →</Link>
        </article>
      ))}
    </section>
  );
}