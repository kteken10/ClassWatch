import { cn } from '../../lib/cn'

const TONES = {
  neutral: 'bg-surface2 text-muted ring-line',
  accent: 'bg-accent-50 text-accent-700 ring-accent-200 dark:bg-accent-500/10 dark:text-accent-300 dark:ring-accent-500/30',
  success: 'bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:ring-emerald-500/30',
  warning: 'bg-amber-50 text-amber-800 ring-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:ring-amber-500/30',
  danger: 'bg-rose-50 text-rose-700 ring-rose-200 dark:bg-rose-500/10 dark:text-rose-300 dark:ring-rose-500/30',
  mono: 'bg-ink text-bg ring-ink',
}

export function Badge({ tone = 'neutral', className, children, ...props }) {
  return (
    <span
      className={cn('inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium ring-1 ring-inset',
        TONES[tone] || TONES.neutral, className)}
      {...props}
    >
      {children}
    </span>
  )
}
