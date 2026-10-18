import { useEffect, useState } from 'react'
import { Bar as RBar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../api'
import { useRisk } from '../App'
import { LecChart, PageHeader, Stat, inr, pct } from '../components/ui'

const COMP = [
  ['incident_response', 'Incident response', '#0e1726'], ['notification', 'Notification', '#2f5fd0'],
  ['downtime', 'Downtime', '#9dbbf5'], ['ransom', 'Ransom', '#b85c12'], ['regulatory', 'Regulatory', '#f2994a'], ['fraud', 'Fraud', '#6a7179'],
] as const

export default function Loss() {
  const { run: base, org, trace } = useRisk()
  const [tefInternet, setTefInternet] = useState(0.25)
  const [tefPhish, setTefPhish] = useState(0.5)
  const [kevFloor, setKevFloor] = useState(0.9)
  const [soc, setSoc] = useState(true)
  const [dpdp, setDpdp] = useState(true)
  const [run, setRun] = useState<any | null>(null)
  const [ms, setMs] = useState<number | null>(null)

  useEffect(() => {
    const t = setTimeout(async () => {
      const t0 = performance.now()
      const r = await api('/run', {
        tef: { internet: tefInternet, phishing: tefPhish },
        assumptions: { edge_probability: { kev_floor_internet: kevFloor }, soc_multiplier: { enabled: soc }, regulatory: { dpdp_enabled: dpdp } },
      })
      setMs(Math.round(performance.now() - t0)); setRun(r)
    }, 150)
    return () => clearTimeout(t)
  }, [tefInternet, tefPhish, kevFloor, soc, dpdp])

  const r = run ?? base
  if (!r || !org) return <p className="text-muted">Loading…</p>
  const s = r.summary
  const comp = Object.entries(r.components as Record<string, Record<string, number>>).map(([j, c]) => ({ jewel: j.replace('_', ' '), ...Object.fromEntries(Object.entries(c).map(([k, v]) => [k, v / 1e5])) }))

  return (
    <div className="max-w-7xl">
      <PageHeader eyebrow="Loss" title="10,000 simulated years">
        {ms !== null && <span className="text-xs text-soft">Re-simulated in {ms} ms</span>}
      </PageHeader>
      <div className="grid grid-cols-4 gap-4">
        <Stat label="Expected annual loss" value={inr(s.eal)} tone="money" onClick={() => trace({ kind: 'eal' })} />
        <Stat label="Median year (P50)" value={inr(s.p50)} sub="Most years see no loss" />
        <Stat label="1-in-20-year loss (VaR95)" value={inr(s.var95)} onClick={() => trace({ kind: 'var95' })} />
        <Stat label="Worst-5% average (CVaR95)" value={inr(s.cvar95)} />
      </div>

      <div className="grid grid-cols-[1fr_340px] gap-4 mt-4">
        <section className="card p-5">
          <h2 className="font-display text-lg font-bold">Loss-exceedance curve</h2>
          <LecChart lec={r.lec} limit={org.org.current_policy.limit_inr} height={300} />
          <h2 className="font-display text-lg font-bold mt-4">What the yearly loss is made of (₹ lakh)</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={comp} layout="vertical" margin={{ left: 20, right: 20 }}>
              <CartesianGrid stroke="#e7e3d9" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="jewel" tick={{ fontSize: 12 }} width={90} />
              <Tooltip formatter={(v: number, n: string) => [inr(v * 1e5), COMP.find(c => c[0] === n)?.[1] ?? n]} />
              <Legend formatter={(v: string) => COMP.find(c => c[0] === v)?.[1] ?? v} wrapperStyle={{ fontSize: 12 }} />
              {COMP.map(([k, , color]) => <RBar key={k} dataKey={k} stackId="a" fill={color} isAnimationActive={false} />)}
            </BarChart>
          </ResponsiveContainer>
        </section>

        <aside className="card p-5 space-y-5" aria-label="Assumptions">
          <div>
            <h2 className="font-display text-lg font-bold">Assumptions</h2>
            <p className="text-xs text-soft">Demo values, editable. Numbers above re-run as you change them.</p>
          </div>
          <Slider label="Targeted internet attempts / year" value={tefInternet} min={0.05} max={1} step={0.05} onChange={setTefInternet} fmt={v => v.toFixed(2)} />
          <Slider label="Successful phishes / year" value={tefPhish} min={0} max={2} step={0.1} onChange={setTefPhish} fmt={v => v.toFixed(1)} />
          <Slider label="Probability floor for KEV-listed, internet-facing flaws" value={kevFloor} min={0.3} max={1} step={0.05} onChange={setKevFloor} fmt={pct} />
          <Toggle label={`Weight attempts by IDS alerts (×${r.soc.multiplier_applied || 2} when ≥5 alerts in 7 days)`} checked={soc} onChange={setSoc} />
          <Toggle label="Include DPDP penalty exposure (applies from 13 May 2027)" checked={dpdp} onChange={setDpdp} />
          <div className="text-xs text-muted border-t border-line pt-3 space-y-1">
            <div>Relative standard error: {pct(s.rel_std_error)}</div>
            <div>Attempts simulated: {s.attempts_simulated.toLocaleString('en-IN')}</div>
            <div>Seed: {r.assumptions.simulation.seed} (same seed ⇒ same numbers)</div>
          </div>
        </aside>
      </div>
    </div>
  )
}

function Slider({ label, value, min, max, step, onChange, fmt }: { label: string; value: number; min: number; max: number; step: number; onChange: (v: number) => void; fmt: (v: number) => string }) {
  const id = label.replace(/\W+/g, '-').toLowerCase()
  return (
    <div>
      <div className="flex justify-between text-sm"><label htmlFor={id}>{label}</label><span className="num font-semibold">{fmt(value)}</span></div>
      <input id={id} type="range" min={min} max={max} step={step} value={value} onChange={e => onChange(Number(e.target.value))} className="w-full accent-[#2f5fd0]" />
    </div>
  )
}
function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className="flex items-start gap-2 text-sm cursor-pointer">
      <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} className="mt-1 accent-[#2f5fd0]" /> {label}
    </label>
  )
}
