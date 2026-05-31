import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import { fmtDate } from './format'

function download(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

const stamp = () => {
  const d = new Date(); const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}_${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`
}

export function exportCSV(lignes) {
  const head = ['id_analyse', 'horodatage', 'source', 'image', 'type', 'gravite', 'confiance', 'description']
  const rows = lignes.map((l) => [
    l.entreeId, fmtDate(l.horodatage, true), l.source, l.image, l.type, l.severite,
    `${Math.round(l.confiance * 100)}%`, `"${(l.description || '').replace(/"/g, '""')}"`,
  ])
  const csv = [head.join(';'), ...rows.map((r) => r.join(';'))].join('\n')
  download(new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' }), `classwatch_incidents_${stamp()}.csv`)
}

export function exportPDF(lignes, stats) {
  const doc = new jsPDF({ unit: 'pt', format: 'a4' })
  doc.setFontSize(18); doc.setTextColor(15, 23, 42)
  doc.text("ClassWatch — Rapport d'incidents", 40, 48)
  doc.setFontSize(10); doc.setTextColor(100, 116, 139)
  doc.text(`Analyses : ${stats.nbAnalyses}   |   Incidents : ${lignes.length}`, 40, 66)
  autoTable(doc, {
    startY: 84,
    head: [['Horodatage', 'Type', 'Gravité', 'Conf.', 'Description']],
    body: lignes.map((l) => [
      fmtDate(l.horodatage), l.type, l.severite, `${Math.round(l.confiance * 100)}%`, l.description,
    ]),
    styles: { fontSize: 9, cellPadding: 5, textColor: [30, 41, 59] },
    headStyles: { fillColor: [15, 23, 42], textColor: [255, 255, 255] },
    alternateRowStyles: { fillColor: [248, 250, 252] },
    columnStyles: { 4: { cellWidth: 220 } },
  })
  doc.save(`classwatch_rapport_${stamp()}.pdf`)
}
