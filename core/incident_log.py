"""
Journal d'incidents — cœur de la "gestion des incidents".

Responsabilités (logique métier pure, indépendante de Streamlit) :
- conserver l'historique horodaté des analyses et des incidents,
- filtrer par type / gravité,
- exporter le rapport en CSV et en PDF.

Le journal manipule des `AnalysisResult` (schéma unique défini dans models/schemas.py).
La persistance via st.session_state est gérée dans l'UI ; ici on travaille sur une
liste d'entrées passée en paramètre, ce qui rend le module testable sans Streamlit.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from models.schemas import (
    AnalysisResult,
    Incident,
    ORDRE_SEVERITE,
    Severite,
    TypeIncident,
)


@dataclass
class EntreeJournal:
    """Une analyse archivée dans le journal."""

    id: int
    horodatage: datetime
    source: str               # 'upload' | 'camera'
    nom_image: str
    result: AnalysisResult
    image_annotee: Optional[bytes] = field(default=None, repr=False)


@dataclass
class LigneIncident:
    """Vue 'à plat' d'un incident, pratique pour tableaux et exports."""

    entree_id: int
    horodatage: datetime
    source: str
    nom_image: str
    type: TypeIncident
    severite: Severite
    description: str
    confiance: float


class IncidentLog:
    """Gestionnaire du journal d'incidents (en mémoire)."""

    def __init__(self, entrees: Optional[List[EntreeJournal]] = None):
        self._entrees: List[EntreeJournal] = entrees if entrees is not None else []
        # Compteur d'id robuste même si la liste vient de session_state.
        self._prochain_id = (max((e.id for e in self._entrees), default=0) + 1)

    # --------------------------------------------------------------- écriture
    def ajouter(
        self,
        result: AnalysisResult,
        source: str,
        nom_image: str,
        horodatage: datetime,
        image_annotee: Optional[bytes] = None,
    ) -> EntreeJournal:
        """Ajoute une analyse au journal et renvoie l'entrée créée."""
        entree = EntreeJournal(
            id=self._prochain_id,
            horodatage=horodatage,
            source=source,
            nom_image=nom_image,
            result=result,
            image_annotee=image_annotee,
        )
        self._entrees.append(entree)
        self._prochain_id += 1
        return entree

    def vider(self) -> None:
        """Réinitialise le journal."""
        self._entrees.clear()
        self._prochain_id = 1

    # --------------------------------------------------------------- lecture
    @property
    def entrees(self) -> List[EntreeJournal]:
        return list(self._entrees)

    def lignes_incidents(self) -> List[LigneIncident]:
        """Aplatit toutes les entrées en lignes d'incidents (une par incident)."""
        lignes: List[LigneIncident] = []
        for e in self._entrees:
            for inc in e.result.incidents:
                lignes.append(
                    LigneIncident(
                        entree_id=e.id,
                        horodatage=e.horodatage,
                        source=e.source,
                        nom_image=e.nom_image,
                        type=inc.type,
                        severite=inc.severite,
                        description=inc.description,
                        confiance=inc.confiance,
                    )
                )
        return lignes

    def filtrer(
        self,
        types: Optional[List[TypeIncident]] = None,
        severites: Optional[List[Severite]] = None,
        severite_min: Optional[Severite] = None,
    ) -> List[LigneIncident]:
        """
        Filtre les incidents par type et/ou gravité.

        - `types` / `severites` : ensembles autorisés (None = tous).
        - `severite_min` : ne garde que les incidents >= à ce niveau.
        """
        lignes = self.lignes_incidents()
        if types:
            types_set = set(types)
            lignes = [l for l in lignes if l.type in types_set]
        if severites:
            sev_set = set(severites)
            lignes = [l for l in lignes if l.severite in sev_set]
        if severite_min is not None:
            seuil = ORDRE_SEVERITE[severite_min]
            lignes = [l for l in lignes if ORDRE_SEVERITE[l.severite] >= seuil]
        return lignes

    # ------------------------------------------------------------ statistiques
    def statistiques(self) -> dict:
        """Quelques agrégats pour les st.metric du journal."""
        lignes = self.lignes_incidents()
        par_type: dict[str, int] = {}
        par_severite: dict[str, int] = {}
        for l in lignes:
            par_type[l.type.value] = par_type.get(l.type.value, 0) + 1
            par_severite[l.severite.value] = par_severite.get(l.severite.value, 0) + 1
        return {
            "nb_analyses": len(self._entrees),
            "nb_incidents": len(lignes),
            "par_type": par_type,
            "par_severite": par_severite,
        }

    # ----------------------------------------------------------------- export
    def export_csv(self, lignes: Optional[List[LigneIncident]] = None) -> bytes:
        """Exporte les incidents (filtrés ou tous) en CSV (UTF-8 BOM pour Excel)."""
        if lignes is None:
            lignes = self.lignes_incidents()

        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=";")
        writer.writerow(
            [
                "id_analyse", "horodatage", "source", "image",
                "type", "gravite", "confiance", "description",
            ]
        )
        for l in lignes:
            writer.writerow(
                [
                    l.entree_id,
                    l.horodatage.strftime("%Y-%m-%d %H:%M:%S"),
                    l.source,
                    l.nom_image,
                    l.type.value,
                    l.severite.value,
                    f"{l.confiance:.2f}",
                    l.description,
                ]
            )
        # BOM UTF-8 pour qu'Excel ouvre correctement les accents.
        return ("﻿" + buf.getvalue()).encode("utf-8")

    def export_pdf(self, lignes: Optional[List[LigneIncident]] = None) -> Optional[bytes]:
        """
        Exporte un rapport PDF des incidents.

        Renvoie None si la dépendance `reportlab` n'est pas installée (l'UI propose
        alors uniquement le CSV). On garde ainsi le PDF "idéal mais optionnel".
        """
        if lignes is None:
            lignes = self.lignes_incidents()
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import cm
            from reportlab.platypus import (
                Paragraph,
                SimpleDocTemplate,
                Spacer,
                Table,
                TableStyle,
            )
        except ImportError:
            return None

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=1.5 * cm, rightMargin=1.5 * cm,
            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        )
        styles = getSampleStyleSheet()
        elements = []

        stats = self.statistiques()
        elements.append(Paragraph("ClassWatch — Rapport d'incidents", styles["Title"]))
        elements.append(
            Paragraph(
                f"Analyses : {stats['nb_analyses']} &nbsp;|&nbsp; "
                f"Incidents : {len(lignes)}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 0.4 * cm))

        # Table : en-tête + lignes.
        data = [["Horodatage", "Type", "Gravité", "Conf.", "Description"]]
        couleur_sev = {
            Severite.FAIBLE: colors.green,
            Severite.MOYEN: colors.orange,
            Severite.ELEVE: colors.red,
        }
        style_cell = styles["BodyText"]
        for l in lignes:
            data.append(
                [
                    l.horodatage.strftime("%d/%m %H:%M"),
                    Paragraph(l.type.value, style_cell),
                    l.severite.value,
                    f"{l.confiance:.0%}",
                    Paragraph(l.description, style_cell),
                ]
            )

        table = Table(
            data,
            colWidths=[2.6 * cm, 3.2 * cm, 1.8 * cm, 1.3 * cm, 7.5 * cm],
            repeatRows=1,
        )
        ts = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
            ]
        )
        # Colore la cellule "gravité" selon le niveau.
        for i, l in enumerate(lignes, start=1):
            ts.add("TEXTCOLOR", (2, i), (2, i), couleur_sev[l.severite])
        table.setStyle(ts)
        elements.append(table)

        if not lignes:
            elements.append(Paragraph("Aucun incident à signaler.", styles["Normal"]))

        doc.build(elements)
        return buf.getvalue()
