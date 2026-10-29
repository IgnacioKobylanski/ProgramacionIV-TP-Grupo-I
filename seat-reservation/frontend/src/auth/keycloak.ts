// Requisito: en el realm, el cliente "seat-web" tiene que aceptar http://localhost:5173 y http://localhost:3000 

import Keycloak from 'keycloak-js';
import { KEYCLOAK_CONFIG } from '../config';

export const keycloak = new Keycloak(KEYCLOAK_CONFIG);

// Se llama UNA sola vez desde main.tsx, antes de renderizar.
export function initKeycloak(): Promise<boolean> {
  return keycloak.init({
    onLoad: 'check-sso', // no obliga a loguearse: ver eventos y asientos es público
    pkceMethod: 'S256',
  });
}
