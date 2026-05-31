import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

// Combine des classes Tailwind en résolvant les conflits (règle d'or SDEN).
export function cn(...inputs) {
  return twMerge(clsx(inputs))
}
