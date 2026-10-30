import type { RejectionReason, ReservationStatus } from '../services';
// Icono, texto y clase CSS (color) de cada estado de la reserva
const ESTADOS: Record<ReservationStatus, { icono: string; texto: string; clase: string }> = {
  EnProceso: { icono: '⏳', texto: 'Procesando tu solicitud...', clase: 'estado-proceso' },
  Retenida: { icono: '🔒', texto: 'Asiento retenido, procesando el pago...', clase: 'estado-retenida' },
  Confirmada: { icono: '✅', texto: '¡Reserva confirmada!', clase: 'estado-ok' },
  Rechazada: { icono: '❌', texto: 'La reserva fue rechazada', clase: 'estado-error' },
  Vencida: { icono: '⌛', texto: 'La retención venció, intentá de nuevo', clase: 'estado-vencida' },
};

const MOTIVOS: Record<RejectionReason, string> = {
  AsientoOcupado: 'Otro usuario reservó ese asiento',
  PagoFallido: 'El pago fue rechazado',
  PagoNoDisponible: 'El servicio de pago no está disponible',
};

interface Props {
  status: ReservationStatus;
  reason: RejectionReason | null; // solo viene cuando la reserva fue Rechazada
}

export function EstadoBadge({ status, reason }: Props) {
  const { icono, texto, clase } = ESTADOS[status];

  return (
    <div className={`estado ${clase}`}>
      <div className="estado-icono">{icono}</div>
      <h3>{texto}</h3>
      {reason && <p>{MOTIVOS[reason]}</p>}
    </div>
  );
}