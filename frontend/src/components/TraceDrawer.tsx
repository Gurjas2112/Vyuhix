import { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import { useRisk } from '../App'
import { inr, pct } from '../format'
import { Bar } from './ui'

export type TraceTarget = { kind: 'eal' } | { kind: 'var95' } | { kind: 'path'; id: string }

const COMP_LABEL: Record<string, string> = {
  incident_response: 'Incident response & forensics', notification: 'Customer notification', downtime: 'Downtime',
  ransom: 'Ransom / extortion', regulatory: 'Regulatory (DPDP, forward-looking)', fraud: 'Fraud loss',
}

export default function TraceDrawer({ target, onClose }: { target: TraceTarget; onClose: () => void }) {
  const { run } = useRisk()
  const [open, setOpen] = useState<string | null>(target.kind === 'path' ? target.id : null)
  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', k); return () => window.removeEventListener('keydown', k)
  }, [onClose])
  if (!run?.paths) return null
  const paths = [...run.paths].sort((a: any, b: any) => b.eal - a.eal)
  const max = paths[0]?.eal ?? 1
  const s = run.summary
  const comps = run.components as Record<string, Record<string, number>>

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-ink/30" onClick={onClose}>
      <aside role="dialog" aria-label="Trace this rupee" onClick={e => e.stopPropagation()}
        className="w-[560px] max-w-full h-full bg-paper shadow-2xl overflow-y-auto">
        <div className="sticky top-0 bg-paper border-b border-line px-6 py-4 flex items-start gap-3">
          <div className="flex-1">
            <div className="eyebrow">Trace this rupee</div>
            <div className="font-display text-2xl font-bold mt-1">
              {target.kind === 'var95' ? `VaR95 ${inr(s.var95)}` : target.kind === 'path' ? `Path ${target.id}` : `EAL ${inr(s.eal)}`}
            </div>
            <p className="text-sm text-muted mt-1">
              {target.kind === 'var95'
                ? `In 1 simulated year out of 20, losses exceed ${inr(s.var95)}. The tail is driven by the same paths below.`
                : `Average annual loss across ${s.attempts_simulated.toLocaleString('en-IN')} simulated attempts over 10,000 years, split by the paths that caused it.`}
            </p>
          </div>
          <button onClick={onClose} aria-label="Close" className="p-1 rounded hover:bg-line/50"><X className="size-5" /></button>
        </div>

        <section className="px-6 py-5">
          <h3 className="text-sm font-semibold mb-3">1 · Paths → rupees</h3>
          <ul className="space-y-2">
            {paths.map((p: any) => (
              <li key={p.id} className="border border-line rounded-xl">
                <button className="w-full text-left px-4 py-3" onClick={() => setOpen(open === p.id ? null : p.id)} aria-expanded={open === p.id}>
                  <div className="flex items-baseline gap-3">
                    <span className="num font-semibold w-8">{p.id}</span>
                    <span className="flex-1 text-sm truncate">{p.text}</span>
                    <span className="num font-semibold text-money">{inr(p.eal)}</span>
                  </div>
                  <div className="mt-2 ml-11"><Bar value={p.eal} max={max} /></div>
                </button>
                {open === p.id && (
                  <ol className="px-4 pb-4 ml-11 space-y-3">
                    {p.edges.map((eid: string) => {
                      const b = run.edge_basis[eid]
                      return (
                        <li key={eid} className="text-sm">
                          <div className="flex gap-2"><span className="num text-soft w-8">{eid}</span><span className="flex-1">{edgeText(run, eid)}</span>
                            <span className="num">{pct(run.edge_p[eid])}</span></div>
                          <div className="ml-10 mt-1 text-xs text-muted">
                            {b.source === 'feeds'
                              ? <>EPSS {b.epss} · {b.in_kev ? <b className="text-bad">in KEV</b> : 'not in KEV'} · {b.internet_facing ? 'internet-facing' : 'internal'}{b.in_kev && b.internet_facing ? ` → floor ${b.kev_floor}` : ''}</>
                              : <>Probability {b.p} from evidence</>}
                          </div>
                          <div className="ml-10 mt-1 flex flex-wrap gap-1">
                            {edgeEvidence(run, eid).map((ev: string) => <code key={ev} className="chip bg-ink text-sand font-mono">{ev}</code>)}
                          </div>
                        </li>
                      )
                    })}
                    <li className="text-xs text-muted">Per attempt, this path succeeds with probability {pct(p.probability_per_attempt)} (product of its edges).</li>
                  </ol>
                )}
              </li>
            ))}
          </ul>
        </section>

        <section className="px-6 pb-5">
          <h3 className="text-sm font-semibold mb-3">2 · What the loss is made of (per year, averaged)</h3>
          {Object.entries(comps).map(([jewel, c]) => (
            <div key={jewel} className="mb-4">
              <div className="text-xs font-semibold text-soft uppercase tracking-wide mb-2">{jewel.replace('_', ' ')}</div>
              {Object.entries(c).filter(([, v]) => v > 0).sort((a, b) => b[1] - a[1]).map(([k, v]) => (
                <div key={k} className="flex items-center gap-3 text-sm py-1">
                  <span className="w-60">{COMP_LABEL[k]}</span>
                  <div className="flex-1"><Bar value={v} max={s.eal} tone="#9dbbf5" /></div>
                  <span className="num w-20 text-right">{inr(v)}</span>
                </div>
              ))}
            </div>
          ))}
        </section>

        <section className="px-6 pb-8">
          <h3 className="text-sm font-semibold mb-2">3 · Assumptions behind it</h3>
          <ul className="text-sm text-muted list-disc ml-5 space-y-1">
            <li>Attempts per year: {Object.entries(run.tef).map(([k, v]) => `${k} ${(v as number).toFixed(2)}`).join(' · ')}</li>
            <li>SOC signal: {run.soc.alerts_in_window} IDS alerts in {run.soc.window_days} days → internet attempts ×{run.soc.multiplier_applied}</li>
            <li>KEV floor for internet-facing assets: {run.assumptions.edge_probability.kev_floor_internet}</li>
            <li>DPDP regulatory exposure: {run.assumptions.regulatory.dpdp_enabled ? 'included (forward-looking, from 13 May 2027)' : 'excluded'}</li>
            <li>Seed {run.assumptions.simulation.seed}, {run.assumptions.simulation.n_years.toLocaleString('en-IN')} years, relative standard error {pct(s.rel_std_error)}</li>
            <li className="text-xs">All demo values are labelled assumptions and editable on the Loss page.</li>
          </ul>
        </section>
      </aside>
    </div>
  )
}

function edgeText(run: any, eid: string): string {
  return run.edge_info?.[eid]?.text ?? eid
}
function edgeEvidence(run: any, eid: string): string[] {
  return run.edge_info?.[eid]?.evidence ?? []
}
