"""
Thème ClassWatch — adaptation Streamlit du design system « SDEN Core ».

Esprit : SOBRE et PREMIUM. Aucune emoji. Une seule couleur vive (accent orange
citron), tout le reste en slate. Icônes au trait en SVG inline (rendu garanti).

Particularités « pro » :
- système de tokens SÉMANTIQUES (`--bg`, `--surface`, `--border`, `--text`…) qui
  bascule entre thème CLAIR et SOMBRE via `inject_css(dark=...)` ;
- cartes structurantes (`st.container(border=True)` stylé) ;
- tableaux écrits À LA MAIN en HTML (le `st.dataframe` ne suit pas le sombre) ;
- dashboard : donut (Altair) + classement à barres + empty states soignés.
"""

from __future__ import annotations

import html as _html

import streamlit as st

# --- Accent (orange citron) ---------------------------------------------------
ACCENT = "#f59e0b"
ACCENT_600 = "#d97706"
ACCENT_700 = "#b45309"

# Tons des badges : (fond, texte, ring) — déclinés clair/sombre.
_TONES_LIGHT = {
    "neutral": ("#f1f5f9", "#334155", "#e2e8f0"),
    "accent": ("#fffbeb", "#b45309", "#fde68a"),
    "success": ("#ecfdf5", "#047857", "#a7f3d0"),
    "warning": ("#fffbeb", "#92400e", "#fde68a"),
    "danger": ("#fff1f2", "#be123c", "#fecdd3"),
}
_TONES_DARK = {
    "neutral": ("#1e293b", "#cbd5e1", "#334155"),
    "accent": ("#3a2c10", "#fcd34d", "#854d0e"),
    "success": ("#0c2a22", "#6ee7b7", "#155e4b"),
    "warning": ("#3a2c10", "#fcd34d", "#854d0e"),
    "danger": ("#3a1620", "#fda4af", "#7f1d3a"),
}

_NIVEAU_INFO = {
    "succès": ("success", "#10b981"),
    "info": ("neutral", "#94a3b8"),
    "alerte": ("warning", "#f59e0b"),
    "danger": ("danger", "#f43f5e"),
}
_DOT_COLOR = {"success": "#10b981", "warning": "#f59e0b", "danger": "#f43f5e", "neutral": "#94a3b8"}
GRAVITE_TONE = {"faible": "success", "moyen": "warning", "élevé": "danger"}
GRAVITE_COLOR = {"faible": "#10b981", "moyen": "#f59e0b", "élevé": "#f43f5e"}

# état courant (rempli par inject_css) pour que les helpers connaissent le mode
_STATE = {"dark": False}


def is_dark() -> bool:
    return _STATE["dark"]


def _tones():
    return _TONES_DARK if _STATE["dark"] else _TONES_LIGHT


def _esc(s) -> str:
    return _html.escape(str(s))


# --------------------------------------------------------------------------- #
#  Icônes SVG inline (« lucide », sans dépendance à une police)
# --------------------------------------------------------------------------- #
_SVG = {
    "visibility": '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
    "group": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "warning": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "speed": '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
    "arrow_forward": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "location_on": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "water_drop": '<path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>',
    "image": '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.09-3.09a2 2 0 0 0-2.82 0L6 21"/>',
    "history": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
    "inventory": '<path d="M3 7v11a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1V7"/><path d="M2 3h20v4H2z"/><path d="M10 12h4"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1Z"/>',
    "sunny": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
    "partly_cloudy_day": '<path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>',
    "cloud": '<path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>',
    "foggy": '<path d="M4 14.9A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.24"/><path d="M16 17H7"/><path d="M17 21H9"/>',
    "rainy": '<path d="M4 14.9A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.24"/><path d="M16 14v6"/><path d="M8 14v6"/><path d="M12 16v6"/>',
    "weather_snowy": '<path d="M4 14.9A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.24"/><path d="M8 15h.01"/><path d="M8 19h.01"/><path d="M12 17h.01"/><path d="M12 21h.01"/><path d="M16 15h.01"/><path d="M16 19h.01"/>',
    "thunderstorm": '<path d="M6 16.3A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 .5 8.97"/><path d="m13 12-3 5h4l-3 5"/>',
    "thermostat": '<path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z"/>',
}


