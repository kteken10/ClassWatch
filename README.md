# 🛎️ ClassWatch — Détection & gestion d'incidents en salle de classe

Application **Streamlit** qui analyse des images de salle de classe (importées
ou prises en temps réel via smartphone) pour **détecter ET gérer** des incidents.
Elle va au-delà de la simple détection d'objets : elle **qualifie** des situations
(type + gravité + description), les **annote** sur l'image, et tient un
**journal d'incidents horodaté, filtrable et exportable**.

---

## ✨ Fonctionnalités

- **Deux modes d'entrée** : import de fichier (`jpg/png/webp`) ou caméra temps réel
  (`st.camera_input`, fonctionne sur smartphone via le navigateur).
- **Analyse d'incident par IA (VLM Gemini)** : détection des personnes/objets,
  qualification de l'incident (type, gravité `faible/moyen/élevé`, description),
  **réponse JSON strictement validée par Pydantic**.
- **Points de surveillance activables** : 8 cases à cocher (présence du professeur,
  chaises renversées, ordinateurs allumés, objets abandonnés, portes/fenêtres
  ouvertes, écrans actifs, élèves debout, atmosphère calme) qui **personnalisent
  dynamiquement le prompt** ; chaque point coché renvoie une **observation** (badge
  succès / info / alerte / danger).
- **Recommandations d'actions** générées par l'IA, en français.
- **Météo en temps réel** : géolocalisation du navigateur + API **Open-Meteo**
  (gratuite, sans clé) → température, ressenti, humidité, et **recommandation de
  climatisation** ; la météo est archivée avec chaque analyse.
- **Visualisation** : image annotée (bounding boxes + labels colorés par gravité),
  `st.metric` (personnes / incidents / gravité max), tableau détaillé.
- **Journal d'incidents** (différenciateur) : historique horodaté en
  `st.session_state`, **filtrage par type / gravité**, **export CSV et PDF**.
- **Robustesse** : gestion des erreurs API, timeout, image illisible, absence de
  détection, clé manquante, météo indisponible, et **backend de démo** utilisable
  sans clé.

---

## 🎨 Design

Interface inspirée du design system **« SDEN »** : une seule couleur vive
(**accent orange citron** `#f59e0b`), tout le reste en **slate** ; surfaces en
cartes arrondies à ombre sobre, badges « Stripe » (fond clair + ring inset),
onglets en *segmented control*, labels uppercase, chiffres en `tabular-nums`.

