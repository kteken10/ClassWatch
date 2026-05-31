"""
Backend de vision factice (déterministe), sans appel réseau.

Utilité :
- démontrer l'application sans clé API valide (démo, soutenance, tests) ;
- servir d'exemple minimal pour implémenter `VisionBackend`.

Il renvoie un résultat plausible dérivé de la taille de l'image (déterministe),
afin que l'annotation, le journal et les exports soient testables de bout en bout.
"""

from __future__ import annotations

import io
import time
from typing import Optional

from PIL import Image

from models.schemas import (
    AnalysisResult,
    BoundingBox,
    Detection,
    Incident,
    NiveauObservation,
    Observation,
    OptionsAnalyse,
    Severite,
    TypeIncident,
)
from vision.backend import VisionBackend, VisionError


class MockBackend(VisionBackend):
    """Backend de démonstration, sans IA réelle."""

    nom = "Démo (factice, sans IA)"

    def analyze(
        self, image: bytes, options: Optional[OptionsAnalyse] = None
    ) -> AnalysisResult:
        if not image:
            raise VisionError("Aucune donnée d'image fournie.")
        try:
            with Image.open(io.BytesIO(image)) as img:
                w, h = img.size
        except Exception as e:
            raise VisionError("Image illisible ou corrompue.") from e

        time.sleep(0.2)  # simule une petite latence

        # Deux "personnes" et un "téléphone" placés de façon déterministe.
        detections = [
            Detection(
                label="personne",
                categorie="personne",
                confiance=0.92,
                box=BoundingBox(x_min=0.08, y_min=0.20, x_max=0.38, y_max=0.95),
            ),
            Detection(
                label="personne",
                categorie="personne",
                confiance=0.88,
                box=BoundingBox(x_min=0.55, y_min=0.18, x_max=0.85, y_max=0.95),
            ),
            Detection(
                label="téléphone",
                categorie="objet",
                confiance=0.74,
                box=BoundingBox(x_min=0.60, y_min=0.45, x_max=0.72, y_max=0.60),
            ),
        ]
        incidents = [
            Incident(
                type=TypeIncident.UTILISATION_TELEPHONE,
                severite=Severite.MOYEN,
                description="Un élève semble utiliser un téléphone pendant le cours.",
                confiance=0.7,
                detections_liees=[2],
            ),
        ]

        # Observations : une par point de surveillance coché (sinon valeurs par défaut).
        points = (
            options.points_surveillance
            if options and options.points_surveillance
            else ["Présence du professeur", "Atmosphère calme"]
        )
        observations = []
        for p in points:
            if "professeur" in p.lower():
                observations.append(
                    Observation(point=p, niveau=NiveauObservation.SUCCES,
                                detail="Un adulte semble présent dans la salle.")
                )
            elif "calme" in p.lower():
                observations.append(
                    Observation(point=p, niveau=NiveauObservation.ALERTE,
                                detail="Ambiance moyennement calme (usage de téléphone).")
                )
            else:
                observations.append(
                    Observation(point=p, niveau=NiveauObservation.INFO,
                                detail="Aucun problème particulier détecté (démo).")
                )

        return AnalysisResult(
            nb_personnes=2,
            detections=detections,
            incidents=incidents,
            observations=observations,
            recommandations=[
                "Rappeler la règle d'interdiction des téléphones en classe.",
                "Vérifier que tous les élèves sont attentifs.",
            ],
            resume="Scène de classe avec 2 personnes ; usage présumé d'un téléphone.",
            latence_ms=200,
        )