def icon(name: str, size: int = 18, color: str = "currentColor", stroke: float = 2) -> str:
    """Renvoie le SVG inline d'une icône au trait (rendu garanti, sans police)."""
    inner = _SVG.get(name, _SVG["thermostat"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke}" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'style="display:inline-block;vertical-align:middle;flex-shrink:0;">{inner}</svg>'
    )


# --------------------------------------------------------------------------- #
#  Feuille de style globale (clair / sombre)
# --------------------------------------------------------------------------- #
def inject_css(dark: bool = False) -> None:
    """Injecte le CSS SDEN. `dark` bascule l'ensemble des tokens sémantiques."""
    _STATE["dark"] = dark

    if dark:
        tokens = """
      --bg:#0b1220; --surface:#111b2e; --surface-2:#0e1726; --elevated:#16233c;
      --border:#1e2c44; --border-soft:#172238;
      --text:#e6edf7; --text-soft:#9fb0c6; --text-faint:#6b7d97;
      --hero:#16233c; --shadow:0 1px 2px rgba(0,0,0,.4);
        """
    else:
        tokens = """
      --bg:#f8fafc; --surface:#ffffff; --surface-2:#f8fafc; --elevated:#0f172a;
      --border:#e2e8f0; --border-soft:#f1f5f9;
      --text:#0f172a; --text-soft:#64748b; --text-faint:#94a3b8;
      --hero:#0f172a; --shadow:0 1px 2px rgba(15,23,42,.05);
        """

    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {{
  --accent:{ACCENT}; --accent-600:{ACCENT_600}; --accent-700:{ACCENT_700};
  {tokens}
}}

html, body, .stApp, [class*="st-"] {{
  font-family:'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
/* Les icônes de Streamlit sont des ligatures : elles gardent leur police,
   sinon leur nom s'affiche en texte (« keyboard_double_arrow_right »). */
[data-testid="stIconMaterial"], .material-symbols-rounded, .material-icons {{
  font-family:'Material Symbols Rounded' !important;
}}
.stApp {{ background: var(--bg); color: var(--text); }}

/* Texte natif → tokens */
.stApp, .stApp p, .stApp li, .stApp label, .stApp span,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] p {{ color: var(--text); }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ color: var(--text-faint) !important; }}

[data-testid="stMain"] .block-container {{ max-width:1480px; padding-top:2.2rem; padding-bottom:3rem; }}
[data-testid="stHeader"] {{ background: transparent; }}
hr, [data-testid="stDivider"] {{ border-color: var(--border) !important; }}

h1,h2,h3,h4 {{ color: var(--text); letter-spacing:-0.02em; }}
h1 {{ font-weight:800; }} h2,h3 {{ font-weight:700; }}
[data-testid="stMain"] h2 {{ font-size:1.02rem; }} [data-testid="stMain"] h3 {{ font-size:.92rem; }}

/* Sidebar */
[data-testid="stSidebar"] {{ background: var(--surface); border-right:1px solid var(--border); }}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {{
  font-size:11px; text-transform:uppercase; letter-spacing:.08em; color:var(--text-faint); font-weight:700;
}}

/* Boutons */
.stButton > button, .stDownloadButton > button {{
  border-radius:8px; font-weight:600; transition:background .15s,border-color .15s,color .15s;
  border:1px solid var(--border); background:var(--surface); color:var(--text); box-shadow:var(--shadow);
}}
.stButton > button:hover, .stDownloadButton > button:hover {{ border-color:var(--accent); color:var(--accent-700); }}
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {{
  background:var(--accent); border-color:var(--accent); color:#1a1206;
  box-shadow:0 1px 2px rgba(245,158,11,.30);
}}
.stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {{
  background:var(--accent-600); border-color:var(--accent-600); color:#1a1206;
}}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {{
  outline:none; box-shadow:0 0 0 3px rgba(245,158,11,.28);
}}

