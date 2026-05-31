import { Eye, ScanSearch, History, Moon, Sun, KeyRound, ShieldCheck, ShieldAlert } from 'lucide-react'
import { cn } from '../lib/cn'
import { useApp } from '../context/AppState'
import { WeatherWidget } from './WeatherWidget'
import { SettingsDialog } from './SettingsDialog'
import { Switch } from './ui'

const NAV = [
  { id: 'analyse', label: 'Analyse', icon: ScanSearch },
  { id: 'journal', label: 'Journal', icon: History },
]

function NavLink({ item, active, onClick }) {
  const Icon = item.icon
  return (
    <button
      onClick={onClick}
      className={cn(
        'group w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
        active ? 'bg-accent-500 text-slate-900 shadow-card' : 'text-muted hover:bg-surface2 hover:text-ink',
      )}
    >
      <Icon className="w-4 h-4 shrink-0" />
      <span>{item.label}</span>
    </button>
  )
}

export function Sidebar({ page, setPage }) {
  const { dark, setDark, journal, hasKey } = useApp()

  return (
    <div className="flex flex-col h-full">
      <div className="px-5 py-5 border-b border-line-soft">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-ink flex items-center justify-center shrink-0">
            <Eye className="w-5 h-5 text-accent-400" />
          </div>
          <div>
            <div className="text-lg font-extrabold tracking-tight text-ink leading-none">
              Class<span className="text-accent-600">Watch</span>
            </div>
            <div className="text-[11px] text-muted mt-1">Surveillance de classe</div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
        <div className="space-y-1">
          <p className="px-3 mb-1 text-[11px] font-semibold uppercase tracking-wider text-faint">Vue d'ensemble</p>
          {NAV.map((item) => (
            <NavLink key={item.id} item={item} active={page === item.id} onClick={() => setPage(item.id)} />
          ))}
        </div>
        <div className="space-y-2">
          <p className="px-3 text-[11px] font-semibold uppercase tracking-wider text-faint">Météo &amp; climat</p>
          <WeatherWidget />
        </div>
      </div>

      <div className="px-4 py-4 border-t border-line-soft space-y-3">
        <SettingsDialog>
          <button className="w-full flex items-center justify-between text-sm text-muted hover:text-ink transition-colors">
            <span className="inline-flex items-center gap-2"><KeyRound className="w-4 h-4" /> Clé Gemini</span>
            {hasKey
              ? <span className="inline-flex items-center gap-1 text-emerald-600 dark:text-emerald-400 text-xs"><ShieldCheck className="w-3.5 h-3.5" /> OK</span>
              : <span className="inline-flex items-center gap-1 text-amber-600 text-xs"><ShieldAlert className="w-3.5 h-3.5" /> Absente</span>}
          </button>
        </SettingsDialog>
        <div className="flex items-center justify-between">
          <span className="inline-flex items-center gap-2 text-sm text-muted">
            {dark ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />} Mode sombre
          </span>
          <Switch checked={dark} onCheckedChange={setDark} />
        </div>
        <div className="text-[11px] text-faint tnum">
          {journal.length} analyse{journal.length > 1 ? 's' : ''} enregistrée{journal.length > 1 ? 's' : ''}
        </div>
      </div>
    </div>
  )
}
