import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Toaster } from 'sonner'
import './index.css'
import App from './App.jsx'
import { AppStateProvider } from './context/AppState'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppStateProvider>
      <App />
      <Toaster position="top-right" toastOptions={{ style: { fontFamily: 'Inter, sans-serif' } }} />
    </AppStateProvider>
  </StrictMode>,
)
