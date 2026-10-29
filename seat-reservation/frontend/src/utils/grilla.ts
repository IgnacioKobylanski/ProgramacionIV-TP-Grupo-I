// La API devuelve TODOS los asientos del evento, y occupied indica si están tomados.
// La sala depende del evento (filas y asientos por fila distintos), así que la grilla
// se arma con lo que viene: una fila por cada letra del label (A1 → fila A).
import type { SeatDto } from '../services';

export type EstadoAsiento = 'libre' | 'ocupado' | 'seleccionado';

export interface AsientoVista {
  label: string;
  id?: string; // solo los libres tienen id (son los únicos reservables)
  estado: EstadoAsiento;
}

export interface FilaVista {
  letra: string;
  asientos: AsientoVista[];
}

// "A10" → 10
function numeroDe(label: string): number {
  return Number(label.slice(1));
}

export function armarGrilla(asientos: SeatDto[], seleccionadoId?: string): FilaVista[] {
  // 1. Agrupa los asientos por letra de fila
  const porFila = new Map<string, SeatDto[]>();
  for (const s of asientos) {
    const letra = s.label[0];
    porFila.set(letra, [...(porFila.get(letra) ?? []), s]);
  }

  // 2. Ordena las filas por letra y los asientos de cada fila por número (A2 antes que A10)
  return [...porFila.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([letra, deLaFila]) => ({
      letra,
      asientos: deLaFila
        .sort((a, b) => numeroDe(a.label) - numeroDe(b.label))
        .map((s): AsientoVista => {
          if (s.occupied) return { label: s.label, estado: 'ocupado' };
          return {
            label: s.label,
            id: s.id,
            estado: s.id === seleccionadoId ? 'seleccionado' : 'libre',
          };
        }),
    }));
}