/* Cartes : st.container(border=True) */
[data-testid="stVerticalBlockBorderWrapper"] {{
  background:var(--surface); border:1px solid var(--border) !important; border-radius:16px;
  box-shadow:var(--shadow); padding:6px 18px 14px;
}}

/* Metrics natifs */
[data-testid="stMetric"] {{
  background:var(--surface); border:1px solid var(--border); border-radius:14px;
  padding:14px 16px; box-shadow:var(--shadow);
}}
[data-testid="stMetricLabel"] {{ color:var(--text-soft); text-transform:uppercase; letter-spacing:.06em; font-size:11px !important; font-weight:600; }}
[data-testid="stMetricValue"] {{ color:var(--text); font-weight:800; font-variant-numeric:tabular-nums; }}

/* Tabs → segmented control */
[data-baseweb="tab-list"] {{ background:var(--surface-2); padding:4px; border-radius:10px; gap:4px; border:1px solid var(--border); }}
[data-baseweb="tab"] {{ border-radius:8px; padding:6px 16px; color:var(--text-soft); font-weight:600; }}
[data-baseweb="tab"]:hover {{ color:var(--text); }}
[data-baseweb="tab"][aria-selected="true"] {{ background:var(--surface); color:var(--accent-700); box-shadow:var(--shadow); }}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"] {{ display:none !important; }}

