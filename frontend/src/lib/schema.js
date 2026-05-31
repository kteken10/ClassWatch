// Constantes métier (équivalent de models/schemas.py, côté front) + schéma JSON
// imposé à Gemini pour une sortie structurée.
import { Type } from '@google/genai'

export const POINTS_SURVEILLANCE = [
  { cle: 'prof_present', libelle: 'Présence du professeur' },
  { cle: 'chaises_renversees', libelle: 'Chaises renversées' },
  { cle: 'ordis_allumes', libelle: 'Ordinateurs allumés' },
  { cle: 'objets_abandonnes', libelle: 'Objets abandonnés / non rangés' },
  { cle: 'portes_ouvertes', libelle: 'Portes / fenêtres ouvertes' },
  { cle: 'ecrans_actifs', libelle: 'Écrans actifs / allumés' },
  { cle: 'eleves_debout', libelle: 'Élèves debout / hors de leur place' },
  { cle: 'atmosphere_calme', libelle: 'Atmosphère calme' },
]

export const TYPES_INCIDENT = [
  'agitation', 'absence', 'comportement à risque', 'objet interdit',
  'posture anormale', 'utilisation téléphone', 'altercation', 'autre',
]
export const SEVERITES = ['faible', 'moyen', 'élevé']
export const NIVEAUX = ['succès', 'info', 'alerte', 'danger']

export const GEMINI_MODEL = 'gemini-2.5-flash'

export const SYSTEM_PROMPT = `Tu es ClassWatch, un système d'analyse d'images de salle de classe \
pour la DÉTECTION et la GESTION D'INCIDENTS. Tu ne fais pas que détecter des objets : \
tu QUALIFIES des situations.

Pour l'image fournie :
1. Détecte les personnes et objets pertinents (téléphone, objet interdit, cartable…) avec \
   une boîte englobante NORMALISÉE (coordonnées entre 0 et 1, (x_min,y_min) en haut-gauche).
2. Identifie les INCIDENTS éventuels (situation : agitation, absence, comportement à risque, \
   objet interdit, posture anormale, utilisation téléphone, altercation). Liste vide si aucun.
3. Pour chaque incident : un type imposé, une severite ('faible'/'moyen'/'élevé') et une \
   description courte en FRANÇAIS.
4. Pour CHAQUE point de surveillance demandé, ajoute une observation (reprends le libellé exact \
   dans 'point', choisis un niveau 'succès'/'info'/'alerte'/'danger', et un 'detail' court).
5. Propose 1 à 4 recommandations (actions concrètes en français).
6. Renseigne nb_personnes et un resume d'une phrase en français.

Réponds STRICTEMENT au format JSON demandé. N'invente pas d'incident s'il n'y en a pas.`

// Schéma de sortie structurée Gemini.
export const RESPONSE_SCHEMA = {
  type: Type.OBJECT,
  properties: {
    nb_personnes: { type: Type.INTEGER },
    detections: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          label: { type: Type.STRING },
          categorie: { type: Type.STRING },
          confiance: { type: Type.NUMBER },
          box: {
            type: Type.OBJECT,
            properties: {
              x_min: { type: Type.NUMBER }, y_min: { type: Type.NUMBER },
              x_max: { type: Type.NUMBER }, y_max: { type: Type.NUMBER },
            },
            propertyOrdering: ['x_min', 'y_min', 'x_max', 'y_max'],
          },
        },
        propertyOrdering: ['label', 'categorie', 'confiance', 'box'],
      },
    },
    incidents: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          type: { type: Type.STRING, enum: TYPES_INCIDENT },
          severite: { type: Type.STRING, enum: SEVERITES },
          description: { type: Type.STRING },
          confiance: { type: Type.NUMBER },
        },
        propertyOrdering: ['type', 'severite', 'description', 'confiance'],
      },
    },
    observations: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          point: { type: Type.STRING },
          niveau: { type: Type.STRING, enum: NIVEAUX },
          detail: { type: Type.STRING },
        },
        propertyOrdering: ['point', 'niveau', 'detail'],
      },
    },
    recommandations: { type: Type.ARRAY, items: { type: Type.STRING } },
    resume: { type: Type.STRING },
  },
  propertyOrdering: [
    'nb_personnes', 'detections', 'incidents', 'observations', 'recommandations', 'resume',
  ],
}
