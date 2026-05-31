import { cn } from '../../lib/cn'

export function SegmentedTabs({ value, onChange, options, className }) {
  return (
    <div className={cn('inline-flex p-1 gap-1 rounded-lg bg-surface2 border border-line', className)}>
      {options.map((opt) => {
        const active = opt.value === value
        const Icon = opt.icon
        return (
          <button
            key={opt.value}
            type="button"
            onClick={() => onChange(opt.value)}
            className={cn(
              'inline-flex items-center justify-center gap-2 px-3.5 h-8 rounded-md text-sm font-semibold transition-colors flex-1',
              active ? 'bg-surface text-accent-700 shadow-card dark:text-accent-300' : 'text-muted hover:text-ink',
            )}
          >
            {Icon && <Icon className="w-4 h-4" />}
            {opt.label}
          </button>
        )
      })}
    </div>
  )
}