/* Champs */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea {{
  border-radius:8px; border:1px solid var(--border); background:var(--surface); color:var(--text);
}}
[data-baseweb="select"] > div {{ border-radius:8px; border-color:var(--border); background:var(--surface); }}
[data-baseweb="popover"] li {{ background:var(--surface); color:var(--text); }}
[data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus {{
  border-color:var(--accent); box-shadow:0 0 0 3px rgba(245,158,11,.16);
}}

/* Expander */
[data-testid="stExpander"] {{ border:1px solid var(--border); border-radius:14px; background:var(--surface); overflow:hidden; box-shadow:var(--shadow); }}
[data-testid="stExpander"] summary {{ color:var(--text); }}
[data-testid="stExpander"] summary:hover {{ color:var(--accent-700); }}

/* Alertes */
[data-testid="stAlert"],[data-testid="stNotification"] {{ border-radius:12px; }}

/* Dropzone upload / camera */
[data-testid="stFileUploaderDropzone"] {{ border-radius:14px; border:1.5px dashed var(--border); background:var(--surface-2); }}
[data-testid="stRadio"] label {{ font-weight:500; }}

/* Altair : fond transparent */
[data-testid="stVegaLiteChart"], .vega-embed {{ background:transparent !important; }}

/* ===== Composants HTML maison (cw-) ===== */
.cw-brand {{ display:flex; align-items:center; gap:13px; margin-bottom:.4rem; }}
.cw-brand-mark {{ width:42px; height:42px; border-radius:11px; background:var(--hero);
  display:flex; align-items:center; justify-content:center; flex-shrink:0; box-shadow:var(--shadow);
  border:1px solid var(--border); }}
.cw-brand-name {{ font-size:21px; font-weight:800; color:var(--text); letter-spacing:-0.02em; line-height:1.1; }}
.cw-brand-name span {{ color:var(--accent-600); }}
.cw-brand-sub {{ font-size:12.5px; color:var(--text-soft); margin-top:1px; }}

.cw-label {{ font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:var(--text-faint); margin:2px 0 8px; }}
.cw-cardtitle {{ font-size:14px; font-weight:700; color:var(--text); margin:2px 0 12px; }}

.cw-badge {{ display:inline-flex; align-items:center; gap:5px; padding:2px 9px; border-radius:8px; font-size:12px; font-weight:600; line-height:1.7; }}

/* Hero KPI */
.cw-hero {{ position:relative; overflow:hidden; border-radius:18px; background:var(--hero); color:#fff; padding:22px 24px; box-shadow:var(--shadow); height:100%; border:1px solid var(--border); }}
.cw-hero::before {{ content:""; position:absolute; right:-40px; top:-40px; width:190px; height:190px; border-radius:9999px; background:rgba(245,158,11,.20); filter:blur(38px); }}
.cw-hero-rel {{ position:relative; z-index:1; }}
.cw-hero-label {{ font-size:11px; text-transform:uppercase; letter-spacing:.09em; color:rgba(255,255,255,.55); }}
.cw-hero-value {{ font-size:46px; font-weight:800; line-height:1; margin-top:8px; font-variant-numeric:tabular-nums; }}
.cw-hero-sub {{ font-size:13px; color:rgba(255,255,255,.68); margin-top:8px; }}

/* MiniStat */
.cw-mini {{ display:flex; align-items:center; gap:12px; background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:13px 15px; box-shadow:var(--shadow); height:100%; }}
.cw-mini-ico {{ width:38px; height:38px; border-radius:10px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }}
.cw-mini-label {{ font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--text-soft); line-height:1.2; }}
.cw-mini-value {{ font-size:22px; font-weight:800; color:var(--text); line-height:1.15; margin-top:2px; font-variant-numeric:tabular-nums; }}

/* Observation */
.cw-obs {{ display:flex; align-items:flex-start; gap:12px; padding:11px 14px; margin-bottom:8px; background:var(--surface); border:1px solid var(--border); border-radius:12px; }}
.cw-obs-dot {{ width:9px; height:9px; border-radius:9999px; margin-top:6px; flex-shrink:0; }}
.cw-obs-point {{ font-size:14px; font-weight:600; color:var(--text); }}
.cw-obs-detail {{ font-size:13px; color:var(--text-soft); margin-top:1px; }}
.cw-obs-right {{ margin-left:auto; flex-shrink:0; padding-top:1px; }}

/* Reco */
.cw-reco {{ display:flex; align-items:center; gap:10px; padding:10px 14px; margin-bottom:7px; background:var(--surface); border:1px solid var(--border); border-radius:12px; font-size:14px; color:var(--text); }}

/* Carte météo */
.cw-weather {{ background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:13px 15px; }}
.cw-weather-top {{ display:flex; align-items:center; gap:10px; }}
.cw-weather-cond {{ font-size:15px; font-weight:700; color:var(--text); }}
.cw-weather-temp {{ font-size:13px; color:var(--text-soft); margin-top:1px; }}
.cw-weather-city {{ font-size:12px; color:var(--text-soft); display:flex; align-items:center; gap:5px; }}
.cw-weather-reco {{ display:flex; align-items:center; gap:8px; font-size:12.5px; color:var(--text); margin-top:11px; padding-top:11px; border-top:1px solid var(--border-soft); }}

/* Empty state */
.cw-empty {{ display:flex; flex-direction:column; align-items:center; text-align:center; padding:40px 20px; }}
.cw-empty-ico {{ width:58px; height:58px; border-radius:16px; background:var(--surface-2); border:1px solid var(--border); display:flex; align-items:center; justify-content:center; margin-bottom:14px; }}
.cw-empty-title {{ font-size:15px; font-weight:700; color:var(--text); }}
.cw-empty-desc {{ font-size:13px; color:var(--text-soft); margin-top:4px; max-width:380px; }}

/* Table HTML */
.cw-table {{ width:100%; border-collapse:collapse; font-size:13.5px; }}
.cw-table thead th {{ text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-soft); font-weight:600; padding:6px 12px 10px; border-bottom:1px solid var(--border); }}
.cw-table tbody td {{ padding:10px 12px; border-top:1px solid var(--border-soft); color:var(--text); vertical-align:top; }}
.cw-table tbody tr:hover td {{ background:var(--surface-2); }}
.cw-mono {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12px; color:var(--text-soft); }}
.cw-num {{ font-variant-numeric:tabular-nums; }}

/* Leaderboard */
.cw-lb {{ list-style:none; padding:0; margin:0; }}
.cw-lb li {{ margin-bottom:11px; }}
.cw-lb-top {{ display:flex; justify-content:space-between; font-size:12.5px; margin-bottom:5px; }}
.cw-lb-name {{ color:var(--text); }}
.cw-lb-count {{ color:var(--text-soft); font-variant-numeric:tabular-nums; }}
.cw-lb-bar {{ height:6px; border-radius:9999px; background:var(--surface-2); overflow:hidden; }}
.cw-lb-fill {{ height:100%; border-radius:9999px; }}
</style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
#  Helpers de rendu
# --------------------------------------------------------------------------- #
def brand_header(name_html: str, subtitle: str, mark_icon: str = "visibility") -> None:
    st.markdown(
        f'<div class="cw-brand"><div class="cw-brand-mark">{icon(mark_icon, 24, ACCENT)}</div>'
        f'<div><div class="cw-brand-name">{name_html}</div>'
        f'<div class="cw-brand-sub">{_esc(subtitle)}</div></div></div>',
        unsafe_allow_html=True,
    )


