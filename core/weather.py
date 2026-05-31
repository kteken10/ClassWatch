"""
Module météo — récupération de la météo courante, lisible et automatique.

Sources, toutes GRATUITES et SANS CLÉ (idéal Streamlit Cloud) :
- météo  : Open-Meteo            (https://open-meteo.com)
- ville  : BigDataCloud reverse  (https://www.bigdatacloud.com) — coordonnées → ville

La position (latitude/longitude) provient de la géolocalisation du navigateur
(gérée côté UI). Ce module ne fait que les appels HTTP + la logique métier
(condition lisible, recommandation de climatisation).
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

from models.schemas import Meteo

_OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
_REVERSE_GEOCODE_URL = "https://api.bigdatacloud.net/data/reverse-geocode-client"
_TIMEOUT_S = 10


class MeteoError(Exception):
    """Erreur lors de la récupération de la météo."""


# --- Codes météo WMO d'Open-Meteo → (icône Material Symbols, description) ------
# Réf. : https://open-meteo.com/en/docs (WMO Weather interpretation codes)
_CODES_WMO: dict[int, tuple[str, str]] = {
    0: ("sunny", "Ciel dégagé"),
    1: ("partly_cloudy_day", "Plutôt dégagé"),
    2: ("partly_cloudy_day", "Partiellement nuageux"),
    3: ("cloud", "Couvert"),
    45: ("foggy", "Brouillard"),
    48: ("foggy", "Brouillard givrant"),
    51: ("rainy", "Bruine légère"),
    53: ("rainy", "Bruine"),
    55: ("rainy", "Bruine dense"),
    56: ("rainy", "Bruine verglaçante"),
    57: ("rainy", "Bruine verglaçante dense"),
    61: ("rainy", "Pluie faible"),
    63: ("rainy", "Pluie"),
    65: ("rainy", "Forte pluie"),
    66: ("rainy", "Pluie verglaçante"),
    67: ("rainy", "Forte pluie verglaçante"),
    71: ("weather_snowy", "Neige faible"),
    73: ("weather_snowy", "Neige"),
    75: ("weather_snowy", "Forte neige"),
    77: ("weather_snowy", "Grains de neige"),
    80: ("rainy", "Averses faibles"),
    81: ("rainy", "Averses"),
    82: ("thunderstorm", "Fortes averses"),
    85: ("weather_snowy", "Averses de neige"),
    86: ("weather_snowy", "Fortes averses de neige"),
    95: ("thunderstorm", "Orage"),
    96: ("thunderstorm", "Orage avec grêle"),
    99: ("thunderstorm", "Orage violent avec grêle"),
}


def _condition_wmo(code: int | None) -> tuple[str, str]:
    """Renvoie (icône Material, description) pour un code météo WMO, avec repli neutre."""
    if code is None:
        return ("thermostat", "Conditions inconnues")
    return _CODES_WMO.get(int(code), ("thermostat", "Conditions variables"))


def reco_climatisation(temperature_c: float) -> tuple[str, str]:
    """
    Recommandation de climatisation selon la température (logique simple, ajustable).

    Renvoie (texte, niveau) où niveau ∈ {success, warning, danger} pour la pastille.
    - >= 28 °C : climatisation recommandée
    - 22–28 °C : climatisation conseillée si inconfort
    - < 22 °C  : climatisation non nécessaire
    """
    if temperature_c >= 28:
        return ("Climatisation recommandée (chaleur élevée).", "danger")
    if temperature_c >= 22:
        return ("Climatisation conseillée en cas d'inconfort.", "warning")
    return ("Climatisation non nécessaire (température confortable).", "success")


def _http_get_json(url: str) -> dict:
    """GET JSON avec timeout et User-Agent ; lève en cas d'échec."""
    req = urllib.request.Request(url, headers={"User-Agent": "ClassWatch/1.0"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_ville(latitude: float, longitude: float) -> str | None:
    """
    Reverse-geocoding : coordonnées → nom lisible 'Ville, Pays'.

    Best effort : renvoie None en cas d'échec (sans casser la météo).
    """
    params = {
        "latitude": f"{latitude:.4f}",
        "longitude": f"{longitude:.4f}",
        "localityLanguage": "fr",
    }
    try:
        data = _http_get_json(f"{_REVERSE_GEOCODE_URL}?{urllib.parse.urlencode(params)}")
    except Exception:
        return None

    # On prend le niveau le plus parlant disponible.
    ville = (
        data.get("city")
        or data.get("locality")
        or data.get("principalSubdivision")
        or None
    )
    pays = data.get("countryName")
    # BigDataCloud (fr) ajoute l'article entre parenthèses : "France (la)" → "France".
    if pays and "(" in pays:
        pays = pays.split("(")[0].strip()
    if ville and pays:
        return f"{ville}, {pays}"
    return ville or pays


def get_meteo(latitude: float, longitude: float) -> Meteo:
    """
    Récupère la météo courante (+ ville lisible) pour des coordonnées.

    Raises:
        MeteoError : en cas d'échec réseau / réponse invalide sur la météo.
        (Le nom de ville, lui, est facultatif : son échec ne bloque pas.)
    """
    params = {
        "latitude": f"{latitude:.4f}",
        "longitude": f"{longitude:.4f}",
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code",
    }
    url = f"{_OPEN_METEO_URL}?{urllib.parse.urlencode(params)}"

    try:
        data = _http_get_json(url)
    except Exception as e:
        raise MeteoError(f"Échec de récupération météo : {e}") from e

    current = data.get("current")
    if not current or "temperature_2m" not in current:
        raise MeteoError("Réponse météo inattendue (pas de données 'current').")

    temperature = float(current["temperature_2m"])
    ressenti = current.get("apparent_temperature")
    humidite = current.get("relative_humidity_2m")
    icone, description = _condition_wmo(current.get("weather_code"))
    reco_txt, reco_niveau = reco_climatisation(temperature)

    return Meteo(
        latitude=latitude,
        longitude=longitude,
        temperature_c=temperature,
        ressenti_c=float(ressenti) if ressenti is not None else None,
        humidite_pct=int(humidite) if humidite is not None else None,
        ville=get_ville(latitude, longitude),
        description=description,
        icone=icone,
        reco_climatisation=reco_txt,
        clim_niveau=reco_niveau,
    )
