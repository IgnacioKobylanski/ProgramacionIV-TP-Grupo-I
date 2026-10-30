import { Route, Routes } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { AsientosPage } from './pages/AsientosPage';
import { EventosPage } from './pages/EventosPage';
import { ReservaPage } from './pages/ReservaPage';
import { MisReservasPage } from './pages/MisReservasPage';

export default function App() {
  return (
    <>
      <Navbar />
      <main className="contenido">
        <Routes>
          <Route path="/" element={<EventosPage />} />
          <Route path="/events/:eventId" element={<AsientosPage />} />
          <Route path="/reservations/:requestId" element={<ReservaPage />} />
          <Route path="/mis-reservas" element={<MisReservasPage />} />
          <Route path="*" element={<p>Página no encontrada.</p>} />
        </Routes>
      </main>
    </>
  );
}
