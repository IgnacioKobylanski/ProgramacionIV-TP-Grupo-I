import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

// Barra superior: logo y boton de Ingresar o Salir segun la sesion
export function Navbar() {
  const { isLogged, username, login, logout } = useAuth();

  return (
    <header className="navbar">
      <Link to="/" className="logo">🎟️ SeatReserve</Link>
      <div className="navbar-right">
        {isLogged ? (
          <>
            <Link to="/mis-reservas" className="btn btn-outline">Mis reservas</Link>
            <span className="user">👤 {username}</span>
            <button className="btn btn-outline" onClick={logout}>Salir</button>
          </>
        ) : (
          <button className="btn btn-light" onClick={login}>Ingresar</button>
        )}
      </div>
    </header>
  );
}