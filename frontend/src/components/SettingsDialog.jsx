import { useState } from 'react'
import { toast } from 'sonner'
import { KeyRound } from 'lucide-react'
import { useApp } from '../context/AppState'
import { Dialog, DialogTrigger, DialogContent, DialogClose, Button, Input } from './ui'

export function SettingsDialog({ children }) {
  const { apiKey, saveKey } = useApp()
  const [val, setVal] = useState(apiKey)

  return (
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent
        title="Clé API Gemini"
        description="La clé est stockée localement (navigateur) et utilisée pour appeler Gemini. Elle n'est jamais envoyée ailleurs que vers Google."
      >
        <div className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-ink">Clé API</label>
            <Input
              type="password" value={val} onChange={(e) => setVal(e.target.value)}
              placeholder="AIza… ou AQ.…"
            />
            <p className="text-xs text-muted">
              Crée une clé sur aistudio.google.com/apikey. ⚠️ En app 100% front, la clé est
              visible côté navigateur : restreins-la par domaine en production.
            </p>
          </div>
          <div className="flex justify-end gap-2">
            <DialogClose asChild><Button variant="secondary">Fermer</Button></DialogClose>
            <DialogClose asChild>
              <Button variant="accent" onClick={() => { saveKey(val.trim()); toast.success('Clé enregistrée.') }}>
                <KeyRound className="w-4 h-4" /> Enregistrer
              </Button>
            </DialogClose>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
