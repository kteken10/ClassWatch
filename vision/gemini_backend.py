"""
Implémentation concrète de `VisionBackend` basée sur Google Gemini (VLM).

Pourquoi Gemini :
- modèle multimodal capable de RAISONNER sur une scène (qualifier un incident),
  pas seulement détecter des objets ;
- sortie JSON FORCÉE via `response_schema` (structured output natif du SDK
  `google-genai`), donc validation Pydantic fiable.

API utilisée : Google Generative Language API (clé via st.secrets / .env).
Doc clé : https://ai.google.dev/  — clé créée sur https://aistudio.google.com/apikey
(une clé valide commence en général par "AIza...").

Le backend reste interchangeable : il suffit d'écrire une autre classe héritant
de VisionBackend (voir vision/mock_backend.py et la note Roboflow/YOLO du README).
"""

from __future__ import annotations

import io
import json
import time
from typing import List, Optional

from PIL import Image
from pydantic import BaseModel, Field, ValidationError

from config import get_gemini_key, get_gemini_model
from models.schemas import (
    AnalysisResult,
    Detection,
    Incident,
    Observation,
    OptionsAnalyse,
)
from vision.backend import VisionBackend, VisionError


# --- Sous-schéma envoyé au modèle : UNIQUEMENT ce qu'il doit produire ---------
# On réutilise les mêmes briques (Detection / Incident / Observation) que le reste
# de l'app : le schéma n'est donc défini qu'une seule fois (dans models/schemas.py).
class _VLMResponse(BaseModel):
    """Forme stricte de la réponse JSON attendue du modèle de vision."""

    nb_personnes: int = Field(default=0, ge=0)
    detections: List[Detection] = Field(default_factory=list)
    incidents: List[Incident] = Field(default_factory=list)
    observations: List[Observation] = Field(default_factory=list)
    recommandations: List[str] = Field(default_factory=list)
    resume: str = Field(default="")


# Prompt système : impose le rôle, le périmètre et le format JSON strict.
SYSTEM_PROMPT = """Tu es ClassWatch, un système d'analyse d'images de salle de classe \
pour la DÉTECTION et la GESTION D'INCIDENTS. Tu ne fais pas que détecter des objets : \
tu QUALIFIES des situations.

Pour l'image fournie :
1. Détecte les personnes et les objets pertinents (téléphone, arme/objet interdit, \
   cartable, etc.) avec une boîte englobante NORMALISÉE (coordonnées entre 0 et 1).
2. Identifie les INCIDENTS éventuels. Un incident est une SITUATION, ex. : agitation, \
   absence, comportement à risque, objet interdit, posture anormale, utilisation \
   téléphone, altercation. S'il n'y a aucun incident, renvoie une liste vide.
3. Pour chaque incident : choisis un `type` parmi la liste imposée, un niveau de \
   `severite` ('faible', 'moyen', 'élevé'), et rédige une `description` courte en FRANÇAIS.
4. Pour CHAQUE point de surveillance demandé, ajoute une `observation` : reprends le \
   libellé exact dans `point`, choisis un `niveau` ('succès' si tout va bien, 'info', \
   'alerte' ou 'danger'), et un `detail` court en français.
5. Propose 1 à 4 `recommandations` (actions concrètes en français) adaptées à la scène.
6. Renseigne `nb_personnes` et un `resume` global d'une phrase en français.

Règles :
- Réponds STRICTEMENT au format JSON demandé, sans texte autour, sans Markdown.
- N'invente pas d'incident s'il n'y en a pas. Reste factuel et prudent.
- Les coordonnées des boîtes sont normalisées (0..1), (x_min,y_min) en haut-gauche.
"""

USER_PROMPT_BASE = "Analyse cette image de salle de classe et renvoie le JSON d'incidents."


def _construire_prompt(options: Optional[OptionsAnalyse]) -> str:
    """Construit dynamiquement la consigne selon les points de surveillance cochés."""
    prompt = USER_PROMPT_BASE
    if options and options.points_surveillance:
        points = "\n".join(f"- {p}" for p in options.points_surveillance)
        prompt += (
            "\n\nVérifie SPÉCIFIQUEMENT ces points de surveillance et renseigne "
            f"une observation pour chacun :\n{points}"
        )
    return prompt

