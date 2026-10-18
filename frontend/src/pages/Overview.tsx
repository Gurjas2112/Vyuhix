import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useRisk } from '../App'
import { Bar, LecChart, PageHeader, Stat, inr, pct } from '../components/ui'

export default function Overview() {
  const { run, org, user, trace } = useRisk()
  const [plan, setPlan] = useState<any | null>(null)
  const isBroker = user.role === 'broker'

  useEffect(() => {
    if (!isBroker) api('/plan', { budget_inr: 500000 }).then(setPlan).catch(() => setPlan(null))
  }, [isBroker])

  if (!run || !org) return <p className="text-muted">Loading…</p>
  const s = run.summary
  const limit = org.org.current_policy.limit_inr
  const ranked = (run.paths ?? []).slice().sort((a: any, b: any) => b.eal - a.eal)
  const top = ranked[0]?.eal ?? 1

  return (
    <div className="max-w-7xl">
      <PageHeader eyebrow={isBroker ? 'Shared client summary' : 'Overview'} title={`${org.org.name}: rupees at risk`} />

      <div className="grid grid-cols-4 gap-4">
        <Stat label="Expected annual loss" value={inr(s.eal)} tone="money" sub="Average per year"
          onClick={isBroker ? undefined : () => trace({ kind: 'eal' })} />
        <Stat label="1-in-20-year loss (VaR95)" value={inr(s.var95)} sub={`Policy limit ${inr(limit)}`}
          onClick={isBroker ? undefined : () => trace({ kind: 'var95' })} />
        <Stat label="Worst-5% average (CVaR95)" value={inr(s.cvar95)} sub="Size of the bad years" />
        <Stat label="Chance of a loss this year" value={pct(s.p_any_loss)} sub={`P90 year ${inr(s.p90)}`} />
      </div>

      <div className="grid grid-cols-5 gap-4 mt-4">
        <section className="card p-5 col-span-3">
          <h2 className="font-display text-lg font-bold">Loss curve vs policy limit</h2>
          <p className="text-sm text-muted mb-2">Chance that a year's loss exceeds each amount. Anything right of the dashed line is uninsured.</p>
          <LecChart lec={run.lec} limit={limit} height={250} />
        </section>

        <section className="card p-5 col-span-2 flex flex-col">
          {isBroker ? (
            <>
              <h2 className="font-display text-lg font-bold">Insurance view</h2>
              <p className="text-sm text-muted mt-1">Attack-path detail stays with the client. You can see loss quantiles, insurability evidence and the coverage gap.</p>
              <Link to="/insurance" className="btn-primary mt-4 self-start">Open insurance view</Link>
            </>
          ) : (
            <>
              <h2 className="font-display text-lg font-bold">Best use of ₹5 lakh</h2>
              {plan ? (
                <>
                  <p className="text-sm text-muted mt-1">Optimised and re-simulated. Costs {inr(plan.cost_inr)}.</p>
                  <ul className="mt-3 space-y-2 text-sm flex-1">
                    {plan.controls.map((c: any) => (
                      <li key={c.id} className="flex justify-between gap-3 border-b border-line/70 pb-2">
                        <span>{c.label}</span><span className="num text-soft">{inr(c.cost_inr)}</span>
                      </li>
                    ))}
                  </ul>
                  <div className="mt-3 rounded-xl bg-[#e3f1ea] p-3">
                    <div className="text-xs text-ok font-semibold">Expected annual loss</div>
                    <div className="num text-xl font-bold">{inr(plan.eal_before)} → {inr(plan.eal_after)}</div>
                    <div className="text-xs text-muted">{pct(plan.reduction_pct)} lower</div>
                  </div>
                  <Link to="/plan" className="text-sm text-act mt-3">Adjust the budget →</Link>
                </>
              ) : <p className="text-sm text-muted mt-2">Computing…</p>}
            </>
          )}
        </section>
      </div>

      {!isBroker && (
        <div className="grid grid-cols-5 gap-4 mt-4">
          <section className="card p-5 col-span-3">
            <div className="flex items-baseline">
              <h2 className="font-display text-lg font-bold flex-1">Where the rupees come from</h2>
              <Link to="/paths" className="text-sm text-act">Open path map →</Link>
            </div>
            <ul className="mt-3 space-y-3">
              {ranked.slice(0, 4).map((p: any) => (
                <li key={p.id}>
                  <button className="w-full text-left" onClick={() => trace({ kind: 'path', id: p.id })}>
                    <div className="flex gap-3 text-sm">
                      <span className="num font-semibold w-7">{p.id}</span>
                      <span className="flex-1 truncate">{p.text}</span>
                      <span className="num font-semibold text-money">{inr(p.eal)}</span>
                    </div>
                    <div className="ml-10 mt-1.5"><Bar value={p.eal} max={top} /></div>
                  </button>
                </li>
              ))}
            </ul>
          </section>
          <section className="card p-5 col-span-2">
            <h2 className="font-display text-lg font-bold">Live signals</h2>
            <dl className="mt-3 space-y-3 text-sm">
              <div><dt className="text-soft text-xs">IDS alerts on the edge server (7 days)</dt>
                <dd className="font-medium">{run.soc.alerts_in_window} alerts, internet attempts weighted ×{run.soc.multiplier_applied}</dd></div>
              <div><dt className="text-soft text-xs">Most common signature</dt><dd>{run.soc.top_signature}</dd></div>
              <div><dt className="text-soft text-xs">Known-exploited catalogue</dt><dd>{org.feeds.kev.version} · {org.feeds.kev.count} relevant entries</dd></div>
              <div><dt className="text-soft text-xs">Copilot mode</dt><dd>{org.llm_mode === 'claude' ? 'Claude (tool calling)' : 'Offline, deterministic'}</dd></div>
            </dl>
          </section>
        </div>
      )}
    </div>
  )
}
