import { Users, TriangleAlert, Gauge, ArrowRight, ShieldCheck } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, Badge, EmptyState } from './ui'
import { MiniStat } from './Stats'
import { GRAVITE_TONE, NIVEAU_TONE, NIVEAU_DOT, pct, gravMax } from '../lib/format'

function IncidentsTable({ incidents }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-[11px] uppercase tracking-wider text-muted">
            <th className="text-left font-semibold px-3 pb-2.5">Type</th>
            <th className="text-left font-semibold px-3 pb-2.5">Gravité</th>
            <th className="text-right font-semibold px-3 pb-2.5">Conf.</th>
            <th className="text-left font-semibold px-3 pb-2.5">Description</th>
          </tr>
        </thead>
        <tbody>
          {incidents.map((inc, i) => (
            <tr key={i} className="border-t border-line-soft hover:bg-surface2">
              <td className="px-3 py-2.5 font-medium text-ink">{inc.type}</td>
              <td className="px-3 py-2.5"><Badge tone={GRAVITE_TONE[inc.severite]}>{inc.severite}</Badge></td>
              <td className="px-3 py-2.5 text-right text-muted tnum">{pct(inc.confiance)}</td>
              <td className="px-3 py-2.5 text-ink">{inc.description}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export function ResultView({ result, annotated }) {
  const gmax = gravMax(result.incidents)
  const incTone = result.incidents?.length ? 'danger' : 'success'
  const gravTone = GRAVITE_TONE[gmax] || 'neutral'

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <Card className="lg:col-span-3 overflow-hidden">
          <CardHeader><CardTitle>Image annotée</CardTitle></CardHeader>
          <CardContent>
            {annotated ? <img src={annotated} alt="annotée" className="w-full rounded-lg" />
              : <p className="text-sm text-muted">Pas d'image annotée.</p>}
          </CardContent>
        </Card>
        <div className="lg:col-span-2 space-y-3">
          <MiniStat icon={Users} label="Personnes" value={result.nb_personnes} />
          <MiniStat icon={TriangleAlert} label="Incidents" value={result.incidents?.length || 0} tone={incTone} />
          <MiniStat icon={Gauge} label="Gravité max" value={gmax} tone={gravTone} />
          {result.resume && (
            <div className="rounded-xl border border-line bg-surface2 px-4 py-3 text-sm text-ink">
              <span className="font-semibold">Résumé. </span>{result.resume}
            </div>
          )}
          {result.latence_ms != null && <p className="text-xs text-faint px-1">Analyse en {result.latence_ms} ms.</p>}
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle>Détail des incidents</CardTitle></CardHeader>
        <CardContent>
          {result.incidents?.length ? <IncidentsTable incidents={result.incidents} />
            : <EmptyState icon={ShieldCheck} title="Aucun incident détecté" description="La scène analysée ne présente pas d'incident." />}
        </CardContent>
      </Card>

      {result.observations?.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Observations &amp; points de surveillance</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {result.observations.map((o, i) => (
              <div key={i} className="flex items-start gap-3 rounded-xl border border-line bg-surface px-4 py-3">
                <span className="w-2.5 h-2.5 rounded-full mt-1.5 shrink-0" style={{ backgroundColor: NIVEAU_DOT[o.niveau] || '#94a3b8' }} />
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-ink">{o.point}</div>
                  <div className="text-sm text-muted">{o.detail}</div>
                </div>
                <span className="ml-auto shrink-0"><Badge tone={NIVEAU_TONE[o.niveau] || 'neutral'}>{o.niveau}</Badge></span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {result.recommandations?.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Recommandations</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {result.recommandations.map((r, i) => (
              <div key={i} className="flex items-center gap-3 rounded-xl border border-line bg-surface px-4 py-2.5 text-sm text-ink">
                <ArrowRight className="w-4 h-4 text-accent-600 shrink-0" />{r}
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
