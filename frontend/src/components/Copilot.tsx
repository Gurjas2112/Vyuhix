import { useEffect, useRef, useState } from 'react'
import { CheckCircle2, Send, ShieldAlert, X } from 'lucide-react'
import { api } from '../api'
import { useRisk } from '../App'

type Msg = { role: 'user' | 'bot'; text: string; meta?: any }

const SUGGEST: Record<string, string[]> = {
  broker: ['Are they adequately insured?', 'What limit would cover the 1-in-20-year loss?'],
  default: ['What is our biggest risk?', 'What if we enforce MFA on admins?', 'We have 5 lakh budget, what should we buy?', 'Explain P2', "What is HDFC's cyber risk?"],
}

export default function Copilot({ onClose }: { onClose: () => void }) {
  const { user } = useRisk()
  const [msgs, setMsgs] = useState<Msg[]>([{ role: 'bot', text: 'Ask about losses, paths, what-ifs, budgets or insurance. Every figure I give comes from the engine and is checked before you see it.' }])
  const [q, setQ] = useState('')
  const [busy, setBusy] = useState(false)
  const end = useRef<HTMLDivElement>(null)
  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth' }) }, [msgs])

  async function ask(text: string) {
    if (!text.trim() || busy) return
    setMsgs(m => [...m, { role: 'user', text }]); setQ(''); setBusy(true)
    try {
      const r = await api('/copilot', { question: text })
      setMsgs(m => [...m, { role: 'bot', text: r.answer, meta: r }])
    } catch (e: any) {
      setMsgs(m => [...m, { role: 'bot', text: e.message }])
    } finally { setBusy(false) }
  }

  return (
    <aside className="w-[400px] shrink-0 border-l border-line bg-paper flex flex-col" aria-label="Copilot">
      <div className="px-4 py-3 border-b border-line flex items-center gap-2">
        <div className="flex-1">
          <div className="font-display font-bold">Copilot</div>
          <div className="text-[11px] text-soft">Tool-calling · numbers grounded in engine output</div>
        </div>
        <button onClick={onClose} aria-label="Close copilot" className="p-1 rounded hover:bg-line/50"><X className="size-4" /></button>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3" aria-live="polite">
        {msgs.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'flex justify-end' : ''}>
            <div className={`rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed max-w-[92%] ${m.role === 'user' ? 'bg-act text-white' : 'bg-sand border border-line'}`}>
              {m.text}
              {m.meta && (
                <div className="mt-2 pt-2 border-t border-line/70 flex flex-wrap gap-1 items-center">
                  {m.meta.grounded
                    ? <span className="chip bg-[#e3f1ea] text-ok"><CheckCircle2 className="size-3" /> grounded</span>
                    : <span className="chip bg-[#fbe4e1] text-bad"><ShieldAlert className="size-3" /> blocked figure</span>}
                  <span className="chip bg-line/60 text-muted">{m.meta.mode}</span>
                  {m.meta.tools.map((t: any, j: number) => <code key={j} className="chip bg-ink text-sand font-mono">{t.tool}()</code>)}
                  {m.meta.evidence.slice(0, 4).map((e: string) => <code key={e} className="chip bg-[#e4ebfb] text-act font-mono">{e}</code>)}
                </div>
              )}
            </div>
          </div>
        ))}
        {busy && <div className="text-xs text-soft">Calling tools…</div>}
        <div ref={end} />
      </div>
      <div className="px-4 pb-2 flex flex-wrap gap-1.5">
        {(SUGGEST[user.role] ?? SUGGEST.default).map(s => (
          <button key={s} onClick={() => ask(s)} className="chip border border-line bg-white hover:border-act text-muted">{s}</button>
        ))}
      </div>
      <form className="p-3 border-t border-line flex gap-2" onSubmit={e => { e.preventDefault(); ask(q) }}>
        <label htmlFor="copilot-q" className="sr-only">Ask the copilot</label>
        <input id="copilot-q" value={q} onChange={e => setQ(e.target.value)} placeholder="Ask a question…" maxLength={500}
          className="flex-1 rounded-lg border border-line bg-white px-3 py-2 text-sm" />
        <button className="btn-primary" disabled={busy} aria-label="Send"><Send className="size-4" /></button>
      </form>
    </aside>
  )
}
