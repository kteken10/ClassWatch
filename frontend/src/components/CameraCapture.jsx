import { useEffect, useRef, useState } from 'react'
import { Camera, AlertTriangle } from 'lucide-react'
import { Button } from './ui'

export function CameraCapture({ onCapture }) {
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const [error, setError] = useState(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function start() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false })
        if (cancelled) { stream.getTracks().forEach((t) => t.stop()); return }
        streamRef.current = stream
        if (videoRef.current) { videoRef.current.srcObject = stream; await videoRef.current.play(); setReady(true) }
      } catch {
        setError('Accès caméra refusé ou indisponible (HTTPS requis hors localhost).')
      }
    }
    start()
    return () => { cancelled = true; if (streamRef.current) streamRef.current.getTracks().forEach((t) => t.stop()) }
  }, [])

  const snap = () => {
    const video = videoRef.current
    if (!video) return
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth; canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)
    canvas.toBlob((blob) => {
      if (blob) onCapture(new File([blob], `camera_${Date.now()}.jpg`, { type: 'image/jpeg' }))
    }, 'image/jpeg', 0.92)
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 text-sm text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/30 rounded-xl px-4 py-3">
        <AlertTriangle className="w-4 h-4 shrink-0" /> {error}
      </div>
    )
  }
  return (
    <div className="space-y-3">
      <div className="rounded-xl overflow-hidden border border-line bg-black aspect-video flex items-center justify-center">
        <video ref={videoRef} className="w-full h-full object-cover" playsInline muted />
      </div>
      <Button variant="accent" onClick={snap} disabled={!ready} className="w-full">
        <Camera className="w-4 h-4" /> Prendre la photo
      </Button>
    </div>
  )
}
