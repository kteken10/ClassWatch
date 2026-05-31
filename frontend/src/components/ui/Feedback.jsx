import { cn } from '../../lib/cn'

export function Spinner({ className }) {
  return (
    <span className={cn('inline-block h-5 w-5 animate-spin rounded-full border-2 border-current border-r-transparent text-accent-500', className)} />
  )
}

export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center text-center py-12 px-6">
      {Icon && (
        <div className="p-4 rounded-2xl bg-surface2 border border-line mb-4">
          <Icon className="w-7 h-7 text-faint" strokeWidth={1.75} />
        </div>
      )}
      <div className="text-base font-semibold text-ink">{title}</div>
      {description && <p className="text-sm text-muted mt-1 max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
