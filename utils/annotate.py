"""
Annotation d'image : dessin des boîtes englobantes et des étiquettes d'incidents.

On combine Pillow (décodage/encodage simple, polices) et OpenCV (dessin rapide).
Les couleurs reflètent la gravité de l'incident lié, sinon une couleur neutre
pour les simples détections.
"""

from __future__ import annotations

import io
from typing import Optional

import cv2
import numpy as np
from PIL import Image

from models.schemas import AnalysisResult, Severite

# Couleurs en BGR (convention OpenCV).
_COULEUR_SEVERITE_BGR = {
    Severite.FAIBLE: (0, 200, 0),     # vert
    Severite.MOYEN: (0, 165, 255),    # orange
    Severite.ELEVE: (0, 0, 255),      # rouge
}
_COULEUR_DETECTION_BGR = (200, 200, 200)  # gris : détection sans incident


def _charger_image_bgr(image_bytes: bytes) -> np.ndarray:
    """Décode des bytes en tableau OpenCV BGR (gère RGBA/L → RGB)."""
    pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    rgb = np.array(pil)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def _gravite_par_detection(result: AnalysisResult) -> dict[int, Severite]:
    """Associe à chaque index de détection la gravité max de ses incidents liés."""
    mapping: dict[int, Severite] = {}
    ordre = {Severite.FAIBLE: 1, Severite.MOYEN: 2, Severite.ELEVE: 3}
    for inc in result.incidents:
        for idx in inc.detections_liees:
            actuelle = mapping.get(idx)
            if actuelle is None or ordre[inc.severite] > ordre[actuelle]:
                mapping[idx] = inc.severite
    return mapping


def _dessiner_label(img: np.ndarray, texte: str, x: int, y: int, couleur) -> None:
    """Dessine une étiquette lisible (fond plein + texte blanc) au-dessus de la boîte."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    echelle = max(0.5, img.shape[1] / 1400)  # taille adaptée à la résolution
    epaisseur = max(1, int(echelle * 2))
    (tw, th), base = cv2.getTextSize(texte, font, echelle, epaisseur)
    y_haut = max(th + base + 2, y)
    cv2.rectangle(
        img, (x, y_haut - th - base - 4), (x + tw + 6, y_haut), couleur, thickness=-1
    )
    cv2.putText(
        img, texte, (x + 3, y_haut - base - 2), font, echelle,
        (255, 255, 255), epaisseur, cv2.LINE_AA,
    )


def annoter_image(image_bytes: bytes, result: AnalysisResult) -> bytes:
    """
    Renvoie l'image annotée (PNG en bytes) : boîtes + labels.

    - Les détections liées à un incident prennent la couleur de sa gravité.
    - Une bannière d'incident s'affiche pour la gravité maximale détectée.
    """
    img = _charger_image_bgr(image_bytes)
    h, w = img.shape[:2]
    gravites = _gravite_par_detection(result)

    # 1) Boîtes des détections (personnes / objets).
    for i, det in enumerate(result.detections):
        left, top, right, bottom = det.box.to_pixels(w, h)
        sev = gravites.get(i)
        couleur = _COULEUR_SEVERITE_BGR[sev] if sev else _COULEUR_DETECTION_BGR
        epaisseur = max(2, int(w / 400))
        cv2.rectangle(img, (left, top), (right, bottom), couleur, epaisseur)
        label = f"{det.label} {int(det.confiance * 100)}%"
        _dessiner_label(img, label, left, top, couleur)

    # 2) Bannière récapitulative en haut si au moins un incident.
    if result.incidents:
        sev_max = result.gravite_max
        couleur = _COULEUR_SEVERITE_BGR.get(sev_max, _COULEUR_DETECTION_BGR)
        texte = f"INCIDENT(S): {len(result.incidents)} | gravite max: {sev_max.value}"
        cv2.rectangle(img, (0, 0), (w, max(30, int(h * 0.06))), couleur, thickness=-1)
        cv2.putText(
            img, texte, (8, max(22, int(h * 0.045))),
            cv2.FONT_HERSHEY_SIMPLEX, max(0.6, w / 1300),
            (255, 255, 255), max(1, int(w / 700)), cv2.LINE_AA,
        )

    # Encode en PNG (sans perte) pour l'affichage Streamlit / l'export.
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    out = io.BytesIO()
    Image.fromarray(rgb).save(out, format="PNG")
    return out.getvalue()
