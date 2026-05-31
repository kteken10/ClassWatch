"""
Interface abstraite des backends de vision.

L'objectif est de pouvoir remplacer le moteur d'analyse (Gemini VLM, Anthropic,
YOLO/Roboflow local...) sans toucher au reste de l'application : l'UI et le
journal ne connaissent QUE `VisionBackend.analyze(image) -> AnalysisResult`.
"""

from __future__ import annotations

import abc
from typing import Optional

from models.schemas import AnalysisResult, OptionsAnalyse


class VisionError(Exception):
    """Erreur métier remontée par un backend (clé manquante, timeout, etc.)."""


class VisionBackend(abc.ABC):
    """Contrat commun à toutes les implémentations de vision."""

    #: Nom lisible affiché dans l'UI.
    nom: str = "abstrait"

    @abc.abstractmethod
    def analyze(
        self, image: bytes, options: Optional[OptionsAnalyse] = None
    ) -> AnalysisResult:
        """
        Analyse une image et renvoie un `AnalysisResult` validé.

        Args:
            image: contenu binaire de l'image (jpg/png/webp).
            options: options d'analyse (points de surveillance à vérifier, etc.).

        Returns:
            AnalysisResult : détections + incidents + observations + recommandations.

        Raises:
            VisionError : en cas d'échec (clé absente, image illisible, timeout,
            réponse non conforme au schéma...). L'UI attrape cette exception.
        """
        raise NotImplementedError

    def disponible(self) -> bool:
        """Indique si le backend est utilisable (ex. clé API présente)."""
        return True
