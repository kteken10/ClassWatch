import { cn } from '../lib/cn'

const TONE_BG = {
  neutral: 'bg-surface2 text-muted',
  accent: 'bg-accent-50 text-accent-700 dark:bg-accent-500/10 dark:text-accent-300',
  success: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-300',
  warning: 'bg-amber-50 text-amber-600 dark:bg-amber-500/10 dark:text-amber-300',
  danger: 'bg-rose-50 text-rose-600 dark:bg-rose-500/10 dark:text-rose-300',
}

export function MiniStat({ icon: Icon, label, value, tone = 'neutral' }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-line bg-surface px-4 py-3 shadow-card">
      <div className={cn('p-2 rounded-lg shrink-0', TONE_BG[tone] || TONE_BG.neutral)}>
        <Icon className="w-4 h-4" />
      </div>
      <div className="min-w-0">
        <div className="text-[11px] uppercase tracking-wider text-muted leading-tight">{label}</div>
        <div className="text-xl font-bold text-ink leading-tight mt-0.5 tnum">{value}</div>
      </div>
    </div>
  )
}

export function HeroKpi({ label, value, sub, ratio, ratioLabel }) {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-[rgb(var(--hero))] text-white p-6 border border-line shadow-card h-full">
      <div className="absolute -right-10 -top-10 w-48 h-48 rounded-full bg-accent-500/25 blur-3xl" />
      <div className="absolute -left-6 -bottom-6 w-32 h-32 rounded-full bg-accent-500/10 blur-2xl" />
      <div className="relative">
        <div className="text-[11px] uppercase tracking-wider text-white/50">{label}</div>
        <div className="text-5xl font-extrabold mt-1.5 tnum">{value}</div>
        {sub && <div className="text-sm text-white/70 mt-1.5">{sub}</div>}
        {ratio != null && (
          <div className="mt-5">
            <div className="flex justify-between text-[11px] text-white/60 mb-1.5">
              <span>{ratioLabel}</span><span className="font-medium text-white/90 tnum">{ratio}%</span>
            </div>
            <div className="h-1.5 rounded-full bg-white/10 overflow-hidden">
              <div className="h-full bg-accent-500 rounded-full transition-all" style={{ width: `${ratio}%` }} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
