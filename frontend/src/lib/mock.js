// Backend de démonstration (sans IA / sans réseau), déterministe.
export async function analyzeMock(file, { points = [] } = {}) {
  await new Promise((r) => setTimeout(r, 250))
  const pts = points.length ? points : ['Présence du professeur', 'Atmosphère calme']
  const observations = pts.map((p) => {
    if (p.toLowerCase().includes('professeur'))
      return { point: p, niveau: 'succès', detail: 'Un adulte semble présent dans la salle.' }
    if (p.toLowerCase().includes('calme'))
      return { point: p, niveau: 'alerte', detail: 'Ambiance moyennement calme (usage de téléphone).' }
    return { point: p, niveau: 'info', detail: 'Aucun problème particulier détecté (démo).' }
  })
  return {
    nb_personnes: 2,
    detections: [
      { label: 'personne', categorie: 'personne', confiance: 0.92, box: { x_min: 0.08, y_min: 0.2, x_max: 0.38, y_max: 0.95 } },
      { label: 'personne', categorie: 'personne', confiance: 0.88, box: { x_min: 0.55, y_min: 0.18, x_max: 0.85, y_max: 0.95 } },
      { label: 'téléphone', categorie: 'objet', confiance: 0.74, box: { x_min: 0.6, y_min: 0.45, x_max: 0.72, y_max: 0.6 } },
    ],
    incidents: [
      { type: 'utilisation téléphone', severite: 'moyen', confiance: 0.7, description: 'Un élève semble utiliser un téléphone pendant le cours.' },
    ],
    observations,
    recommandations: [
      "Rappeler la règle d'interdiction des téléphones en classe.",
      'Vérifier que tous les élèves sont attentifs.',
    ],
    resume: "Scène de classe avec 2 personnes ; usage présumé d'un téléphone.",
    latence_ms: 250,
  }
}
