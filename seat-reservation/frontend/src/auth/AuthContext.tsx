import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { keycloak } from './keycloak';

interface AuthContextValue {
  isLogged: boolean;
  username?: string;
  login: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLogged, setIsLogged] = useState(!!keycloak.authenticated);
  const [username, setUsername] = useState<string | undefined>(
    keycloak.tokenParsed?.preferred_username as string | undefined,
  );

  useEffect(() => {
    const cerrarSesion = () => {
      setIsLogged(false);
      setUsername(undefined);
    };
    keycloak.onAuthLogout = cerrarSesion;
    keycloak.onAuthRefreshError = cerrarSesion;
    return () => {
      keycloak.onAuthLogout = undefined;
      keycloak.onAuthRefreshError = undefined;
    };
  }, []);

  const value: AuthContextValue = {
    isLogged,
    username,
    login: () => keycloak.login({ redirectUri: window.location.href }),
    logout: () => keycloak.logout({ redirectUri: window.location.origin }),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth tiene que usarse dentro de <AuthProvider>');
  return ctx;
}
