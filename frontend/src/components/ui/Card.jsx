import { cn } from '../../lib/cn'

export function Card({ className, ...props }) {
  return <div className={cn('rounded-2xl border border-line bg-surface shadow-card', className)} {...props} />
}
export function CardHeader({ className, ...props }) {
  return <div className={cn('px-5 py-4 border-b border-line-soft', className)} {...props} />
}
export function CardTitle({ className, ...props }) {
  return <h3 className={cn('text-base font-semibold text-ink', className)} {...props} />
}
export function CardDescription({ className, ...props }) {
  return <p className={cn('text-sm text-muted mt-1', className)} {...props} />
}
export function CardContent({ className, ...props }) {
  return <div className={cn('px-5 py-4', className)} {...props} />
}
export function CardFooter({ className, ...props }) {
  return <div className={cn('px-5 py-3 border-t border-line-soft bg-surface2/50 rounded-b-2xl', className)} {...props} />
}
