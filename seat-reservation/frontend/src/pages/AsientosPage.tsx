import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api, type ApiError, type SeatDto } from '../services';
import { useAuth } from '../auth/AuthContext';
import { Asiento } from '../components/Asiento';
import { armarGrilla } from '../utils/grilla';

export function AsientosPage() {
  const { eventId = '' } = useParams();
  const navigate = useNavigate();
  const { isLogged, login } = useAuth();

  const [asientos, setAsientos] = useState<SeatDto[] | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [seleccionado, setSeleccionado] = useState<string>();
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    api.getSeats(eventId).then(setAsientos).catch((e: ApiError) => setError(e));
  }, [eventId]);

  const reservar = async () => {
    if (!seleccionado) return;
    if (!isLogged) {
      login(); // va a Keycloak y vuelve a esta página
      return;
    }
    setEnviando(true);
    try {
      const { requestId } = await api.createReservation(eventId, seleccionado);
      const label = asientos?.find((s) => s.id === seleccionado)?.label;
      navigate(`/reservations/${requestId}`, { state: { label } });
    } catch (e) {
      setError(e as ApiError);
      setEnviando(false);
    }
  };

  if (error?.status === 404) return <p className="mensaje-error">El evento no existe.</p>;
  if (error) return <p className="mensaje-error">El servicio no está disponible. Reintentá en unos segundos.</p>;
  if (!asientos) return <p className="cargando">Cargando asientos…</p>;

  const grilla = armarGrilla(asientos, seleccionado);
  const labelSel = asientos.find((s) => s.id === seleccionado)?.label;

  return (
    <section>
      <Link to="/" className="volver">← Volver a eventos</Link>
      <h2>Elegí tu asiento</h2>

      <div className="escenario">ESCENARIO</div>

      {grilla.map((fila) => (
        <div key={fila.letra} className="fila">
          <span className="fila-label">{fila.letra}</span>
          {fila.asientos.map((a) => (
            <Asiento key={a.label} asiento={a} onSelect={setSeleccionado} />
          ))}
        </div>
      ))}

      <div className="leyenda">
        <span><i className="asiento-mini libre" /> Libre</span>
        <span><i className="asiento-mini seleccionado" /> Seleccionado</span>
        <span><i className="asiento-mini ocupado" /> Ocupado</span>
      </div>

      {seleccionado && (
        <div className="card barra-reserva">
          <span>Asiento <b>{labelSel}</b></span>
          <button className="btn btn-primary" onClick={reservar} disabled={enviando}>
            {isLogged ? (enviando ? 'Enviando…' : 'Reservar') : 'Ingresar para reservar'}
          </button>
        </div>
      )}
    </section>
  );
}