import { createContext, useContext, useEffect, useState } from 'react'

const Ctx = createContext(null)
export const useApp = () => useContext(Ctx)

const LS_JOURNAL = 'classwatch.journal'
const LS_DARK = 'classwatch.dark'
const LS_KEY = 'classwatch.apikey'

function load(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback } catch { return fallback }
}

export function AppStateProvider({ children }) {
  const [journal, setJournal] = useState(() => load(LS_JOURNAL, []))
  const [weather, setWeather] = useState(null)
  const [dark, setDark] = useState(() => localStorage.getItem(LS_DARK) === '1')
  // Clé : override localStorage > variable d'environnement de build.
  const [apiKey, setApiKey] = useState(
    () => localStorage.getItem(LS_KEY) || import.meta.env.VITE_GEMINI_API_KEY || '',
  )

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem(LS_DARK, dark ? '1' : '0')
  }, [dark])

  useEffect(() => { localStorage.setItem(LS_JOURNAL, JSON.stringify(journal)) }, [journal])

  const saveKey = (k) => {
    setApiKey(k)
    if (k) localStorage.setItem(LS_KEY, k)
    else localStorage.removeItem(LS_KEY)
  }

  const value = {
    journal,
    addEntry: (e) => setJournal((j) => [...j, e]),
    clearJournal: () => setJournal([]),
    weather, setWeather,
    dark, setDark,
    apiKey, saveKey,
    hasKey: Boolean(apiKey),
  }
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}
