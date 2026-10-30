// Pantalla 3 ( ruta: /reservations/:requestId )
// Muestra el estado de la reserva. La reserva es asincronica: el backend la procesa
// por detras (RabbitMQ -> Booking -> Payment), asi que esta pantalla consulta
// el estado cada 1 segundo hasta que llega un resultado final.

import { Link, useLocation, useParams } from 'react-router-dom';
import { Cargando, ErrorMensaje } from '../components/Estados';
import { EstadoBadge } from '../components/EstadoBadge';
import { PasosReserva } from '../components/PasosReserva';
import { useReservationStatus } from '../hooks/useReservationStatus';

// Datos que manda la Pantalla 2 al navegar (se pierden si se recarga la pagina)
interface EstadoNavegacion {
  label?: string;     // asiento, por ejemplo "A5"
  eventId?: string;   // para el boton "Elegir otro asiento"
  eventName?: string;
}

export function ReservaPage() {
  const { requestId } = useParams();
  const info = (useLocation().state as EstadoNavegacion | null) ?? {};
  // timedOut: pasaron 30 s sin resultado final y se dejo de consultar
  const { result, error, timedOut, loading } = useReservationStatus(requestId);

  // Si la reserva no salio, se ofrece elegir otro asiento
  const fallo = result?.status === 'Rechazada' || result?.status === 'Vencida';

  return (
    <section>
      <h2>Tu reserva</h2>
      <p className="muted">Se actualiza sola cada 1 segundo hasta tener un resultado.</p>

      <div className="card reserva">
        {loading && <Cargando texto="Consultando tu reserva..." />}
        {error && <ErrorMensaje error={error} />}

        {result && (
          <>
            <EstadoBadge status={result.status} reason={result.reason} />
            {(info.eventName || info.label) && (
              <p className="muted">
                {[info.eventName, info.label && `Asiento ${info.label}`].filter(Boolean).join(' · ')}
              </p>
            )}
            <PasosReserva status={result.status} />
          </>
        )}

        {timedOut && (
          <div className="mensaje-error">
            Está tardando más de lo normal. Recargá la página en unos segundos para ver el resultado.
          </div>
        )}

        <div className="detalle">
          {info.label && <div><span>Asiento</span><b>{info.label}</b></div>}
          {result && <div><span>Estado</span><b>{result.status}</b></div>}
          <div><span>N° de solicitud</span><code>{requestId}</code></div>
        </div>
      </div>

      <div className="acciones">
        {fallo && info.eventId && (
          <Link to={`/events/${info.eventId}`} className="btn btn-primary">Elegir otro asiento</Link>
        )}
        <Link to="/" className="volver">← Volver a eventos</Link>
      </div>
    </section>
  );
}