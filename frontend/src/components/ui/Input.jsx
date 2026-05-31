import { cn } from '../../lib/cn'

export function Input({ className, ...props }) {
  return (
    <input
      className={cn(
        'w-full h-10 px-3 rounded-lg border border-line bg-surface text-sm text-ink',
        'placeholder:text-faint focus:outline-none focus:ring-2 focus:ring-accent-500/25 focus:border-accent-500',
        className,
      )}
      {...props}
    />
  )
}