# Timeout de l'appel réseau (millisecondes) — protège l'UI d'un blocage.
_TIMEOUT_MS = 45_000


class GeminiBackend(VisionBackend):
    """Backend de vision utilisant l'API Google Gemini."""

    nom = "Google Gemini (VLM)"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        # Clé jamais en dur : lue via config (st.secrets / .env) si non fournie.
        self._api_key = api_key or get_gemini_key()
        self._model = model or get_gemini_model()
        self._client = None  # initialisation paresseuse (lazy)

    # ------------------------------------------------------------------ utils
    def disponible(self) -> bool:
        return bool(self._api_key)

    def _get_client(self):
        """Initialise le client Gemini une seule fois."""
        if self._client is not None:
            return self._client
        if not self._api_key:
            raise VisionError(
                "Clé API Gemini manquante. Renseigne GEMINI_API_KEY dans .env "
                "ou st.secrets (voir README)."
            )
        try:
            from google import genai
            from google.genai import types

            self._client = genai.Client(
                api_key=self._api_key,
                http_options=types.HttpOptions(timeout=_TIMEOUT_MS),
            )
        except ImportError as e:
            raise VisionError(
                "Le paquet 'google-genai' n'est pas installé "
                "(pip install google-genai)."
            ) from e
        except Exception as e:  # clé invalide, etc.
            raise VisionError(f"Initialisation du client Gemini impossible : {e}") from e
        return self._client

    @staticmethod
    def _mime_type(image: bytes) -> str:
        """Détecte le type MIME via Pillow ; lève VisionError si illisible."""
        try:
            with Image.open(io.BytesIO(image)) as img:
                fmt = (img.format or "JPEG").upper()
        except Exception as e:
            raise VisionError("Image illisible ou corrompue.") from e
        return {
            "JPEG": "image/jpeg",
            "JPG": "image/jpeg",
            "PNG": "image/png",
            "WEBP": "image/webp",
        }.get(fmt, "image/jpeg")

    # ---------------------------------------------------------------- analyse
    def analyze(
        self, image: bytes, options: Optional[OptionsAnalyse] = None
    ) -> AnalysisResult:
        if not image:
            raise VisionError("Aucune donnée d'image fournie.")

        mime = self._mime_type(image)
        client = self._get_client()

        from google.genai import types

        user_prompt = _construire_prompt(options)

        t0 = time.perf_counter()
        try:
            response = client.models.generate_content(
                model=self._model,
                contents=[
                    types.Part.from_bytes(data=image, mime_type=mime),
                    user_prompt,
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=_VLMResponse,  # sortie JSON forcée
                    temperature=0.1,
                ),
            )
        except Exception as e:
            # Réseau, timeout, quota, clé invalide → message clair pour l'UI.
            raise VisionError(f"Échec de l'appel à Gemini : {e}") from e

        latence_ms = int((time.perf_counter() - t0) * 1000)

        # 1) Tentative idéale : objet déjà parsé par le SDK (response.parsed).
        vlm: _VLMResponse | None = getattr(response, "parsed", None)

        # 2) Repli : parser le texte JSON brut nous-mêmes.
        if vlm is None:
            raw = getattr(response, "text", None)
            if not raw:
                raise VisionError("Réponse vide du modèle Gemini.")
            try:
                data = json.loads(raw)
                vlm = _VLMResponse.model_validate(data)
            except (json.JSONDecodeError, ValidationError) as e:
                raise VisionError(
                    f"Réponse du modèle non conforme au schéma JSON : {e}"
                ) from e

        # Construit l'AnalysisResult final (métadonnées remplies par l'app ensuite).
        result = AnalysisResult(
            nb_personnes=vlm.nb_personnes,
            detections=vlm.detections,
            incidents=vlm.incidents,
            observations=vlm.observations,
            recommandations=vlm.recommandations,
            resume=vlm.resume,
            latence_ms=latence_ms,
        )
        return result
