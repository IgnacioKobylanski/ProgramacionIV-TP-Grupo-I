import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// CORS habilitado para localhost:5173 y localhost:3000.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, strictPort: true },
})