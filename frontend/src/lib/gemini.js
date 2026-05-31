// Appel direct à l'API Gemini depuis le navigateur (architecture 100% front).
// ⚠️ La clé est exposée côté client : utiliser une clé restreinte par domaine en prod.
import { GoogleGenAI } from '@google/genai'
import { GEMINI_MODEL, RESPONSE_SCHEMA, SYSTEM_PROMPT } from './schema'

// Lit une image (File/Blob) → { base64, mimeType }.
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const res = reader.result // data:<mime>;base64,XXXX
      const base64 = String(res).split(',')[1]
      resolve({ base64, mimeType: file.type || 'image/jpeg' })
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

export async function analyzeWithGemini(file, { points = [], apiKey } = {}) {
  if (!apiKey) throw new Error('Clé Gemini manquante (renseigne-la dans les paramètres).')

  const { base64, mimeType } = await fileToBase64(file)
  const ai = new GoogleGenAI({ apiKey })

  let userPrompt = "Analyse cette image de salle de classe et renvoie le JSON d'incidents."
  if (points.length) {
    userPrompt += '\n\nVérifie SPÉCIFIQUEMENT ces points de surveillance (une observation chacun) :\n'
      + points.map((p) => `- ${p}`).join('\n')
  }

  const t0 = performance.now()
  let response
  try {
    response = await ai.models.generateContent({
      model: GEMINI_MODEL,
      contents: [
        { role: 'user', parts: [
          { inlineData: { mimeType, data: base64 } },
          { text: userPrompt },
        ] },
      ],
      config: {
        systemInstruction: SYSTEM_PROMPT,
        responseMimeType: 'application/json',
        responseSchema: RESPONSE_SCHEMA,
        temperature: 0.1,
      },
    })
  } catch (e) {
    const msg = e?.message || String(e)
    throw new Error(`Échec de l'appel à Gemini : ${msg}`)
  }
  const latence_ms = Math.round(performance.now() - t0)

  const text = response.text
  if (!text) throw new Error('Réponse vide du modèle Gemini.')

  let data
  try {
    data = JSON.parse(text)
  } catch (e) {
    throw new Error('Réponse du modèle non conforme au JSON attendu.')
  }

  return {
    nb_personnes: data.nb_personnes ?? 0,
    detections: data.detections ?? [],
    incidents: data.incidents ?? [],
    observations: data.observations ?? [],
    recommandations: data.recommandations ?? [],
    resume: data.resume ?? '',
    latence_ms,
  }
}
