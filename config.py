"""
Gestion centralisée de la configuration et des clés API.

Règle d'or : AUCUNE clé en dur dans le code.
Les clés sont lues, par ordre de priorité :
  1. st.secrets  (déploiement Streamlit Community Cloud)
  2. variables d'environnement / fichier .env (développement local)

Le fichier .env fourni par l'utilisateur a une syntaxe non standard ; on lit
donc plusieurs noms de variables possibles pour rester tolérant.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

# Charge le fichier .env local s'il existe (ignoré en prod Streamlit Cloud).
load_dotenv()

# Noms de variables acceptés pour la clé Gemini (du plus standard au plus tolérant).
_GEMINI_KEY_NAMES = ["GEMINI_API_KEY", "GOOGLE_API_KEY", "Gemini_Key", "GEMINI_KEY"]
_ANTHROPIC_KEY_NAMES = ["ANTHROPIC_API_KEY", "Anthropic_Key", "ANTHROPIC_KEY"]

# Modèle de vision Gemini par défaut (modifiable via env/secrets).
GEMINI_MODEL_DEFAULT = "gemini-2.5-flash"


def _from_secrets(name: str) -> Optional[str]:
    """Tente de lire une clé dans st.secrets sans planter hors contexte Streamlit."""
    try:
        import streamlit as st  # import local : config.py reste utilisable hors Streamlit

        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        # Pas de contexte Streamlit, ou secrets.toml absent → on ignore.
        pass
    return None


def _get_first(names: list[str]) -> Optional[str]:
    """Renvoie la première valeur non vide trouvée (secrets puis env)."""
    for name in names:
        val = _from_secrets(name)
        if val and val.strip() and val.strip().lower() != "api key":
            return val.strip()
    for name in names:
        val = os.getenv(name)
        if val and val.strip() and val.strip().lower() != "api key":
            return val.strip()
    return None


def get_gemini_key() -> Optional[str]:
    """Clé API Google Gemini, ou None si introuvable."""
    return _get_first(_GEMINI_KEY_NAMES)


def get_anthropic_key() -> Optional[str]:
    """Clé API Anthropic (backend alternatif), ou None si introuvable."""
    return _get_first(_ANTHROPIC_KEY_NAMES)


def get_gemini_model() -> str:
    """Nom du modèle Gemini à utiliser."""
    return (
        _from_secrets("GEMINI_MODEL")
        or os.getenv("GEMINI_MODEL")
        or GEMINI_MODEL_DEFAULT
    )
