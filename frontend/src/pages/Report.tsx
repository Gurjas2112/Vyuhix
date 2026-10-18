import { useEffect, useState } from 'react'
import { Printer } from 'lucide-react'
import { api } from '../api'
import { inr, pct } from '../components/ui'

export default function Report() {
  const [r, setR] = useState<any | null>(null)
  useEffect(() => { api('/report').then(setR) }, [])
  if (!r) return <p className="text-muted">Loading…</p>
  const s = r.summary
  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-end mb-3 print:hidden"><button className="btn-primary" onClick={() => window.print()}><Printer className="size-4" /> Print or save as PDF</button></div>
      <article className="bg-paper border border-line rounded-2xl p-10 print:border-0">
        <div className="eyebrow">Board briefing · cyber risk</div>
        <h1 className="font-display text-3xl font-bold mt-1">{r.org.name}</h1>
        <p className="text-sm text-soft">Generated {new Date(r.generated_at).toLocaleString('en-IN')} · Vyuhix proof of concept</p>

        <div className="grid grid-cols-3 gap-6 mt-8">
          <Big label="Expected loss per year" value={inr(s.eal)} />
          <Big label="1-in-20-year loss" value={inr(s.var95)} />
          <Big label="Chance of a loss this year" value={pct(s.p_any_loss)} />
        </div>

        <h2 className="font-display text-xl font-bold mt-10">Where it comes from</h2>
        <ol className="mt-3 space-y-2 text-sm list-decimal ml-5">
          {r.top_paths.map((p: any) => <li key={p.id}><b className="num">{inr(p.eal)}/yr</b>: {p.text}</li>)}
        </ol>

        <h2 className="font-display text-xl font-bold mt-8">Recommended plan (₹15 lakh ceiling)</h2>
        <ul className="mt-3 text-sm space-y-1 list-disc ml-5">
          {r.plan.controls.map((c: any) => <li key={c.id}>{c.label} ({inr(c.cost_inr)})</li>)}
        </ul>
        <p className="text-sm mt-2">Cost {inr(r.plan.cost_inr)}; expected annual loss falls from {inr(r.plan.eal_before)} to <b>{inr(r.plan.eal_after)}</b> ({pct(r.plan.reduction_pct)} lower).</p>

        <h2 className="font-display text-xl font-bold mt-8">Insurance</h2>
        <p className="text-sm mt-2">Current limit {inr(r.insurance.current_limit_inr)}; 1-in-20-year loss {inr(r.insurance.var95)}; gap {inr(r.insurance.coverage_gap_inr)}. A limit near {inr(r.insurance.recommended_limit_inr)} would cover a 1-in-100-year loss. Insurability score {r.insurance.insurability_score}/100.</p>
        <p className="text-xs text-soft mt-2">{r.insurance.disclaimer}</p>

        <p className="text-xs text-soft mt-10 border-t border-line pt-3">{r.assumptions_note} Fictional organisation; synthetic data.</p>
      </article>
    </div>
  )
}

function Big({ label, value }: { label: string; value: string }) {
  return <div><div className="text-xs text-soft">{label}</div><div className="num text-3xl font-bold text-money mt-1">{value}</div></div>
}
