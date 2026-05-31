import { cn } from '../../lib/cn'

// Accent = lime → texte foncé (slate-900) pour le contraste.
const variants = {
  primary: 'bg-ink text-bg hover:opacity-90 disabled:opacity-40',
  accent: 'bg-accent-500 text-slate-900 hover:bg-accent-400 disabled:bg-accent-200 shadow-card',
  secondary: 'bg-surface text-ink border border-line hover:bg-surface2',
  outline: 'bg-transparent border border-line text-ink hover:border-accent-500 hover:text-accent-700',
  ghost: 'bg-transparent text-muted hover:bg-surface2 hover:text-ink',
  danger: 'bg-rose-600 text-white hover:bg-rose-700 disabled:bg-rose-300',
}
const sizes = { sm: 'h-8 px-3 text-xs', md: 'h-10 px-4 text-sm', lg: 'h-11 px-5 text-base', icon: 'h-9 w-9' }

export function Button({ variant = 'primary', size = 'md', loading = false, className, children, disabled, ...props }) {
  return (
    <button
      disabled={disabled || loading}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-colors',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-500/50 focus-visible:ring-offset-1 focus-visible:ring-offset-bg',
        'disabled:cursor-not-allowed',
        variants[variant], sizes[size], className,
      )}
      {...props}
    >
      {loading && <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-r-transparent" />}
      {loading ? 'Chargement…' : children}
    </button>
  )
}
