import { useEffect, useState } from 'react'
import { CartesianGrid, Line, LineChart, ReferenceDot, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../api'
import { PageHeader, Stat, inr, pct } from '../components/ui'

export default function Plan() {
  const [budget, setBudget] = useState(500000)
  const [plan, setPlan] = useState<any | null>(null)
  const [frontier, setFrontier] = useState<any[]>([])

  useEffect(() => { api('/frontier').then(d => setFrontier(d.points)) }, [])
  useEffect(() => {
    const t = setTimeout(() => api('/plan', { budget_inr: budget }).then(setPlan), 200)
    return () => clearTimeout(t)
  }, [budget])

  const data = frontier.map(p => ({ x: p.budget_inr / 1e5, y: p.eal_after / 1e7 }))
  return (
    <div className="max-w-7xl">
      <PageHeader eyebrow="Plan" title="The best use of a fixed budget" />
      <section className="card p-5">
        <div className="flex items-end gap-6">
          <div className="flex-1">
            <label htmlFor="budget" className="text-sm font-medium">Budget this quarter</label>
            <input id="budget" type="range" min={0} max={1500000} step={25000} value={budget} onChange={e => setBudget(Number(e.target.value))}
              className="w-full accent-[#2f5fd0] mt-2" />
            <div className="flex justify-between text-xs text-soft"><span>₹0</span><span>₹15 L</span></div>
          </div>
          <div className="num text-4xl font-bold text-act w-40 text-right">{inr(budget)}</div>
        </div>
      </section>

      {plan && (
        <div className="grid grid-cols-4 gap-4 mt-4">
          <Stat label="Plan cost" value={inr(plan.cost_inr)} sub={`${plan.chosen.length} controls`} />
          <Stat label="Expected annual loss" value={inr(plan.eal_after)} tone="ok" sub={`from ${inr(plan.eal_before)}`} />
          <Stat label="Reduction" value={pct(plan.reduction_pct)} sub="re-simulated, not estimated" />
          <Stat label="1-in-20-year loss" value={inr(plan.var95_after)} sub={plan.var95_after === 0 ? `from ${inr(plan.var95_before)} · now fewer than 1 year in 20 sees any loss` : `from ${inr(plan.var95_before)}`} />
        </div>
      )}

      <div className="grid grid-cols-[1fr_420px] gap-4 mt-4">
        <section className="card p-5">
          <h2 className="font-display text-lg font-bold">Investment vs remaining risk</h2>
          <p className="text-sm text-muted">Each point is an optimised plan, re-simulated. The curve flattens where extra spend stops paying off.</p>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data} margin={{ top: 16, right: 24, bottom: 24, left: 4 }}>
              <CartesianGrid stroke="#e7e3d9" />
              <XAxis dataKey="x" type="number" tickFormatter={v => `₹${v} L`} tick={{ fontSize: 12 }} label={{ value: 'Budget', position: 'insideBottom', offset: -14, fontSize: 12 }} />
              <YAxis tickFormatter={v => `₹${v.toFixed(1)} Cr`} tick={{ fontSize: 12 }} width={70} />
              <Tooltip formatter={(v: number) => [inr(v * 1e7), 'EAL after plan']} labelFormatter={(v: number) => `Budget ${inr(v * 1e5)}`} />
              <Line type="stepAfter" dataKey="y" stroke="#2f5fd0" strokeWidth={2.5} dot={{ r: 3 }} isAnimationActive={false} />
              {plan && <ReferenceDot x={budget / 1e5} y={plan.eal_after / 1e7} r={7} fill="#b85c12" stroke="#fff" />}
            </LineChart>
          </ResponsiveContainer>
        </section>
        <section className="card p-5">
          <h2 className="font-display text-lg font-bold">Chosen controls</h2>
          {plan?.controls.length ? (
            <ul className="mt-3 space-y-2">
              {plan.controls.map((c: any) => (
                <li key={c.id} className="rounded-xl border border-line p-3">
                  <div className="flex justify-between gap-3"><span className="text-sm font-medium">{c.label}</span><span className="num text-sm">{inr(c.cost_inr)}</span></div>
                  <div className="text-xs text-muted mt-1">Alone removes <b className="text-ok">{inr(c.eal_removed_alone)}</b> a year · {inr(c.rupees_removed_per_rupee)} per ₹1 spent</div>
                </li>
              ))}
            </ul>
          ) : <p className="text-sm text-muted mt-2">Raise the budget to fund the first control.</p>}
          {plan && (
            <>
              <p className="text-xs text-muted mt-3">Paths removed: {plan.paths.removed.join(', ') || 'none'}. {plan.rosi !== null && `Return on security investment: ${plan.rosi.toFixed(0)}×.`}</p>
              <p className="text-[11px] text-soft mt-2">{plan.method}</p>
            </>
          )}
        </section>
      </div>
    </div>
  )
}
