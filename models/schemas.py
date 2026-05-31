"""
Schémas Pydantic — SOURCE UNIQUE de vérité du format d'incident.

Ces modèles sont réutilisés partout :
- ils définissent le schéma JSON imposé au VLM (Gemini) en sortie structurée,
- ils valident strictement la réponse du modèle,
- ils servent de format d'échange entre la couche métier et l'UI Streamlit.

NB : on garde volontairement le schéma simple et "plat" pour maximiser la
fiabilité de la sortie JSON des modèles de vision.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Severite(str, Enum):
    """Niveau de gravité d'un incident."""

    FAIBLE = "faible"
    MOYEN = "moyen"
    ELEVE = "élevé"


# Ordre utilisé pour calculer la "gravité maximale" et pour le tri.
ORDRE_SEVERITE = {Severite.FAIBLE: 1, Severite.MOYEN: 2, Severite.ELEVE: 3}


class NiveauObservation(str, Enum):
    """Niveau d'une observation de surveillance (pour l'affichage en badge)."""

    SUCCES = "succès"   # tout va bien (ex. professeur présent)
    INFO = "info"       # information neutre
    ALERTE = "alerte"   # à surveiller
    DANGER = "danger"   # problème avéré


# --- Points de surveillance activables (cases à cocher) -----------------------
# clé technique -> libellé affiché. Réutilisé par l'UI ET par le prompt VLM.
POINTS_SURVEILLANCE: dict[str, str] = {
    "prof_present": "Présence du professeur",
    "chaises_renversees": "Chaises renversées",
    "ordis_allumes": "Ordinateurs allumés",
    "objets_abandonnes": "Objets abandonnés / non rangés",
    "portes_ouvertes": "Portes / fenêtres ouvertes",
    "ecrans_actifs": "Écrans actifs / allumés",
    "eleves_debout": "Élèves debout / hors de leur place",
    "atmosphere_calme": "Atmosphère calme",
}


class TypeIncident(str, Enum):
    """
    Typologie des incidents détectables en salle de classe.

    La liste reste ouverte côté usage (le modèle peut décrire finement dans le
    champ `description`), mais on contraint la catégorie à un ensemble connu
    pour permettre le filtrage et les statistiques.
    """

    AGITATION = "agitation"
    ABSENCE = "absence"
    COMPORTEMENT_A_RISQUE = "comportement à risque"
    OBJET_INTERDIT = "objet interdit"
    POSTURE_ANORMALE = "posture anormale"
    UTILISATION_TELEPHONE = "utilisation téléphone"
    ALTERCATION = "altercation"
    AUTRE = "autre"


class BoundingBox(BaseModel):
    """
    Boîte englobante en coordonnées NORMALISÉES (0..1).

    On normalise pour rester indépendant de la résolution de l'image :
    (x_min, y_min) = coin haut-gauche, (x_max, y_max) = coin bas-droite.
    """

    x_min: float = Field(..., ge=0.0, le=1.0, description="Bord gauche (0..1)")
    y_min: float = Field(..., ge=0.0, le=1.0, description="Bord haut (0..1)")
    x_max: float = Field(..., ge=0.0, le=1.0, description="Bord droit (0..1)")
    y_max: float = Field(..., ge=0.0, le=1.0, description="Bord bas (0..1)")

    @field_validator("x_max")
    @classmethod
    def _x_coherent(cls, v: float, info):
        # On tolère les petites incohérences du modèle plutôt que de tout rejeter.
        x_min = info.data.get("x_min", 0.0)
        return max(v, x_min)

    @field_validator("y_max")
    @classmethod
    def _y_coherent(cls, v: float, info):
        y_min = info.data.get("y_min", 0.0)
        return max(v, y_min)

    def to_pixels(self, width: int, height: int) -> tuple[int, int, int, int]:
        """Convertit la boîte normalisée en pixels (left, top, right, bottom)."""
        left = int(self.x_min * width)
        top = int(self.y_min * height)
        right = int(self.x_max * width)
        bottom = int(self.y_max * height)
        return left, top, right, bottom


class Detection(BaseModel):
    """Une détection élémentaire : une personne ou un objet pertinent."""

    label: str = Field(..., description="Étiquette, ex. 'personne', 'téléphone', 'couteau'")
    categorie: str = Field(
        default="objet",
        description="'personne' ou 'objet'",
    )
    confiance: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Confiance estimée 0..1"
    )
    box: BoundingBox = Field(..., description="Boîte englobante normalisée")


