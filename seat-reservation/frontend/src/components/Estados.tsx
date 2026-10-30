// Mensajes reutilizables de carga y de error
import type { ApiError } from '../services';
import { useAuth } from '../auth/AuthContext';

export function Cargando({ texto = 'Cargando…' }: { texto?: string }) {
  return (
    <div className="cargando">
      <span className="spinner" /> {texto}
    </div>
  );
}

export function ErrorMensaje({ error, onRetry }: { error: ApiError; onRetry?: () => void }) {
  const { login } = useAuth();

  // 401: falta iniciar sesion, se ofrece ingresar en lugar de reintentar
  if (error.status === 401) {
    return (
      <div className="mensaje-error">
        Tenés que iniciar sesión para ver esto.
        <button className="btn btn-primary" onClick={login}>Ingresar</button>
      </div>
    );
  }

  // status 0: no hubo respuesta (servicio caido o sin conexion)
  const texto =
    error.status === 404
      ? 'No encontramos lo que buscabas.'
      : error.status >= 500 || error.status === 0
        ? 'El servicio no está disponible en este momento.'
        : `Ocurrió un error (código ${error.status}).`;

  return (
    <div className="mensaje-error">
      {texto}
      {onRetry && error.status !== 404 && (
        <button className="btn btn-primary" onClick={onRetry}>Reintentar</button>
      )}
    </div>
  );
}