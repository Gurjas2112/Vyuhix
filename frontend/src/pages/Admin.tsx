import { useEffect, useState } from 'react'
import { CheckCircle2, RefreshCw, ShieldAlert, Zap } from 'lucide-react'
import { api } from '../api'
import { useRisk } from '../App'
import { PageHeader, Stat } from '../components/ui'

const TABS = ['Overview', 'Feeds', 'Guardrails', 'Audit log', 'Users'] as const

export default function Admin() {
  const { reload } = useRisk()
  const [tab, setTab] = useState<(typeof TABS)[number]>('Overview')
  const [o, setO] = useState<any | null>(null)
  const [guards, setGuards] = useState<any[]>([])
  const [audit, setAudit] = useState<any[]>([])
  const [verify, setVerify] = useState<any | null>(null)
  const [msg, setMsg] = useState<string | null>(null)

  const load = async () => {
    const [a, g, au] = await Promise.all([api('/admin/overview'), api('/admin/guardrails'), api('/admin/audit')])
    setO(a); setGuards(g); setAudit(au)
  }
  useEffect(() => { load() }, [])
  if (!o) return <p className="text-muted">Loading…</p>

  const calls = o.copilot.reduce((n: number, c: any) => n + c.n, 0)
  const grounded = o.copilot.reduce((n: number, c: any) => n + (c.grounded ?? 0), 0)
  const simulate = async () => { const r = await api('/admin/feeds/simulate-kev-update', {}); setMsg(r.message); await load(); await reload() }
  const reset = async () => { await api('/admin/feeds/reset', {}); setMsg('KEV feed back on the frozen snapshot.'); await load(); await reload() }

  return (
    <div className="max-w-7xl">
      <PageHeader eyebrow="Platform operations" title="Admin console" />
      <div className="flex gap-1 border-b border-line mb-5" role="tablist">
        {TABS.map(t => (
          <button key={t} role="tab" aria-selected={tab === t} onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm -mb-px border-b-2 ${tab === t ? 'border-act text-act font-medium' : 'border-transparent text-muted'}`}>{t}</button>
        ))}
      </div>

      {tab === 'Overview' && (
        <>
          <div className="grid grid-cols-4 gap-4">
            <Stat label="Users" value={String(o.users.length)} sub="across demo tenants" />
            <Stat label="Open guardrail events" value={String(o.guardrails_open)} tone="money" sub="injection, refused scans, blocked figures" />
            <Stat label="Copilot answers" value={String(calls)} sub={`${grounded} grounded · mode ${o.llm_mode}`} />
            <Stat label="Audit entries" value={String(o.audit_rows)} sub="hash-chained, append-only" />
          </div>
          <section className="card p-5 mt-4">
            <h2 className="font-display text-lg font-bold">Recent jobs</h2>
            <table className="w-full text-sm mt-2">
              <thead className="text-left text-xs text-soft uppercase"><tr><th className="py-2">#</th><th>Kind</th><th>Status</th><th>By</th><th>Detail</th><th>At (UTC)</th></tr></thead>
              <tbody>
                {o.jobs.map((j: any) => (
                  <tr key={j.id} className="border-t border-line/70">
                    <td className="py-2 num">{j.id}</td><td>{j.kind}</td>
                    <td><span className={`chip ${j.status === 'done' ? 'bg-[#e3f1ea] text-ok' : j.status === 'refused' ? 'bg-[#fbe4e1] text-bad' : 'bg-line'}`}>{j.status}</span></td>
                    <td className="text-xs">{j.actor}</td>
                    <td className="text-xs text-muted">{j.detail?.findings !== undefined ? `${j.detail.findings} findings, ${j.detail.guardrail_events} guardrail` : j.detail?.reason ?? ''}</td>
                    <td className="text-xs text-soft">{j.at}</td>
                  </tr>
                ))}
                {!o.jobs.length && <tr><td colSpan={6} className="py-3 text-muted">No jobs yet.</td></tr>}
              </tbody>
            </table>
          </section>
        </>
      )}

      {tab === 'Feeds' && (
        <div className="grid grid-cols-2 gap-4">
          <section className="card p-5">
            <h2 className="font-display text-lg font-bold">Known-exploited vulnerabilities (KEV)</h2>
            <dl className="text-sm mt-3 space-y-1.5">
              <div><dt className="inline text-soft">State: </dt><dd className="inline font-medium">{o.feeds.kev.state}</dd></div>
              <div><dt className="inline text-soft">Catalogue: </dt><dd className="inline">{o.feeds.kev.version} · {o.feeds.kev.count} entries</dd></div>
              <div className="text-xs text-muted">{o.feeds.kev.title}</div>
            </dl>
            <div className="flex gap-2 mt-4">
              <button className="btn-primary" onClick={simulate}><Zap className="size-4" /> Load simulated KEV update</button>
              <button className="btn-ghost" onClick={reset}><RefreshCw className="size-4" /> Reset</button>
            </div>
            {msg && <p role="status" className="text-sm mt-3 rounded-lg bg-[#fdecd8] text-[#7a3f00] p-3">{msg}</p>}
          </section>
          <section className="card p-5">
            <h2 className="font-display text-lg font-bold">Exploit prediction (EPSS) and IDS</h2>
            <p className="text-sm mt-3">EPSS snapshot {o.feeds.epss.score_date} · {o.feeds.epss.count} CVEs</p>
            <p className="text-xs text-muted">{o.feeds.epss.title}</p>
            <p className="text-sm mt-3">Suricata: {o.feeds.soc.alerts_in_window} alerts in {o.feeds.soc.window_days} days on {o.feeds.soc.target}</p>
          </section>
        </div>
      )}

      {tab === 'Guardrails' && (
        <section className="card p-5">
          <h2 className="font-display text-lg font-bold flex items-center gap-2"><ShieldAlert className="size-5 text-warn" /> Guardrail events</h2>
          <ul className="mt-3 divide-y divide-line/70">
            {guards.map(g => (
              <li key={g.id} className="py-2.5 text-sm flex gap-3">
                <span className="chip bg-[#fdf1e6] text-warn self-start">{g.type}</span>
                <div className="flex-1"><code className="font-mono text-xs">{g.source}</code>
                  <div className="text-xs text-muted">{g.detail?.text ?? g.detail?.reason ?? JSON.stringify(g.detail)}</div></div>
                <span className="text-xs text-soft">{g.at}</span>
              </li>
            ))}
            {!guards.length && <li className="py-3 text-muted text-sm">No events.</li>}
          </ul>
        </section>
      )}

      {tab === 'Audit log' && (
        <section className="card p-5">
          <div className="flex items-center">
            <h2 className="font-display text-lg font-bold flex-1">Tamper-evident audit log</h2>
            <button className="btn-primary" onClick={async () => setVerify(await api('/admin/audit/verify', {}))}><CheckCircle2 className="size-4" /> Verify chain</button>
          </div>
          {verify && (
            <p role="status" className={`text-sm mt-3 rounded-lg p-3 ${verify.ok ? 'bg-[#e3f1ea] text-ok' : 'bg-[#fbe4e1] text-bad'}`}>
              {verify.ok ? `Chain intact: ${verify.rows} entries, head ${verify.head.slice(0, 16)}…` : `Chain broken at entry ${verify.first_broken_id}`}
            </p>
          )}
          <table className="w-full text-sm mt-3">
            <thead className="text-left text-xs text-soft uppercase"><tr><th className="py-2">#</th><th>Action</th><th>Actor</th><th>Target</th><th>Hash</th><th>At (UTC)</th></tr></thead>
            <tbody>
              {audit.map(a => (
                <tr key={a.id} className="border-t border-line/70">
                  <td className="py-1.5 num">{a.id}</td><td>{a.action}</td><td className="text-xs">{a.actor}</td><td className="text-xs">{a.target ?? ''}</td>
                  <td className="font-mono text-xs text-soft">{a.row_hash.slice(0, 12)}…</td><td className="text-xs text-soft">{a.at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {tab === 'Users' && (
        <section className="card p-5">
          <table className="w-full text-sm">
            <thead className="text-left text-xs text-soft uppercase"><tr><th className="py-2">Name</th><th>Email</th><th>Role</th><th>Organisation</th></tr></thead>
            <tbody>
              {o.users.map((u: any) => (
                <tr key={u.email} className="border-t border-line/70"><td className="py-2">{u.name}</td><td>{u.email}</td><td><span className="chip bg-[#e4ebfb] text-act">{u.role}</span></td><td>{u.org_id ?? 'platform'}</td></tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  )
}