class Incident(BaseModel):
    """Un incident qualifié (situation), pas un simple objet détecté."""

    type: TypeIncident = Field(..., description="Catégorie de l'incident")
    severite: Severite = Field(..., description="Gravité : faible / moyen / élevé")
    description: str = Field(
        ..., min_length=1, description="Description courte générée en français"
    )
    confiance: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Confiance du modèle 0..1"
    )
    # Indices renvoyant vers la liste `detections` d'AnalysisResult (facultatif).
    detections_liees: List[int] = Field(
        default_factory=list,
        description="Indices des détections associées à cet incident",
    )


class Observation(BaseModel):
    """
    Résultat d'un point de surveillance vérifié par le modèle.

    Ex. : point="Présence du professeur", niveau="succès", detail="Adulte présent au tableau".
    Affichée sous forme de badge coloré dans l'UI.
    """

    point: str = Field(..., description="Libellé du point de surveillance vérifié")
    niveau: NiveauObservation = Field(
        default=NiveauObservation.INFO, description="succès / info / alerte / danger"
    )
    detail: str = Field(default="", description="Constat court en français")


class Meteo(BaseModel):
    """Instantané météo (via géolocalisation + Open-Meteo)."""

    latitude: float
    longitude: float
    temperature_c: float = Field(..., description="Température en °C")
    ressenti_c: Optional[float] = Field(default=None, description="Température ressentie °C")
    humidite_pct: Optional[int] = Field(default=None, description="Humidité relative %")
    ville: Optional[str] = Field(default=None, description="Lieu lisible (ville, pays)")
    description: str = Field(default="", description="Condition météo en mots (français)")
    icone: str = Field(default="thermostat", description="Nom d'icône Material Symbols")
    reco_climatisation: str = Field(
        default="", description="Recommandation de climatisation déduite de la température"
    )
    clim_niveau: str = Field(
        default="success", description="Ton de la reco : success / warning / danger"
    )

    def libelle_court(self) -> str:
        """Phrase courte et lisible, ex. 'Paris — Ciel dégagé · 21 °C (ressenti 19 °C)'."""
        lieu = f"{self.ville} — " if self.ville else ""
        ressenti = (
            f" (ressenti {self.ressenti_c:.0f} °C)" if self.ressenti_c is not None else ""
        )
        return f"{lieu}{self.description} · {self.temperature_c:.0f} °C{ressenti}"


class AnalysisResult(BaseModel):
    """
    Résultat complet d'une analyse d'image.

    C'est l'objet renvoyé par tout VisionBackend et consommé par l'UI + le journal.
    Les champs `horodatage`, `source` et `latence_ms` sont remplis côté application
    (pas par le modèle) — d'où leur exclusion du schéma envoyé au VLM.
    """

    nb_personnes: int = Field(
        default=0, ge=0, description="Nombre de personnes détectées"
    )
    detections: List[Detection] = Field(
        default_factory=list, description="Détections (personnes/objets)"
    )
    incidents: List[Incident] = Field(
        default_factory=list, description="Incidents qualifiés"
    )
    observations: List[Observation] = Field(
        default_factory=list,
        description="Constats sur les points de surveillance demandés",
    )
    recommandations: List[str] = Field(
        default_factory=list,
        description="Actions suggérées, en français (1 phrase chacune)",
    )
    resume: str = Field(
        default="", description="Résumé global en une phrase de la scène"
    )

    # --- Métadonnées remplies par l'application (non par le modèle) ---
    meteo: Optional[Meteo] = Field(
        default=None, description="Instantané météo associé à l'analyse"
    )
    horodatage: Optional[datetime] = Field(
        default=None, description="Date/heure de l'analyse (UTC ou locale)"
    )
    source: str = Field(
        default="inconnue", description="Origine : 'upload' ou 'camera'"
    )
    latence_ms: Optional[int] = Field(
        default=None, description="Durée de l'appel au backend en ms"
    )

    # ------------------------------------------------------------------ helpers
    @property
    def nb_incidents(self) -> int:
        return len(self.incidents)

    @property
    def gravite_max(self) -> Optional[Severite]:
        """Renvoie la gravité la plus élevée parmi les incidents, sinon None."""
        if not self.incidents:
            return None
        return max(
            (i.severite for i in self.incidents),
            key=lambda s: ORDRE_SEVERITE[s],
        )


class OptionsAnalyse(BaseModel):
    """
    Options passées au backend pour personnaliser l'analyse.

    `points_surveillance` : libellés des points cochés dans l'UI (sous-ensemble
    de POINTS_SURVEILLANCE.values()) que le modèle doit vérifier en priorité.
    """

    points_surveillance: List[str] = Field(default_factory=list)


# Schéma JSON "épuré" demandé au VLM : on ne lui demande QUE ce qu'il peut produire.
# (les métadonnées applicatives — meteo, horodatage… — sont remplies par l'app)
SCHEMA_VLM_KEYS = [
    "nb_personnes",
    "detections",
    "incidents",
    "observations",
    "recommandations",
    "resume",
]
