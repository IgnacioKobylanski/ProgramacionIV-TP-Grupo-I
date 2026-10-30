// Pantalla 2 ( ruta: /events/:eventId )
// Muestra la sala del evento: verde = libre, rojo = ocupado, azul = seleccionado.
// Ver los asientos no requiere sesion; para reservar, primero hay que ingresar.

import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api, type ApiError } from '../services';
import { useAuth } from '../auth/AuthContext';
import { Asiento } from '../components/Asiento';
import { Cargando, ErrorMensaje } from '../components/Estados';
import { useAsync } from '../hooks/useAsync';
import { fechaLarga } from '../utils/formato';
import { armarGrilla } from '../utils/grilla';
import { borrarSeleccion, guardarSeleccion, leerSeleccion } from '../utils/seleccion';

export function AsientosPage() {
  const { eventId = '' } = useParams();
  const navigate = useNavigate();
  const { isLogged, login } = useAuth();

  const evento = useAsync(async () => (await api.getEvents()).find((e) => e.id === eventId) ?? null, [eventId]);
  const asientos = useAsync(() => api.getSeats(eventId), [eventId]);
  
  // Al abrir la pantalla, recupera el asiento elegido antes de ir al login (si hay)
  const [seleccionado, setSeleccionado] = useState<string | undefined>(() => leerSeleccion(eventId));
  const [enviando, setEnviando] = useState(false); // evita el doble clic en "Reservar"
  const [errorReserva, setErrorReserva] = useState<ApiError | null>(null);

  const todos = asientos.data;
  const libres = todos?.filter((s) => !s.occupied);
  // Si el asiento recordado ya no esta libre (otro lo reservo), se ignora
  const seleccionValida = libres?.some((s) => s.id === seleccionado) ? seleccionado : undefined;
  const labelSel = libres?.find((s) => s.id === seleccionValida)?.label;

  // Si se toca el mismo asiento de nuevo, se deselecciona
  const elegir = (id: string) => {
    setSeleccionado(id === seleccionValida ? undefined : id);
    setErrorReserva(null);
  };

  const reservar = async () => {
    if (!seleccionValida) return;

    // Sin sesion: guarda el asiento y manda al login. Keycloak lo devuelve a esta misma pantalla
    if (!isLogged) {
      guardarSeleccion(eventId, seleccionValida);
      login();
      return;
    }

    setEnviando(true);
    setErrorReserva(null);
    try {
      // El backend responde enseguida (202) con un requestId; el resultado se consulta en la Pantalla 3
      const { requestId } = await api.createReservation(eventId, seleccionValida);
      borrarSeleccion(eventId);
      navigate(`/reservations/${requestId}`, {
        state: { label: labelSel, eventId, eventName: evento.data?.name },
      });
    } catch (e) {
      setErrorReserva(e as ApiError);
      setEnviando(false);
    }
  };

  return (
    <section>
      <Link to="/" className="volver">← Volver a eventos</Link>

      {evento.data ? (
        <>
          <h2>{evento.data.name}</h2>
          <p className="muted capitalizar">{fechaLarga(evento.data.dateUtc)}</p>
        </>
      ) : (
        <h2>Elegí tu asiento</h2>
      )}

      {asientos.loading && <Cargando texto="Cargando asientos..." />}
      {asientos.error && <ErrorMensaje error={asientos.error} onRetry={asientos.reload} />}

      {todos && libres && (
        <>
          <div className="escenario">ESCENARIO</div>

          <div className="sala">
            {armarGrilla(todos, seleccionValida).map((fila) => (
              <div key={fila.letra} className="fila">
                <span className="fila-label">{fila.letra}</span>
                {fila.asientos.map((a) => (
                  <Asiento key={a.label} asiento={a} onSelect={elegir} />
                ))}
              </div>
            ))}
          </div>

          <div className="leyenda">
            <span><i className="asiento-mini libre" /> Libre</span>
            <span><i className="asiento-mini seleccionado" /> Seleccionado</span>
            <span><i className="asiento-mini ocupado" /> Ocupado</span>
            <button className="btn-link" onClick={asientos.reload}>↻ Actualizar</button>
          </div>

          {libres.length === 0 && <p className="card vacio">No quedan asientos libres para este evento.</p>}
          {errorReserva && <ErrorMensaje error={errorReserva} />}

          {seleccionValida ? (
            <div className="card barra-reserva">
              <span>Asiento <b>{labelSel}</b></span>
              <button className="btn btn-primary" onClick={reservar} disabled={enviando}>
                {!isLogged ? 'Ingresar para reservar' : enviando ? 'Enviando...' : 'Reservar'}
              </button>
            </div>
          ) : (
            libres.length > 0 && <p className="muted ayuda">Tocá un asiento verde para elegirlo.</p>
          )}
        </>
      )}
    </section>
  );
}