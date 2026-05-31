import { useState } from 'react'
import * as Icons from 'lucide-react'
import { MapPin, Droplets, Navigation, Loader2 } from 'lucide-react'
import { useApp } from '../context/AppState'
import { getWeather } from '../lib/weather'

const RECO_DOT = { success: '#10b981', warning: '#f59e0b', danger: '#f43f5e' }

export function WeatherWidget() {
  const { weather, setWeather } = useApp()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const locate = () => {
    setError(null)
    if (!navigator.geolocation) { setError('Géolocalisation non supportée.'); return }
    setLoading(true)
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try { setWeather(await getWeather(pos.coords.latitude, pos.coords.longitude)) }
        catch (e) { setError(e.message) }
        finally { setLoading(false) }
      },
      () => { setError('Position refusée.'); setLoading(false) },
      { enableHighAccuracy: false, timeout: 10000 },
    )
  }

  if (!weather) {
    return (
      <div className="px-3">
        <button
          onClick={locate} disabled={loading}
          className="w-full inline-flex items-center justify-center gap-2 h-9 rounded-lg border border-line bg-surface text-sm font-medium text-ink hover:border-accent-500 hover:text-accent-700 transition-colors disabled:opacity-60"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Navigation className="w-4 h-4" />}
          Activer la météo
        </button>
        {error && <p className="text-[11px] text-rose-500 mt-1.5 px-1">{error}</p>}
      </div>
    )
  }

  const WIcon = Icons[weather.icone] || Icons.Thermometer
  return (
    <div className="mx-3 rounded-xl border border-line bg-surface p-3">
      <div className="flex items-center gap-2.5">
        <WIcon className="w-7 h-7 text-accent-600 shrink-0" strokeWidth={1.75} />
        <div className="min-w-0">
          <div className="text-sm font-semibold text-ink truncate">{weather.description}</div>
          <div className="text-xs text-muted tnum">
            {Math.round(weather.temperature_c)} °C
            {weather.ressenti_c != null && <> · ressenti {Math.round(weather.ressenti_c)} °C</>}
          </div>
        </div>
        {weather.humidite_pct != null && (
          <span className="ml-auto inline-flex items-center gap-1 text-xs text-muted tnum">
            <Droplets className="w-3.5 h-3.5 text-faint" />{weather.humidite_pct}%
          </span>
        )}
      </div>
      {weather.ville && (
        <div className="mt-2 flex items-center gap-1 text-xs text-muted">
          <MapPin className="w-3.5 h-3.5 text-faint" />{weather.ville}
        </div>
      )}
      <div className="mt-2.5 pt-2.5 border-t border-line-soft flex items-center gap-2 text-xs text-ink">
        <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: RECO_DOT[weather.clim_niveau] || '#94a3b8' }} />
        {weather.reco_climatisation}
      </div>
    </div>
  )
}
