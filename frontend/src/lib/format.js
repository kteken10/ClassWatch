// Helpers de présentation (tons, dates, %, aplatissement journal).
export const GRAVITE_TONE = { faible: 'success', moyen: 'warning', 'élevé': 'danger' }
export const GRAVITE_COLOR = { faible: '#10b981', moyen: '#f59e0b', 'élevé': '#f43f5e' }
export const GRAVITE_ORDRE = { faible: 1, moyen: 2, 'élevé': 3 }

export const NIVEAU_TONE = { 'succès': 'success', info: 'neutral', alerte: 'warning', danger: 'danger' }
export const NIVEAU_DOT = { 'succès': '#10b981', info: '#94a3b8', alerte: '#f59e0b', danger: '#f43f5e' }

export const pct = (x) => `${Math.round((x || 0) * 100)}%`

export function gravMax(incidents = []) {
  return incidents.reduce(
    (m, i) => (GRAVITE_ORDRE[i.severite] > (GRAVITE_ORDRE[m] || 0) ? i.severite : m),
    '—',
  )
}

export function fmtDate(iso, withSeconds = false) {
  if (!iso) return '—'
  const d = new Date(iso)
  const date = d.toLocaleDateString('fr-FR')
  const time = d.toLocaleTimeString('fr-FR', {
    hour: '2-digit', minute: '2-digit', ...(withSeconds ? { second: '2-digit' } : {}),
  })
  return `${date} ${time}`
}

export function lignesIncidents(entries) {
  const out = []
  for (const e of entries) {
    for (const inc of e.result.incidents || []) {
      out.push({
        entreeId: e.id, horodatage: e.horodatage, source: e.source, image: e.nomImage,
        type: inc.type, severite: inc.severite, confiance: inc.confiance, description: inc.description,
      })
    }
  }
  return out
}

export const WEATHER_ICON = {
  Sun: 'Sun', CloudSun: 'CloudSun', Cloud: 'Cloud', CloudFog: 'CloudFog',
  CloudRain: 'CloudRain', CloudSnow: 'CloudSnow', CloudLightning: 'CloudLightning',
  Thermometer: 'Thermometer',
}
