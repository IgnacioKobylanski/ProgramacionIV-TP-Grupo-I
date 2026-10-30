// Un asiento de la grilla. El color sale de la clase CSS (libre / ocupado / seleccionado).
import type { AsientoVista } from '../utils/grilla';

interface Props {
  asiento: AsientoVista;
  onSelect: (id: string) => void;
}

export function Asiento({ asiento, onSelect }: Props) {
  return (
    <button
      className={`asiento ${asiento.estado}`}
      disabled={asiento.estado === 'ocupado'}
      // Los ocupados no tienen id, asi que no se pueden seleccionar
      onClick={() => asiento.id && onSelect(asiento.id)}
      title={asiento.estado === 'ocupado' ? 'Ocupado' : `Asiento ${asiento.label}`}
    >
      {asiento.label}
    </button>
  );
}