// Météo 100% navigateur : Open-Meteo (météo) + BigDataCloud (ville). Sans clé.
const WMO = {
  0: ['Sun', 'Ciel dégagé'], 1: ['CloudSun', 'Plutôt dégagé'], 2: ['CloudSun', 'Partiellement nuageux'],
  3: ['Cloud', 'Couvert'], 45: ['CloudFog', 'Brouillard'], 48: ['CloudFog', 'Brouillard givrant'],
  51: ['CloudRain', 'Bruine légère'], 53: ['CloudRain', 'Bruine'], 55: ['CloudRain', 'Bruine dense'],
  56: ['CloudRain', 'Bruine verglaçante'], 57: ['CloudRain', 'Bruine verglaçante dense'],
  61: ['CloudRain', 'Pluie faible'], 63: ['CloudRain', 'Pluie'], 65: ['CloudRain', 'Forte pluie'],
  66: ['CloudRain', 'Pluie verglaçante'], 67: ['CloudRain', 'Forte pluie verglaçante'],
  71: ['CloudSnow', 'Neige faible'], 73: ['CloudSnow', 'Neige'], 75: ['CloudSnow', 'Forte neige'],
  77: ['CloudSnow', 'Grains de neige'], 80: ['CloudRain', 'Averses faibles'], 81: ['CloudRain', 'Averses'],
  82: ['CloudLightning', 'Fortes averses'], 85: ['CloudSnow', 'Averses de neige'],
  86: ['CloudSnow', 'Fortes averses de neige'], 95: ['CloudLightning', 'Orage'],
  96: ['CloudLightning', 'Orage avec grêle'], 99: ['CloudLightning', 'Orage violent avec grêle'],
}

function reco(temp) {
  if (temp >= 28) return ['Climatisation recommandée (chaleur élevée).', 'danger']
  if (temp >= 22) return ["Climatisation conseillée en cas d'inconfort.", 'warning']
  return ['Climatisation non nécessaire (température confortable).', 'success']
}

async function getVille(lat, lon) {
  try {
    const r = await fetch(
      `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=fr`,
    )
    const d = await r.json()
    const ville = d.city || d.locality || d.principalSubdivision || null
    let pays = d.countryName || null
    if (pays && pays.includes('(')) pays = pays.split('(')[0].trim()
    return ville && pays ? `${ville}, ${pays}` : ville || pays
  } catch {
    return null
  }
}

export async function getWeather(lat, lon) {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat.toFixed(4)}&longitude=${lon.toFixed(4)}`
    + `&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Météo indisponible.')
  const data = await res.json()
  const c = data.current
  if (!c || c.temperature_2m == null) throw new Error('Réponse météo inattendue.')

  const [icone, description] = WMO[c.weather_code] || ['Thermometer', 'Conditions variables']
  const [reco_climatisation, clim_niveau] = reco(c.temperature_2m)
  const ville = await getVille(lat, lon)

  return {
    latitude: lat, longitude: lon,
    temperature_c: c.temperature_2m,
    ressenti_c: c.apparent_temperature ?? null,
    humidite_pct: c.relative_humidity_2m ?? null,
    ville, description, icone, reco_climatisation, clim_niveau,
  }
}
