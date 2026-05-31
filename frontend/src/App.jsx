import { useState } from 'react'
import { Menu, X, Eye } from 'lucide-react'
import { Sidebar } from './components/Sidebar'
import { AnalysePage } from './pages/AnalysePage'
import { JournalPage } from './pages/JournalPage'

export default function App() {
  const [page, setPage] = useState('analyse')
  const [drawer, setDrawer] = useState(false)
  const go = (p) => { setPage(p); setDrawer(false) }

  return (
    <div className="flex h-screen overflow-hidden bg-bg">
      <aside className="hidden lg:flex lg:flex-col lg:w-64 shrink-0 bg-surface border-r border-line">
        <Sidebar page={page} setPage={go} />
      </aside>

      {drawer && (
        <div className="lg:hidden fixed inset-0 z-40">
          <div className="absolute inset-0 bg-slate-900/50" onClick={() => setDrawer(false)} />
          <aside className="absolute left-0 top-0 h-full w-72 bg-surface border-r border-line shadow-xl">
            <Sidebar page={page} setPage={go} />
          </aside>
        </div>
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <header className="lg:hidden flex items-center gap-3 px-4 py-3 bg-surface border-b border-line">
          <button onClick={() => setDrawer(true)} className="p-1.5 rounded-lg hover:bg-surface2">
            {drawer ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-ink flex items-center justify-center"><Eye className="w-4 h-4 text-accent-400" /></div>
            <span className="font-extrabold text-ink">Class<span className="text-accent-600">Watch</span></span>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto">
          <div className="max-w-[1400px] mx-auto w-full p-4 sm:p-6 lg:p-8">
            {page === 'analyse' ? <AnalysePage /> : <JournalPage />}
          </div>
        </main>
      </div>
    </div>
  )
}
