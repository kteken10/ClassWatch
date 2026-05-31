import * as RSwitch from '@radix-ui/react-switch'
import { cn } from '../../lib/cn'

export function Switch({ checked, onCheckedChange, id }) {
  return (
    <RSwitch.Root
      id={id}
      checked={checked}
      onCheckedChange={onCheckedChange}
      className={cn(
        'relative h-5 w-9 rounded-full transition-colors outline-none focus-visible:ring-2 focus-visible:ring-accent-500/40',
        checked ? 'bg-accent-500' : 'bg-line',
      )}
    >
      <RSwitch.Thumb className="block h-4 w-4 rounded-full bg-white shadow transition-transform translate-x-0.5 data-[state=checked]:translate-x-[18px]" />
    </RSwitch.Root>
  )
}
