// Annotation d'image côté navigateur (canvas) : boîtes + bannière incidents.
const GRAVITE_COLOR = { faible: '#10b981', moyen: '#f59e0b', 'élevé': '#f43f5e' }
const ACCENT = '#84cc16'
const ORDER = { faible: 1, moyen: 2, 'élevé': 3 }

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

// file : File image ; result : objet d'analyse → renvoie un dataURL PNG annoté.
export async function annotate(file, result) {
  const url = URL.createObjectURL(file)
  let img
  try {
    img = await loadImage(url)
  } finally {
    URL.revokeObjectURL(url)
  }

  const w = img.naturalWidth || img.width
  const h = img.naturalHeight || img.height
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')
  ctx.drawImage(img, 0, 0)

  const gravMax = (result.incidents || []).reduce(
    (m, i) => (ORDER[i.severite] > (ORDER[m] || 0) ? i.severite : m), null,
  )
  const boxColor = gravMax ? GRAVITE_COLOR[gravMax] : ACCENT
  const lw = Math.max(2, Math.round(w / 400))
  ctx.lineWidth = lw
  ctx.font = `${Math.max(13, Math.round(w / 55))}px Inter, sans-serif`
  ctx.textBaseline = 'top'

  for (const d of result.detections || []) {
    const b = d.box || {}
    const left = (b.x_min || 0) * w
    const top = (b.y_min || 0) * h
    const right = (b.x_max || 0) * w
    const bottom = (b.y_max || 0) * h
    ctx.strokeStyle = boxColor
    ctx.strokeRect(left, top, right - left, bottom - top)
    const label = `${d.label || 'objet'} ${Math.round((d.confiance || 0) * 100)}%`
    const tw = ctx.measureText(label).width
    const fh = Math.max(16, Math.round(w / 45))
    ctx.fillStyle = boxColor
    ctx.fillRect(left, Math.max(0, top - fh - 4), tw + 10, fh + 4)
    ctx.fillStyle = '#0f172a'
    ctx.fillText(label, left + 5, Math.max(2, top - fh - 1))
  }

  if ((result.incidents || []).length) {
    const bh = Math.max(28, Math.round(h * 0.06))
    ctx.fillStyle = boxColor
    ctx.fillRect(0, 0, w, bh)
    ctx.fillStyle = '#0f172a'
    ctx.font = `bold ${Math.max(13, Math.round(w / 60))}px Inter, sans-serif`
    ctx.fillText(
      `INCIDENT(S): ${result.incidents.length} · gravité max: ${gravMax}`,
      10, Math.max(4, (bh - Math.round(w / 60)) / 2 - 2),
    )
  }

  return canvas.toDataURL('image/png')
}