def card_title(text: str) -> None:
    st.markdown(f'<div class="cw-cardtitle">{_esc(text)}</div>', unsafe_allow_html=True)


def section_label(text: str) -> None:
    st.markdown(f'<div class="cw-label">{_esc(text)}</div>', unsafe_allow_html=True)


def badge_html(label: str, tone: str = "neutral") -> str:
    bg, fg, ring = _tones().get(tone, _tones()["neutral"])
    return (f'<span class="cw-badge" style="background:{bg};color:{fg};'
            f'box-shadow:inset 0 0 0 1px {ring};">{_esc(label)}</span>')


def kpi_hero(label: str, value, sub: str = "", ratio: int | None = None, ratio_label: str = "") -> None:
    bar = ""
    if ratio is not None:
        ratio = max(0, min(100, int(ratio)))
        bar = f"""<div style="margin-top:16px;">
          <div style="display:flex;justify-content:space-between;font-size:11px;color:rgba(255,255,255,.6);margin-bottom:6px;">
            <span>{_esc(ratio_label)}</span><span style="color:rgba(255,255,255,.9);font-weight:600;">{ratio}%</span></div>
          <div style="height:6px;border-radius:9999px;background:rgba(255,255,255,.12);overflow:hidden;">
            <div style="height:100%;width:{ratio}%;border-radius:9999px;background:{ACCENT};"></div></div></div>"""
    st.markdown(
        f'<div class="cw-hero"><div class="cw-hero-rel"><div class="cw-hero-label">{_esc(label)}</div>'
        f'<div class="cw-hero-value">{_esc(value)}</div><div class="cw-hero-sub">{_esc(sub)}</div>{bar}'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def mini_stat(icon_name: str, label: str, value, tone: str = "neutral") -> None:
    bg, fg, _ = _tones().get(tone, _tones()["neutral"])
    st.markdown(
        f'<div class="cw-mini"><div class="cw-mini-ico" style="background:{bg};color:{fg};">'
        f'{icon(icon_name, 20, fg)}</div><div><div class="cw-mini-label">{_esc(label)}</div>'
        f'<div class="cw-mini-value">{_esc(value)}</div></div></div>',
        unsafe_allow_html=True,
    )


def observation(point: str, detail: str, niveau: str) -> None:
    tone, dot = _NIVEAU_INFO.get(niveau, ("neutral", "#94a3b8"))
    st.markdown(
        f'<div class="cw-obs"><span class="cw-obs-dot" style="background:{dot};"></span>'
        f'<div><div class="cw-obs-point">{_esc(point)}</div>'
        f'<div class="cw-obs-detail">{_esc(detail)}</div></div>'
        f'<span class="cw-obs-right">{badge_html(niveau, tone)}</span></div>',
        unsafe_allow_html=True,
    )


def recommandation(texte: str) -> None:
    st.markdown(
        f'<div class="cw-reco">{icon("arrow_forward", 17, ACCENT_600)}<span>{_esc(texte)}</span></div>',
        unsafe_allow_html=True,
    )


def weather_card(icone: str, condition: str, ville: str | None, temperature: str,
                 ressenti: str | None, reco: str, reco_niveau: str, humidite: str | None = None) -> None:
    ress = f" · ressenti {_esc(ressenti)}" if ressenti else ""
    hum = (f'<span style="margin-left:auto;display:flex;align-items:center;gap:4px;color:var(--text-soft);font-size:12px;">'
           f'{icon("water_drop", 14, "#94a3b8")}{_esc(humidite)}</span>') if humidite else ""
    ville_html = (f'<div class="cw-weather-city">{icon("location_on", 14, "#94a3b8")}{_esc(ville)}</div>') if ville else ""
    dot = _DOT_COLOR.get(reco_niveau, "#94a3b8")
    st.markdown(
        f'<div class="cw-weather"><div class="cw-weather-top">{icon(icone, 30, ACCENT_600)}'
        f'<div><div class="cw-weather-cond">{_esc(condition)}</div>'
        f'<div class="cw-weather-temp">{_esc(temperature)}{ress}</div></div>{hum}</div>'
        f'<div style="margin-top:8px;">{ville_html}</div>'
        f'<div class="cw-weather-reco"><span style="width:8px;height:8px;border-radius:9999px;background:{dot};flex-shrink:0;"></span>'
        f'<span>{_esc(reco)}</span></div></div>',
        unsafe_allow_html=True,
    )


def empty_state(icon_name: str, title: str, desc: str = "") -> None:
    d = f'<div class="cw-empty-desc">{_esc(desc)}</div>' if desc else ""
    st.markdown(
        f'<div class="cw-empty"><div class="cw-empty-ico">{icon(icon_name, 26, "#94a3b8")}</div>'
        f'<div class="cw-empty-title">{_esc(title)}</div>{d}</div>',
        unsafe_allow_html=True,
    )


def html_table(headers: list[str], rows: list[list[str]], aligns: list[str] | None = None) -> None:
    """Tableau HTML maison (thème sombre OK). Les cellules peuvent contenir du HTML."""
    aligns = aligns or ["left"] * len(headers)
    thead = "".join(f'<th style="text-align:{a};">{_esc(h)}</th>' for h, a in zip(headers, aligns))
    body = ""
    for r in rows:
        tds = "".join(f'<td style="text-align:{a};">{c}</td>' for c, a in zip(r, aligns))
        body += f"<tr>{tds}</tr>"
    st.markdown(
        f'<table class="cw-table"><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table>',
        unsafe_allow_html=True,
    )


def leaderboard(items: list[tuple[str, int]]) -> None:
    """Classement à barres (le 1er en accent, le reste en slate)."""
    if not items:
        st.markdown('<div style="color:var(--text-soft);font-size:13px;">Aucune donnée.</div>',
                    unsafe_allow_html=True)
        return
    maxi = max(c for _, c in items) or 1
    lis = ""
    for i, (name, count) in enumerate(items):
        pct = int(round(100 * count / maxi))
        fill = ACCENT if i == 0 else "var(--text-faint)"
        lis += (f'<li><div class="cw-lb-top"><span class="cw-lb-name">{_esc(name)}</span>'
                f'<span class="cw-lb-count">{count}</span></div>'
                f'<div class="cw-lb-bar"><div class="cw-lb-fill" style="width:{pct}%;background:{fill};"></div></div></li>')
    st.markdown(f'<ul class="cw-lb">{lis}</ul>', unsafe_allow_html=True)


def donut_gravite(counts: dict[str, int]):
    """Donut Altair de répartition par gravité (palette slate/accent/rose). None si vide."""
    data = [(g, n) for g, n in counts.items() if n > 0]
    if not data:
        return None
    import altair as alt
    import pandas as pd

    df = pd.DataFrame(data, columns=["gravite", "n"])
    txt = "#e6edf7" if _STATE["dark"] else "#0f172a"
    domain = ["faible", "moyen", "élevé"]
    rng = [GRAVITE_COLOR["faible"], GRAVITE_COLOR["moyen"], GRAVITE_COLOR["élevé"]]
    chart = (
        alt.Chart(df)
        .mark_arc(innerRadius=52, outerRadius=80, stroke=None)
        .encode(
            theta=alt.Theta("n:Q", stack=True),
            color=alt.Color(
                "gravite:N",
                scale=alt.Scale(domain=domain, range=rng),
                legend=alt.Legend(title=None, orient="right", labelColor=txt, labelFontSize=12),
            ),
            tooltip=["gravite:N", "n:Q"],
        )
        .properties(height=190, background="transparent")
        .configure_view(stroke=None)
    )
    return chart
