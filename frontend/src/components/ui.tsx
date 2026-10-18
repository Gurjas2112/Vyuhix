import type { ReactNode } from 'react'
import { Area, AreaChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { inr, pct } from '../format'

export function PageHeader({ eyebrow, title, children }: { eyebrow: string; title: string; children?: ReactNode }) {
  return (
    <div className="mb-6 flex items-end gap-4">
      <div className="flex-1">
        <div className="eyebrow">{eyebrow}</div>
        <h1 className="font-display text-3xl font-bold tracking-tight mt-1">{title}</h1>
      </div>
      {children}
    </div>
  )
}

export function Stat({ label, value, sub, tone = 'ink', onClick }: { label: string; value: string; sub?: string; tone?: 'ink' | 'money' | 'ok'; onClick?: () => void }) {
  const color = tone === 'money' ? 'text-money' : tone === 'ok' ? 'text-ok' : 'text-ink'
  const body = (
    <>
      <div className="text-xs text-soft">{label}</div>
      <div className={`num text-2xl @[230px]:text-3xl font-bold mt-1 whitespace-nowrap ${color}`}>{value}</div>
      {sub && <div className="text-xs text-muted mt-1">{sub}</div>}
    </>
  )
  return onClick
    ? <button onClick={onClick} className="card @container p-5 text-left hover:border-money transition-colors" title="Trace this figure">{body}<div className="text-[11px] text-money mt-2">Trace this rupee →</div></button>
    : <div className="card @container p-5">{body}</div>
}

const STATUS: Record<string, string> = {
  evidenced: 'bg-[#e3f1ea] text-ok', planned: 'bg-[#e4ebfb] text-act', declared: 'bg-[#fdf3d8] text-warn', absent: 'bg-[#fbe4e1] text-bad',
}
export function StatusPill({ status }: { status: string }) {
  return <span className={`chip ${STATUS[status] ?? 'bg-line text-ink'}`}>{status}</span>
}

const SEV: Record<string, string> = {
  critical: 'bg-[#fbe4e1] text-bad', high: 'bg-[#fbe4e1] text-bad', medium: 'bg-[#fdf3d8] text-warn', low: 'bg-[#e4ebfb] text-act', info: 'bg-line/60 text-muted',
}
export function Sev({ s }: { s: string }) { return <span className={`chip ${SEV[s] ?? SEV.info}`}>{s}</span> }

export function LecChart({ lec, limit, height = 260 }: { lec: { loss: number; p_exceed: number }[]; limit?: number; height?: number }) {
  const data = lec.filter(d => d.loss > 0).map(d => ({ x: d.loss / 1e7, p: d.p_exceed * 100 }))
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 20, bottom: 24, left: 4 }}>
        <defs>
          <linearGradient id="lecFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#f2994a" stopOpacity={0.45} />
            <stop offset="100%" stopColor="#f2994a" stopOpacity={0.05} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#e7e3d9" vertical={false} />
        <XAxis dataKey="x" type="number" scale="log" domain={['dataMin', 'dataMax']} tickFormatter={v => v >= 1 ? `₹${v.toFixed(0)} Cr` : `₹${Math.round(v * 100)} L`}
          tick={{ fontSize: 12, fill: '#6a7179' }} label={{ value: 'Annual loss (log scale)', position: 'insideBottom', offset: -14, fontSize: 12, fill: '#6a7179' }} />
        <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 12, fill: '#6a7179' }} width={44} />
        <Tooltip formatter={(v: number) => [`${v.toFixed(1)}%`, 'Chance of exceeding']} labelFormatter={(v: number) => `Loss ${inr(v * 1e7)} or more`} />
        <Area type="monotone" dataKey="p" stroke="#b85c12" strokeWidth={2} fill="url(#lecFill)" isAnimationActive={false} />
        {limit !== undefined && limit > 0 && (
          <ReferenceLine x={limit / 1e7} stroke="#2f5fd0" strokeWidth={2} strokeDasharray="5 4"
            label={{ value: `Policy limit ${inr(limit)}`, position: 'top', fill: '#2f5fd0', fontSize: 12 }} />
        )}
      </AreaChart>
    </ResponsiveContainer>
  )
}

export function Bar({ value, max, tone = '#f2994a' }: { value: number; max: number; tone?: string }) {
  return <div className="h-2 rounded-full bg-line/60 overflow-hidden"><div className="h-full rounded-full" style={{ width: `${Math.max(2, (value / Math.max(max, 1)) * 100)}%`, background: tone }} /></div>
}

export { inr, pct }
