import * as RCheckbox from '@radix-ui/react-checkbox'
import { Check } from 'lucide-react'
import { cn } from '../../lib/cn'

export function Checkbox({ checked, onCheckedChange, label, id }) {
  const cid = id || `cb-${label}`
  return (
    <div className="flex items-center gap-2.5">
      <RCheckbox.Root
        id={cid}
        checked={checked}
        onCheckedChange={onCheckedChange}
        className={cn(
          'flex h-[18px] w-[18px] items-center justify-center rounded-[5px] border transition-colors',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-accent-500/40',
          checked ? 'bg-accent-500 border-accent-500' : 'bg-surface border-line hover:border-accent-400',
        )}
      >
        <RCheckbox.Indicator>
          <Check className="h-3.5 w-3.5 text-slate-900" strokeWidth={3} />
        </RCheckbox.Indicator>
      </RCheckbox.Root>
      {label && <label htmlFor={cid} className="text-sm text-ink cursor-pointer select-none">{label}</label>}
    </div>
  )
}