Caractéristiques « produit » :
- **Mode clair / sombre** avec bascule dans la barre latérale (système de tokens
  sémantiques `--bg / --surface / --border / --text…` qui s'adapte partout).
- **Icônes au trait en SVG inline** (rendu garanti, sans police d'icônes externe).
- **Sections en cartes** + **empty states** soignés (icône + titre + description).
- **Dashboard du Journal** : carte KPI « hero », donut de répartition par gravité
  (Altair), classement des types d'incidents, tableaux écrits en HTML maison
  (compatibles thème sombre, contrairement à `st.dataframe`).

Tout passe par le thème `.streamlit/config.toml` + une feuille de style injectée
dans [ui/theme.py](ui/theme.py) (aucune dépendance front lourde). Pour changer
l'accent : modifier `ACCENT` dans `ui/theme.py` et `primaryColor` dans
`.streamlit/config.toml`.

## 🧱 Architecture

La logique métier est **séparée de l'UI** pour rester testable, et le schéma
d'incident est **défini une seule fois** (Pydantic), réutilisé partout.

```
app.py                  # UI Streamlit : onglets Analyse / Journal + sidebar météo/points
.streamlit/config.toml  # thème (palette noir/blanc + accent orange citron)
ui/theme.py             # design « SDEN » : CSS + helpers (header, hero KPI, badges…)
config.py               # chargement des clés (st.secrets / .env), jamais en dur
models/schemas.py       # Pydantic : Detection, Incident, Observation, Meteo, AnalysisResult
vision/backend.py       # interface abstraite VisionBackend.analyze(bytes, options)->AnalysisResult
vision/gemini_backend.py# implémentation Google Gemini (sortie JSON forcée, prompt dynamique)
vision/mock_backend.py  # backend de démo déterministe (sans IA / sans réseau)
utils/annotate.py       # dessin des bounding boxes + labels (OpenCV + Pillow)
core/incident_log.py    # journal : historique, filtrage, export CSV/PDF
core/weather.py         # météo Open-Meteo (gratuite, sans clé) + reco climatisation
requirements.txt
.env.example
```

### Backend de vision interchangeable

Tout moteur d'analyse implémente l'interface :

```python
class VisionBackend(abc.ABC):
    def analyze(self, image: bytes) -> AnalysisResult: ...
```

- **`GeminiBackend`** (par défaut) : VLM multimodal Google Gemini. La sortie JSON
  est **forcée** via `response_schema` (structured output du SDK `google-genai`),
  puis **validée par Pydantic**.
- **`MockBackend`** : résultat factice déterministe, pour démo/tests sans clé.
- **Alternative possible** : un backend `YOLO`/`Roboflow` local. Il suffit de créer
  une classe héritant de `VisionBackend` et de renvoyer un `AnalysisResult`. Aucun
  autre fichier n'a besoin de changer.

---

## 🔑 API utilisée & gestion de la clé

**API : Google Generative Language (Gemini).** Crée une clé gratuite sur
👉 https://aistudio.google.com/apikey — une clé valide commence en général par `AIza...`.

> ⚠️ Les clés ne sont **jamais en dur** dans le code. Elles sont lues via
> `st.secrets` (déploiement) ou `.env` (local). Le code accepte plusieurs noms
> de variable (`GEMINI_API_KEY`, `GOOGLE_API_KEY`, `Gemini_Key`) pour tolérer
> une configuration non standard.

### En local (`.env`)

```bash
cp .env.example .env
# puis édite .env :
# GEMINI_API_KEY=AIza...
```

### Sur Streamlit Community Cloud (`secrets`)

Dans l'app : **Settings → Secrets**, colle :

```toml
GEMINI_API_KEY = "AIza..."
```

---

## 🚀 Installation & lancement local

Prérequis : **Python 3.11+**.

```bash
# 1) (recommandé) environnement virtuel
python -m venv .venv
# Windows :
.venv\Scripts\activate
# macOS/Linux :
source .venv/bin/activate

# 2) dépendances
pip install -r requirements.txt

# 3) clé API (voir section ci-dessus)
cp .env.example .env   # puis renseigne GEMINI_API_KEY

# 4) lancement
streamlit run app.py
```

L'app s'ouvre sur http://localhost:8501.
**Sans clé valide**, choisis le backend **« Démo (sans IA) »** dans la barre
latérale pour tester toute la chaîne (analyse → annotation → journal → export).

### 🌡️ Météo (géolocalisation)

La barre latérale affiche un **bouton de géolocalisation** (composant
`streamlit-geolocation`). En cliquant, le navigateur demande l'autorisation de
partager la position ; ClassWatch interroge alors **Open-Meteo** (gratuit, sans
clé) pour la température, le ressenti, l'humidité et une **recommandation de
climatisation**. Un repli **saisie manuelle de coordonnées** est prévu si la
géolocalisation est refusée. La géolocalisation nécessite un contexte sécurisé
(HTTPS ou `localhost`).

### 📱 Tester la caméra sur smartphone

`st.camera_input` nécessite un contexte sécurisé (HTTPS ou `localhost`). Le plus
simple : **déployer sur Streamlit Cloud** (HTTPS automatique) et ouvrir l'URL sur
le téléphone. En local, le navigateur du PC suffit pour tester la webcam.

---

## ☁️ Déploiement sur Streamlit Community Cloud

1. Pousse ce dossier sur un dépôt GitHub (le `.gitignore` exclut déjà `.env` et
   `secrets.toml`).
2. Sur https://share.streamlit.io → **New app**, sélectionne le repo et `app.py`.
3. **Settings → Secrets** : ajoute `GEMINI_API_KEY = "AIza..."`.
4. Deploy. (Le `requirements.txt` utilise `opencv-python-headless`, compatible Cloud.)

---

## 🧪 Notes de conception

- **Schéma unique** : `models/schemas.py` est la source de vérité ; il sert à la
  fois de contrat JSON pour le VLM, de validateur, et de format d'échange UI/journal.
- **Testabilité** : `core/incident_log.py` et `utils/annotate.py` ne dépendent pas
  de Streamlit et peuvent être testés isolément.
- **PDF optionnel** : si `reportlab` n'est pas installé, l'export PDF se désactive
  proprement et le CSV reste disponible.

---

## 🔒 Avertissement

ClassWatch est un projet pédagogique d'aide à la surveillance. Toute analyse d'images
de personnes (a fortiori de mineurs) doit respecter le RGPD et le cadre légal/éthique
applicable (consentement, finalité, conservation). À n'utiliser que dans un cadre autorisé.
