"""
ClassWatch — Application Streamlit de détection et gestion d'incidents en classe.

Architecture : l'UI ne contient PAS de logique métier. Elle orchestre :
- un VisionBackend (Gemini par défaut, repli démo) → models/schemas.AnalysisResult
- core.weather pour la météo (géolocalisation navigateur + Open-Meteo)
- utils.annotate pour l'image annotée
- core.incident_log.IncidentLog pour le journal, le filtrage et les exports.

La présentation (thème SDEN clair/sombre, cartes, dashboard) est dans ui/theme.py.
Lancement local :  streamlit run app.py
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from config import get_gemini_key, get_gemini_model
from core.incident_log import IncidentLog
from core.weather import MeteoError, get_meteo
from models.schemas import (
    Meteo,
    OptionsAnalyse,
    POINTS_SURVEILLANCE,
    Severite,
    TypeIncident,
)
from ui import theme
from utils.annotate import annoter_image
from vision.backend import VisionBackend, VisionError
from vision.gemini_backend import GeminiBackend
from vision.mock_backend import MockBackend

st.set_page_config(
    page_title="ClassWatch — Gestion d'incidents",
    page_icon=":material/visibility:",
    layout="wide",
)


# --------------------------------------------------------------------------- #
#  État de session
# --------------------------------------------------------------------------- #
def _init_session() -> None:
    if "journal_entrees" not in st.session_state:
        st.session_state.journal_entrees = []
    if "backend_choisi" not in st.session_state:
        st.session_state.backend_choisi = "Gemini (recommandé)"
    if "meteo" not in st.session_state:
        st.session_state.meteo = None  # type: ignore[assignment]
    if "points_selectionnes" not in st.session_state:
        st.session_state.points_selectionnes = list(POINTS_SURVEILLANCE.values())
    if "dark" not in st.session_state:
        st.session_state.dark = False


def get_journal() -> IncidentLog:
    return IncidentLog(st.session_state.journal_entrees)


def construire_backend(choix: str) -> VisionBackend:
    if choix.startswith("Gemini"):
        return GeminiBackend()
    return MockBackend()


# --------------------------------------------------------------------------- #
#  Barre latérale
# --------------------------------------------------------------------------- #
def _maj_meteo_si_besoin(coords: tuple[float, float]) -> None:
    cle = (round(coords[0], 3), round(coords[1], 3))
    if st.session_state.get("meteo_coords") == cle and st.session_state.meteo is not None:
        return
    try:
        st.session_state.meteo = get_meteo(coords[0], coords[1])
        st.session_state.meteo_coords = cle
    except MeteoError as e:
        st.sidebar.error(f"Météo indisponible : {e}")


def _section_meteo() -> None:
    st.sidebar.subheader("Météo & climat")
    st.sidebar.caption("Clique une fois sur le repère pour activer la météo de ta position.")

    coords = None
    try:
        from streamlit_geolocation import streamlit_geolocation

        # IMPORTANT : rendre le composant DANS la sidebar (sinon il s'affiche
        # dans la zone principale).
        with st.sidebar:
            loc = streamlit_geolocation()
        if loc and loc.get("latitude") is not None and loc.get("longitude") is not None:
            coords = (float(loc["latitude"]), float(loc["longitude"]))
    except ImportError:
        st.sidebar.caption("Composant de géolocalisation absent (voir requirements.txt).")

    with st.sidebar.expander("Position refusée ? Saisir manuellement"):
        lat = st.number_input("Latitude", value=48.8566, format="%.4f")
        lon = st.number_input("Longitude", value=2.3522, format="%.4f")
        if st.button("Utiliser ces coordonnées", use_container_width=True):
            coords = (lat, lon)

    if coords is not None:
        _maj_meteo_si_besoin(coords)

    meteo: Meteo | None = st.session_state.meteo
    if meteo is not None:
        with st.sidebar:
            theme.weather_card(
                icone=meteo.icone,
                condition=meteo.description,
                ville=meteo.ville,
                temperature=f"{meteo.temperature_c:.0f} °C",
                ressenti=f"{meteo.ressenti_c:.0f} °C" if meteo.ressenti_c is not None else None,
                reco=meteo.reco_climatisation,
                reco_niveau=meteo.clim_niveau,
                humidite=f"{meteo.humidite_pct} %" if meteo.humidite_pct is not None else None,
            )
    else:
        st.sidebar.caption("Météo non encore activée.")


def _section_points_surveillance() -> None:
    st.sidebar.subheader("Points de surveillance")
    st.sidebar.caption("Cochés = vérifiés en priorité par l'IA.")
    selectionnes = []
    for cle, libelle in POINTS_SURVEILLANCE.items():
        defaut = libelle in st.session_state.points_selectionnes
        if st.sidebar.checkbox(libelle, value=defaut, key=f"pt_{cle}"):
            selectionnes.append(libelle)
    st.session_state.points_selectionnes = selectionnes


def barre_laterale() -> VisionBackend:
    # Apparence (bascule clair / sombre)
    st.sidebar.subheader("Apparence")
    st.sidebar.toggle("Mode sombre", key="dark")
    st.sidebar.divider()

    st.sidebar.subheader("Configuration")
    options = ["Gemini (recommandé)", "Démo (sans IA)"]
    choix = st.sidebar.radio(
        "Backend de vision",
        options,
        index=options.index(st.session_state.backend_choisi)
        if st.session_state.backend_choisi in options
        else 0,
        help="Le backend est interchangeable (voir vision/backend.py).",
    )
    st.session_state.backend_choisi = choix

    if choix.startswith("Gemini"):
        if get_gemini_key():
            st.sidebar.success(f"Clé Gemini détectée · modèle {get_gemini_model()}")
        else:
            st.sidebar.error(
                "Clé Gemini introuvable. Renseigne `GEMINI_API_KEY` dans `.env` "
                "ou `st.secrets`. Utilise le backend **Démo** en attendant."
            )
    else:
        st.sidebar.info("Mode démo : résultat factice, sans appel réseau.")

    st.sidebar.divider()
    _section_meteo()
    st.sidebar.divider()
    _section_points_surveillance()
    st.sidebar.divider()

    journal = get_journal()
    st.sidebar.metric("Analyses réalisées", journal.statistiques()["nb_analyses"])
    if st.sidebar.button("Vider le journal", use_container_width=True):
        st.session_state.journal_entrees = []
        st.sidebar.success("Journal vidé.")
    st.sidebar.caption("Clés gérées via `.env` / `st.secrets` — jamais en dur.")
    return construire_backend(choix)


# --------------------------------------------------------------------------- #
#  Tableaux HTML
# --------------------------------------------------------------------------- #
def _table_incidents(incidents) -> None:
    rows = [
        [
            inc.type.value,
            theme.badge_html(inc.severite.value, theme.GRAVITE_TONE[inc.severite.value]),
            f'<span class="cw-num">{inc.confiance:.0%}</span>',
            inc.description,
        ]
        for inc in incidents
    ]
    theme.html_table(
        ["Type", "Gravité", "Conf.", "Description"],
        rows,
        aligns=["left", "left", "right", "left"],
    )


# --------------------------------------------------------------------------- #
#  Affichage d'un résultat d'analyse
# --------------------------------------------------------------------------- #
def afficher_resultat(result, image_annotee: bytes) -> None:
    grav = result.gravite_max.value if result.gravite_max else "—"
    grav_tone = theme.GRAVITE_TONE.get(grav, "neutral")
    inc_tone = "danger" if result.nb_incidents else "success"

    col_img, col_side = st.columns([3, 2])
    with col_img:
        with st.container(border=True):
            theme.card_title("Image annotée")
            st.image(image_annotee, use_container_width=True)
    with col_side:
        theme.mini_stat("group", "Personnes", result.nb_personnes)
        theme.mini_stat("warning", "Incidents", result.nb_incidents, tone=inc_tone)
        theme.mini_stat("speed", "Gravité max", grav, tone=grav_tone)
        if result.resume:
            st.info(f"**Résumé.** {result.resume}")
        meta = []
        if result.meteo is not None:
            meta.append(f"{result.meteo.libelle_court()} — {result.meteo.reco_climatisation}")
        if result.latence_ms is not None:
            meta.append(f"Analyse en {result.latence_ms} ms.")
        if meta:
            st.caption(" · ".join(meta))

    # Incidents
    with st.container(border=True):
        theme.card_title("Détail des incidents")
        if result.incidents:
            _table_incidents(result.incidents)
        else:
            theme.empty_state("shield", "Aucun incident détecté",
                              "La scène analysée ne présente pas d'incident.")

    # Observations
    if result.observations:
        with st.container(border=True):
            theme.card_title("Observations & points de surveillance")
            for obs in result.observations:
                theme.observation(obs.point, obs.detail, obs.niveau.value)

    # Recommandations
    if result.recommandations:
        with st.container(border=True):
            theme.card_title("Recommandations")
            for reco in result.recommandations:
                theme.recommandation(reco)

    # Détections brutes
    if result.detections:
        with st.expander(f"Détections brutes ({len(result.detections)})"):
            theme.html_table(
                ["Label", "Catégorie", "Conf."],
                [[d.label, d.categorie, f'<span class="cw-num">{d.confiance:.0%}</span>']
                 for d in result.detections],
                aligns=["left", "left", "right"],
            )


# --------------------------------------------------------------------------- #
#  Onglet ANALYSE
# --------------------------------------------------------------------------- #
def onglet_analyse(backend: VisionBackend) -> None:
    image_bytes = None
    nom_image = "image"
    source = "upload"

    with st.container(border=True):
        theme.card_title("Nouvelle analyse")
        mode = st.radio(
            "Mode d'entrée",
            ["Importer une image", "Caméra (temps réel)"],
            horizontal=True,
        )
        if mode == "Importer une image":
            fichier = st.file_uploader(
                "Image de salle de classe (jpg, png, webp)",
                type=["jpg", "jpeg", "png", "webp"],
            )
            if fichier is not None:
                image_bytes = fichier.getvalue()
                nom_image = fichier.name
                source = "upload"
        else:
            photo = st.camera_input("Prends une photo de la classe")
            if photo is not None:
                image_bytes = photo.getvalue()
                nom_image = f"camera_{datetime.now():%H%M%S}.jpg"
                source = "camera"

        if image_bytes is not None:
            st.image(image_bytes, caption="Aperçu", width=320)
            if not backend.disponible():
                st.warning(
                    "Backend indisponible (clé manquante ?). Bascule sur le backend "
                    "**Démo** dans la barre latérale."
                )
            lancer = st.button("Lancer l'analyse", type="primary",
                               disabled=not backend.disponible())
        else:
            lancer = False

    if image_bytes is None:
        with st.container(border=True):
            theme.empty_state(
                "image", "Aucune image pour le moment",
                "Importe une image de salle de classe ou prends une photo pour lancer l'analyse.",
            )
        return

    if lancer:
        options = OptionsAnalyse(points_surveillance=st.session_state.points_selectionnes)
        with st.spinner(f"Analyse en cours via {backend.nom}…"):
            try:
                result = backend.analyze(image_bytes, options)
            except VisionError as e:
                st.error(str(e))
                return
            except Exception as e:
                st.error(f"Erreur inattendue : {e}")
                return

        result.source = source
        result.horodatage = datetime.now()
        result.meteo = st.session_state.meteo

        try:
            image_annotee = annoter_image(image_bytes, result)
        except Exception as e:
            st.warning(f"Annotation impossible ({e}) — affichage de l'image brute.")
            image_annotee = image_bytes

        get_journal().ajouter(
            result=result, source=source, nom_image=nom_image,
            horodatage=result.horodatage, image_annotee=image_annotee,
        )
        st.success("Analyse enregistrée dans le journal.")
        afficher_resultat(result, image_annotee)


# --------------------------------------------------------------------------- #
#  Onglet JOURNAL
# --------------------------------------------------------------------------- #
def onglet_journal() -> None:
    journal = get_journal()
    stats = journal.statistiques()
    nb_inc = stats["nb_incidents"]
    nb_graves = stats["par_severite"].get("élevé", 0)
    ratio = int(round(100 * nb_graves / nb_inc)) if nb_inc else 0

    col_hero, col_kpi = st.columns([2, 1])
    with col_hero:
        theme.kpi_hero(
            label="Analyses réalisées",
            value=stats["nb_analyses"],
            sub=f"{nb_inc} incident(s) recensé(s) · {nb_graves} grave(s)",
            ratio=ratio,
            ratio_label="Part d'incidents graves",
        )
    with col_kpi:
        theme.mini_stat("warning", "Incidents (total)", nb_inc,
                        tone="danger" if nb_inc else "neutral")
        theme.mini_stat("speed", "Incidents graves", nb_graves,
                        tone="danger" if nb_graves else "success")

    if stats["nb_analyses"] == 0:
        with st.container(border=True):
            theme.empty_state(
                "history", "Journal vide",
                "Lance une première analyse dans l'onglet Analyse pour alimenter le journal.",
            )
        return

    # --- Dashboard : répartition par gravité + types fréquents ---
    with st.container(border=True):
        theme.card_title("Répartition des incidents")
        d1, d2 = st.columns(2)
        with d1:
            chart = theme.donut_gravite(stats["par_severite"])
            if chart is not None:
                st.altair_chart(chart, use_container_width=True)
            else:
                st.caption("Aucun incident à répartir.")
        with d2:
            theme.section_label("Types les plus fréquents")
            top = sorted(stats["par_type"].items(), key=lambda kv: kv[1], reverse=True)[:6]
            theme.leaderboard(top)

    # --- Filtres (barre, hors carte) ---
    theme.section_label("Filtres")
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        types_sel = st.multiselect("Type d'incident", options=[t.value for t in TypeIncident])
    with fcol2:
        sev_sel = st.multiselect("Gravité", options=[s.value for s in Severite])

    types = [TypeIncident(t) for t in types_sel] if types_sel else None
    severites = [Severite(s) for s in sev_sel] if sev_sel else None
    lignes = journal.filtrer(types=types, severites=severites)

    # --- Tableau filtré (carte) ---
    with st.container(border=True):
        theme.card_title(f"Incidents ({len(lignes)})")
        if lignes:
            rows = [
                [
                    f'<span class="cw-num">{l.horodatage:%d/%m/%Y %H:%M}</span>',
                    l.source,
                    f'<span class="cw-mono">{l.nom_image}</span>',
                    l.type.value,
                    theme.badge_html(l.severite.value, theme.GRAVITE_TONE[l.severite.value]),
                    f'<span class="cw-num">{l.confiance:.0%}</span>',
                    l.description,
                ]
                for l in lignes
            ]
            theme.html_table(
                ["Date/heure", "Source", "Image", "Type", "Gravité", "Conf.", "Description"],
                rows,
                aligns=["left", "left", "left", "left", "left", "right", "left"],
            )
        else:
            theme.empty_state("history", "Aucun incident",
                              "Aucun incident ne correspond aux filtres sélectionnés.")

    # --- Exports ---
    theme.section_label("Export du rapport")
    horod = datetime.now().strftime("%Y%m%d_%H%M%S")
    e1, e2 = st.columns(2)
    with e1:
        st.download_button(
            "Exporter en CSV", data=journal.export_csv(lignes),
            file_name=f"classwatch_incidents_{horod}.csv", mime="text/csv",
            use_container_width=True,
        )
    with e2:
        pdf_bytes = journal.export_pdf(lignes)
        if pdf_bytes is not None:
            st.download_button(
                "Exporter en PDF", data=pdf_bytes,
                file_name=f"classwatch_rapport_{horod}.pdf", mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.button("Export PDF (indisponible)", disabled=True, use_container_width=True,
                      help="Installe 'reportlab' (voir requirements.txt) pour activer le PDF.")

    # --- Galerie archivée ---
    with st.expander("Analyses archivées (images, météo, recommandations)"):
        for e in reversed(journal.entrees):
            meteo_txt = (f" · {e.result.meteo.temperature_c:.0f} °C"
                         if e.result.meteo is not None else "")
            st.markdown(
                f"**#{e.id}** — {e.horodatage:%d/%m/%Y %H:%M:%S} · {e.source} · "
                f"{e.nom_image} · {e.result.nb_incidents} incident(s){meteo_txt}"
            )
            if e.image_annotee:
                st.image(e.image_annotee, width=300)
            if e.result.recommandations:
                st.caption("Recommandations : " + " ; ".join(e.result.recommandations))


# --------------------------------------------------------------------------- #
#  Point d'entrée
# --------------------------------------------------------------------------- #
def main() -> None:
    _init_session()
    theme.inject_css(dark=st.session_state.dark)

    theme.brand_header(
        'Class<span>Watch</span>',
        "Détection et gestion d'incidents en salle de classe",
        mark_icon="visibility",
    )
    st.divider()

    backend = barre_laterale()

    tab_analyse, tab_journal = st.tabs(["Analyse", "Journal"])
    with tab_analyse:
        onglet_analyse(backend)
    with tab_journal:
        onglet_journal()


if __name__ == "__main__":
    main()
