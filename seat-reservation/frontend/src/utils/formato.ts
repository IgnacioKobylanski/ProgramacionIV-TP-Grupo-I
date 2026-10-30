export const fechaLarga = (iso: string) =>
  new Date(iso).toLocaleString('es-AR', { weekday: 'long', day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit', hour12: false }) + ' hs';

export const dia = (iso: string) => new Date(iso).getDate();
export const mesCorto = (iso: string) => new Date(iso).toLocaleString('es-AR', { month: 'short' }).replace('.', '');
