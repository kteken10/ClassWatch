import { useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import { Upload, Camera, Image as ImageIcon, Bolt, Sparkles, Cpu, KeyRound } from 'lucide-react'
import { PageHeader } from '../components/PageHeader'
import { CameraCapture } from '../components/CameraCapture'
import { ResultView } from '../components/ResultView'
import { SettingsDialog } from '../components/SettingsDialog'
import {
  Card, CardHeader, CardTitle, CardDescription, CardContent,
  Button, SegmentedTabs, Checkbox, EmptyState,
} from '../components/ui'
import { useApp } from '../context/AppState'
import { analyzeWithGemini } from '../lib/gemini'
import { analyzeMock } from '../lib/mock'
import { annotate } from '../lib/annotate'
import { POINTS_SURVEILLANCE } from '../lib/schema'

export function AnalysePage() {
  const { addEntry, weather, apiKey, hasKey } = useApp()
  const [mode, setMode] = useState('upload')
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [backend, setBackend] = useState(hasKey ? 'gemini' : 'mock')
  const [points, setPoints] = useState(POINTS_SURVEILLANCE.map((p) => p.libelle))
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [annotated, setAnnotated] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef(null)

  useEffect(() => { setBackend(hasKey ? 'gemini' : 'mock') }, [hasKey])

  const pickFile = (f) => {
    if (!f) return
    setFile(f); setPreview(URL.createObjectURL(f)); setResult(null); setAnnotated(null)
  }
  const togglePoint = (l) => setPoints((p) => (p.includes(l) ? p.filter((x) => x !== l) : [...p, l]))

  const run = async () => {
    if (!file) return
    setBusy(true); setResult(null)
    try {
      const res = backend === 'mock'
        ? await analyzeMock(file, { points })
        : await analyzeWithGemini(file, { points, apiKey })
      const img = await annotate(file, res).catch(() => null)
      if (weather) res.meteo = weather
      res.horodatage = new Date().toISOString()
      res.source = mode === 'camera' ? 'camera' : 'upload'
      setResult(res); setAnnotated(img)
      addEntry({ id: Date.now(), horodatage: res.horodatage, source: res.source, nomImage: file.name, result: res, annotated: img })
      toast.success('Analyse enregistrée dans le journal.')
    } catch (e) {
      toast.error(e.message || 'Échec de l’analyse.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <PageHeader
        title="Analyse"
        description="Importe une image de salle de classe ou prends une photo pour détecter et qualifier les incidents."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-5">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between gap-4">
            <div>
              <CardTitle>Source</CardTitle>
              <CardDescription>Importer un fichier ou utiliser la caméra.</CardDescription>
            </div>
            <SegmentedTabs
              value={mode}
              onChange={(v) => { setMode(v); setFile(null); setPreview(null); setResult(null) }}
              options={[{ value: 'upload', label: 'Importer', icon: Upload }, { value: 'camera', label: 'Caméra', icon: Camera }]}
            />
          </CardHeader>
          <CardContent>
            {mode === 'upload' ? (
              <>
                <input ref={inputRef} type="file" accept="image/png,image/jpeg,image/webp" className="hidden"
                  onChange={(e) => pickFile(e.target.files?.[0])} />
                <button
                  type="button" onClick={() => inputRef.current?.click()}
                  onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={(e) => { e.preventDefault(); setDragOver(false); pickFile(e.dataTransfer.files?.[0]) }}
                  className={`w-full rounded-xl border-[1.5px] border-dashed px-6 py-10 flex flex-col items-center justify-center gap-2 transition-colors ${
                    dragOver ? 'border-accent-500 bg-accent-50/40 dark:bg-accent-500/5' : 'border-line bg-surface2 hover:border-accent-400'
                  }`}
                >
                  <div className="p-3 rounded-xl bg-surface border border-line"><Upload className="w-5 h-5 text-faint" /></div>
                  <div className="text-sm font-medium text-ink">Glisse une image ou clique pour parcourir</div>
                  <div className="text-xs text-muted">JPG, PNG, WEBP</div>
                </button>
              </>
            ) : <CameraCapture onCapture={pickFile} />}

            {preview && (
              <div className="mt-4 flex items-start gap-4">
                <img src={preview} alt="aperçu" className="w-40 rounded-lg border border-line" />
                <div className="text-sm text-muted">
                  <div className="font-medium text-ink">{file?.name}</div>
                  <div className="mt-0.5">{file && `${(file.size / 1024).toFixed(0)} Ko`}</div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Options d'analyse</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-wider text-faint mb-2">Moteur</p>
              <SegmentedTabs value={backend} onChange={setBackend} className="w-full"
                options={[{ value: 'gemini', label: 'Gemini', icon: Sparkles }, { value: 'mock', label: 'Démo', icon: Cpu }]} />
              {backend === 'gemini' && !hasKey && (
                <div className="mt-2 text-[11px] text-amber-600 flex items-center gap-1.5">
                  <KeyRound className="w-3.5 h-3.5" />
                  Clé absente —
                  <SettingsDialog><button className="underline hover:text-amber-700">en ajouter une</button></SettingsDialog>
                </div>
              )}
            </div>
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-wider text-faint mb-2">Points de surveillance</p>
              <div className="space-y-2">
                {POINTS_SURVEILLANCE.map((p) => (
                  <Checkbox key={p.cle} label={p.libelle} checked={points.includes(p.libelle)}
                    onCheckedChange={() => togglePoint(p.libelle)} />
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="mb-6">
        <Button variant="accent" size="lg" onClick={run}
          disabled={!file || (backend === 'gemini' && !hasKey)} loading={busy}>
          {!busy && <Bolt className="w-4 h-4" />} Lancer l'analyse
        </Button>
      </div>

      {result ? <ResultView result={result} annotated={annotated} /> : (
        !file && (
          <Card>
            <EmptyState icon={ImageIcon} title="Aucune image pour le moment"
              description="Importe une image ou prends une photo, puis lance l'analyse pour voir les incidents détectés." />
          </Card>
        )
      )}
    </div>
  )
}
