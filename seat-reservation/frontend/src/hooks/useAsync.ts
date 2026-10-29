import { useCallback, useEffect, useState, type DependencyList } from 'react';
import type { ApiError } from '../services';

export function useAsync<T>(fn: () => Promise<T>, deps: DependencyList) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(true);
  const [intento, setIntento] = useState(0);
  const cargar = useCallback(fn, deps);

  useEffect(() => {
    let activo = true;
    setData(null);
    setLoading(true);
    setError(null);
    cargar()
      .then((d) => activo && setData(d))
      .catch((e: ApiError) => activo && setError(e))
      .finally(() => activo && setLoading(false));
    return () => {
      activo = false;
    };
  }, [cargar, intento]);

  return { data, error, loading, reload: () => setIntento((n) => n + 1) };
}
