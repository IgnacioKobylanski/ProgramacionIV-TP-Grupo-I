import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import App from "./App";
import "./styles/index.css";
import { initKeycloak } from "./auth/keycloak";

initKeycloak()
  // Ver eventos y asientos es público: si Keycloak falla, la app arranca igual sin sesión.
  .catch((error) => console.error("No se pudo iniciar sesion: ", error))
  .then(() => {
    createRoot(document.getElementById("root")!).render(
      <StrictMode>
        <BrowserRouter>
          <AuthProvider>
            <App />
          </AuthProvider>
        </BrowserRouter>
      </StrictMode>
    );
  });