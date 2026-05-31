import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// App 100% front : pas de backend, donc pas de proxy. Tout (Gemini, météo,
// annotation, journal) tourne dans le navigateur.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
})
