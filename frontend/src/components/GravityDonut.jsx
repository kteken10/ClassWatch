import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import { GRAVITE_COLOR } from '../lib/format'

export function GravityDonut({ counts }) {
  const data = [
    { name: 'faible', value: counts.faible || 0 },
    { name: 'moyen', value: counts.moyen || 0 },
    { name: 'élevé', value: counts['élevé'] || 0 },
  ].filter((d) => d.value > 0)
  const total = data.reduce((a, b) => a + b.value, 0)

  if (!total) return <div className="text-sm text-muted py-8 text-center">Aucun incident à répartir.</div>

  return (
    <div className="flex items-center gap-5">
      <div className="relative" style={{ width: 130, height: 130 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" innerRadius={42} outerRadius={62} paddingAngle={2} stroke="none">
              {data.map((d) => <Cell key={d.name} fill={GRAVITE_COLOR[d.name]} />)}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-ink tnum leading-none">{total}</span>
          <span className="text-[10px] uppercase tracking-wider text-muted mt-0.5">incidents</span>
        </div>
      </div>
      <div className="flex-1 space-y-2">
        {data.map((d) => (
          <div key={d.name} className="flex items-center gap-2 text-sm">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: GRAVITE_COLOR[d.name] }} />
            <span className="text-muted capitalize flex-1">{d.name}</span>
            <span className="font-semibold text-ink tnum">{d.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function Leaderboard({ items }) {
  if (!items.length) return <div className="text-sm text-muted">Aucune donnée.</div>
  const max = Math.max(...items.map((i) => i[1])) || 1
  return (
    <ul className="space-y-2.5">
      {items.map(([name, count], i) => (
        <li key={name} className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="text-ink truncate">{name}</span>
            <span className="text-muted tnum">{count}</span>
          </div>
          <div className="h-1.5 rounded-full bg-surface2 overflow-hidden">
            <div
              className={i === 0 ? 'h-full bg-accent-500 rounded-full' : 'h-full bg-slate-400 dark:bg-slate-500 rounded-full'}
              style={{ width: `${Math.round((count / max) * 100)}%` }}
            />
          </div>
        </li>
      ))}
    </ul>
  )
}
