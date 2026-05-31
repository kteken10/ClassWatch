import { useMemo, useState } from 'react'
import { toast } from 'sonner'
import { TriangleAlert, Gauge, Download, FileText, Trash2, History, Filter } from 'lucide-react'
import { PageHeader } from '../components/PageHeader'
import { HeroKpi, MiniStat } from '../components/Stats'
import { GravityDonut, Leaderboard } from '../components/GravityDonut'
import { Card, CardHeader, CardTitle, CardContent, Badge, Button, EmptyState } from '../components/ui'
import { useApp } from '../context/AppState'
import { lignesIncidents, GRAVITE_TONE, fmtDate, pct } from '../lib/format'
import { exportCSV, exportPDF } from '../lib/exports'

export function JournalPage() {
  const { journal, clearJournal } = useApp()
  const [typeFilter, setTypeFilter] = useState([])
  const [sevFilter, setSevFilter] = useState([])

  const lignes = useMemo(() => lignesIncidents(journal), [journal])
  const stats = useMemo(() => {
    const parType = {}, parSev = {}
    for (const l of lignes) {
      parType[l.type] = (parType[l.type] || 0) + 1
      parSev[l.severite] = (parSev[l.severite] || 0) + 1
    }
    return { nbAnalyses: journal.length, nbIncidents: lignes.length, nbGraves: parSev['élevé'] || 0, parType, parSev }
  }, [journal, lignes])

  const types = useMemo(() => [...new Set(lignes.map((l) => l.type))], [lignes])
  const sevs = ['faible', 'moyen', 'élevé']
  const filtered = lignes.filter((l) =>
    (!typeFilter.length || typeFilter.includes(l.type)) && (!sevFilter.length || sevFilter.includes(l.severite)))
  const toggle = (arr, set, v) => set(arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v])

  const ratio = stats.nbIncidents ? Math.round((100 * stats.nbGraves) / stats.nbIncidents) : 0
  const topTypes = Object.entries(stats.parType).sort((a, b) => b[1] - a[1]).slice(0, 6)

  return (
    <div>
      <PageHeader
        title="Journal d'incidents"
        description="Historique horodaté, répartition et export du rapport."
        actions={journal.length > 0 && (
          <Button variant="ghost" onClick={() => { clearJournal(); toast.success('Journal vidé.') }}>
            <Trash2 className="w-4 h-4" /> Vider
          </Button>
        )}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
        <div className="lg:col-span-2">
          <HeroKpi label="Analyses réalisées" value={stats.nbAnalyses}
            sub={`${stats.nbIncidents} incident(s) recensé(s) · ${stats.nbGraves} grave(s)`}
            ratio={ratio} ratioLabel="Part d'incidents graves" />
        </div>
        <div className="grid grid-rows-2 gap-3">
          <MiniStat icon={TriangleAlert} label="Incidents (total)" value={stats.nbIncidents} tone={stats.nbIncidents ? 'danger' : 'neutral'} />
          <MiniStat icon={Gauge} label="Incidents graves" value={stats.nbGraves} tone={stats.nbGraves ? 'danger' : 'success'} />
        </div>
      </div>

      {journal.length === 0 ? (
        <Card>
          <EmptyState icon={History} title="Journal vide"
            description="Lance une première analyse dans l'onglet Analyse pour alimenter le journal." />
        </Card>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader><CardTitle>Répartition par gravité</CardTitle></CardHeader>
              <CardContent><GravityDonut counts={stats.parSev} /></CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Types les plus fréquents</CardTitle></CardHeader>
              <CardContent><Leaderboard items={topTypes} /></CardContent>
            </Card>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-faint mr-1">
              <Filter className="w-3.5 h-3.5" /> Filtres
            </span>
            {types.map((t) => (
              <button key={t} onClick={() => toggle(typeFilter, setTypeFilter, t)}
                className={`px-2.5 h-7 rounded-lg text-xs font-medium border transition-colors ${
                  typeFilter.includes(t) ? 'border-accent-500 bg-accent-50 text-accent-700 dark:bg-accent-500/10 dark:text-accent-300'
                    : 'border-line text-muted hover:text-ink'}`}>{t}</button>
            ))}
            <span className="w-px h-5 bg-line mx-1" />
            {sevs.map((s) => (
              <button key={s} onClick={() => toggle(sevFilter, setSevFilter, s)}
                className={`px-2.5 h-7 rounded-lg text-xs font-medium border transition-colors capitalize ${
                  sevFilter.includes(s) ? 'border-accent-500 bg-accent-50 text-accent-700 dark:bg-accent-500/10 dark:text-accent-300'
                    : 'border-line text-muted hover:text-ink'}`}>{s}</button>
            ))}
            <span className="ml-auto text-xs text-muted tnum">{filtered.length} / {lignes.length}</span>
          </div>

          <Card className="overflow-hidden">
            <CardHeader><CardTitle>Incidents ({filtered.length})</CardTitle></CardHeader>
            <CardContent className="px-0 py-0">
              {filtered.length ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-surface2">
                      <tr className="text-[11px] uppercase tracking-wider text-muted">
                        <th className="text-left font-semibold px-5 py-3">Date / heure</th>
                        <th className="text-left font-semibold px-5 py-3">Source</th>
                        <th className="text-left font-semibold px-5 py-3">Image</th>
                        <th className="text-left font-semibold px-5 py-3">Type</th>
                        <th className="text-left font-semibold px-5 py-3">Gravité</th>
                        <th className="text-right font-semibold px-5 py-3">Conf.</th>
                        <th className="text-left font-semibold px-5 py-3">Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filtered.map((l, i) => (
                        <tr key={i} className="border-t border-line-soft hover:bg-surface2">
                          <td className="px-5 py-3 text-muted tnum whitespace-nowrap">{fmtDate(l.horodatage)}</td>
                          <td className="px-5 py-3 text-muted">{l.source}</td>
                          <td className="px-5 py-3 font-mono text-xs text-muted">{l.image}</td>
                          <td className="px-5 py-3 font-medium text-ink">{l.type}</td>
                          <td className="px-5 py-3"><Badge tone={GRAVITE_TONE[l.severite]}>{l.severite}</Badge></td>
                          <td className="px-5 py-3 text-right text-muted tnum">{pct(l.confiance)}</td>
                          <td className="px-5 py-3 text-ink">{l.description}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : <EmptyState icon={Filter} title="Aucun incident" description="Aucun incident ne correspond aux filtres." />}
            </CardContent>
          </Card>

          <div className="flex flex-wrap items-center gap-3">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-faint mr-1">Export du rapport</span>
            <Button variant="secondary" onClick={() => exportCSV(filtered)}><Download className="w-4 h-4" /> CSV</Button>
            <Button variant="secondary" onClick={() => exportPDF(filtered, stats)}><FileText className="w-4 h-4" /> PDF</Button>
          </div>
        </div>
      )}
    </div>
  )
}
