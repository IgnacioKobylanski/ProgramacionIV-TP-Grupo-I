// Barra de pasos: Recibida -> Asiento retenido -> Resultado
import type { ReservationStatus } from '../services';

type EstadoPaso = 'hecho' | 'actual' | 'pendiente' | 'error';

// Como se ve cada uno de los 3 pasos segun el estado de la reserva
const MAPA: Record<ReservationStatus, [EstadoPaso, EstadoPaso, EstadoPaso]> = {
  EnProceso: ['hecho', 'actual', 'pendiente'],
  Retenida: ['hecho', 'hecho', 'actual'],
  Confirmada: ['hecho', 'hecho', 'hecho'],
  Rechazada: ['hecho', 'hecho', 'error'],
  Vencida: ['hecho', 'hecho', 'error'],
};

// Texto del ultimo paso: dice "Pago" hasta que llega el resultado
const TITULO_FINAL: Record<ReservationStatus, string> = {
  EnProceso: 'Pago',
  Retenida: 'Pago',
  Confirmada: 'Confirmada',
  Rechazada: 'Rechazada',
  Vencida: 'Vencida',
};

const ICONOS: Partial<Record<EstadoPaso, string>> = { hecho: '✓', error: '✕' };

export function PasosReserva({ status }: { status: ReservationStatus }) {
  const estados = MAPA[status];
  const textos = ['Recibida', 'Asiento retenido', TITULO_FINAL[status]];

  return (
    <ol className="pasos">
      {textos.map((texto, i) => (
        <li key={texto} className={`paso ${estados[i]}`}>
          {/* Hecho = ✓, error = ✕, el resto muestra el numero del paso */}
          <span className="paso-circulo">{ICONOS[estados[i]] ?? i + 1}</span>
          <span className="paso-texto">{texto}</span>
        </li>
      ))}
    </ol>
  );
}