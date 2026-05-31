import * as RDialog from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import { cn } from '../../lib/cn'

export const Dialog = RDialog.Root
export const DialogTrigger = RDialog.Trigger
export const DialogClose = RDialog.Close

export function DialogContent({ className, title, description, children }) {
  return (
    <RDialog.Portal>
      <RDialog.Overlay className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm data-[state=open]:animate-in" />
      <RDialog.Content
        className={cn(
          'fixed left-1/2 top-1/2 z-50 w-[92vw] max-w-lg -translate-x-1/2 -translate-y-1/2',
          'rounded-2xl border border-line bg-surface p-6 shadow-xl max-h-[85vh] overflow-y-auto',
          className,
        )}
      >
        {title && <RDialog.Title className="text-lg font-bold text-ink">{title}</RDialog.Title>}
        {description && <RDialog.Description className="text-sm text-muted mt-1">{description}</RDialog.Description>}
        <div className={title ? 'mt-4' : ''}>{children}</div>
        <RDialog.Close className="absolute right-4 top-4 p-1 rounded-lg text-muted hover:bg-surface2 hover:text-ink">
          <X className="w-4 h-4" />
        </RDialog.Close>
      </RDialog.Content>
    </RDialog.Portal>
  )
}
