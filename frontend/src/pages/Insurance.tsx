import { useEffect, useState } from 'react'
import { api } from '../api'
import { useRisk } from '../App'
import { LecChart, PageHeader, Stat, StatusPill, inr, pct } from '../components/ui'

export default function Insurance() {
  const { org } = useRisk()
  const [limit, setLimit] = useState<number | null>(null)
  const [withPlan, setWithPlan] = useState(false)
  const [plan, setPlan] = useState<string[]>([])
  const [v, setV] = useState<any | null>(null)

  useEffect(() => { if (org && limit === null) setLimit(org.org.current_policy.limit_inr) }, [org, limit])
  useEffect(() => { if (withPlan && !plan.length) api('/plan', { budget_inr: 500000 }).then(p => setPlan(p.chosen)).catch(() => setPlan([])) }, [withPlan, plan.length])
  useEffect(() => {
    if (limit === null) return
    const t = setTimeout(() => api('/insurance', { limit_inr: limit, controls: withPlan ? plan : [] }).then(setV), 120)
    return () => clearTimeout(t)
  }, [limit, withPlan, plan])

  if (!v || limit === null) return <p className="text-muted">Loading…</p>
  return (
    <div className="max-w-7xl">
      <PageHeader eyebrow="Insurance" title="Is the policy limit enough?">
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={withPlan} onChange={e => setWithPlan(e.target.checked)} className="accent-[#2f5fd0]" /> Show with the ₹5 lakh plan applied</label>
      </PageHeader>
      <div className="grid grid-cols-4 gap-4">
        <Stat label="Insurability score" value={`${v.insurability_score}/100`} tone={v.insurability_score >= 60 ? 'ok' : 'money'} sub="Evidence-weighted controls insurers ask about" />
        <Stat label="Coverage gap at VaR95" value={inr(v.coverage_gap_inr)} tone="money" sub={`VaR95 ${inr(v.var95)} vs limit ${inr(v.current_limit_inr)}`} />
        <Stat label="Limit that covers a 1-in-100-year loss" value={inr(v.recommended_limit_inr)} sub={`VaR99 ${inr(v.var99)} · indicative, rounded to ₹50 L`} />
        <Stat label="Chance a year exceeds the limit" value={pct(v.p_exceed_limit)} />
      </div>

      <div className="grid grid-cols-[1fr_400px] gap-4 mt-4">
        <section className="card p-5">
          <h2 className="font-display text-lg font-bold">Drag the policy limit</h2>
          <LecChart lec={v.lec} limit={limit} height={280} />
          <label htmlFor="limit" className="text-sm font-medium">Policy limit: <span className="num text-act">{inr(limit)}</span></label>
          <input id="limit" type="range" min={1e7} max={4e8} step={5e6} value={limit} onChange={e => setLimit(Number(e.target.value))} className="w-full accent-[#2f5fd0]" />
          <p className="text-xs text-soft mt-3 border-t border-line pt-3">{v.disclaimer}</p>
        </section>
        <section className="card p-5">
          <h2 className="font-display text-lg font-bold">Controls insurers ask about</h2>
          <ul className="mt-3 space-y-2.5">
            {v.controls.map((c: any) => (
              <li key={c.key} className="text-sm">
                <div className="flex items-start gap-2"><span className="flex-1">{c.label}</span><StatusPill status={c.status} /></div>
                <div className="text-xs text-muted mt-0.5">{c.note} · weight {c.weight} · <code className="font-mono">{c.evidence}</code></div>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-4">
        <section className="card p-5">
          <h2 className="font-display text-lg font-bold">Proposal answers, with evidence</h2>
          <table className="w-full text-sm mt-2">
            <tbody>
              {v.proposal_answers.map((a: any) => (
                <tr key={a.q} className="border-b border-line/70 align-top">
                  <td className="py-2 pr-3">{a.q}</td><td className="py-2 pr-3 font-medium">{a.a}</td><td className="py-2"><code className="text-xs font-mono text-soft">{a.evidence}</code></td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
        <section className="card p-5">
          <h2 className="font-display text-lg font-bold">Claims readiness</h2>
          <ul className="mt-2 space-y-2.5">
            {v.claims_readiness.map((c: any) => (
              <li key={c.item} className="flex items-start gap-2 text-sm"><span className="flex-1">{c.item}</span><StatusPill status={c.status} /></li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  )
}
