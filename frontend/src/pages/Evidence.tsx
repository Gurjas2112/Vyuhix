import { useEffect, useState } from 'react'
import { CheckCircle2, Play, ShieldAlert, ShieldX } from 'lucide-react'
import { api } from '../api'
import { useRisk } from '../App'
import { PageHeader, Sev } from '../components/ui'

export default function Evidence() {
  const { reload } = useRisk()
  const [state, setState] = useState<any | null>(null)
  const [scan, setScan] = useState<any | null>(null)
  const [shown, setShown] = useState(0)
  const [busy, setBusy] = useState(false)
  const [target, setTarget] = useState('8.8.8.8')
  const [refusal, setRefusal] = useState<string | null>(null)

  useEffect(() => { api('/evidence').then(d => { setState(d); if (d.last_scan) { setScan(d.last_scan); setShown(d.last_scan.steps.length) } }) }, [])

  async function runScan() {
    setBusy(true); setRefusal(null); setShown(0)
    const r = await api('/scan', { targets: state.allowlist })
    setScan(r)
    for (let i = 1; i <= r.steps.length; i++) { await new Promise(res => setTimeout(res, 260)); setShown(i) }
    setBusy(false); reload()
  }
  async function tryTarget() {
    setRefusal(null)
    try { await api('/scan', { targets: [target] }); setRefusal('Accepted (inside the lab range).') }
    catch (e: any) { setRefusal(e.message) }
  }

  if (!state) return <p className="text-muted">Loading…</p>
  return (
    <div className="max-w-7xl">
      <PageHeader eyebrow="Evidence" title="Scanner evidence in, attack graph out">
        <button className="btn-primary" onClick={runScan} disabled={busy}><Play className="size-4" /> {busy ? 'Scanning…' : 'Run lab scan'}</button>
      </PageHeader>

      <div className="grid grid-cols-[1fr_380px] gap-4">
        <section className="card p-5">
          <h2 className="font-display text-lg font-bold">Pipeline</h2>
          <p className="text-sm text-muted">Level 1 replays recorded outputs of real tools against the demo lab ({state.allowlist.join(', ')}). Parsers are deterministic; free text is checked for injected instructions.</p>
          <ol className="mt-3 grid grid-cols-4 gap-2">
            {(scan?.steps ?? []).map((s: any, i: number) => (
              <li key={s.step} className={`rounded-xl border p-3 text-sm transition-colors ${i < shown ? 'border-ok bg-[#eef7f2]' : 'border-line text-soft'}`}>
                <div className="flex items-center gap-1.5 font-medium">{i < shown && <CheckCircle2 className="size-4 text-ok" />}{s.step}</div>
                <div className="text-xs mt-1">{i < shown ? `${s.records} records · ${s.ms} ms` : 'waiting'}</div>
              </li>
            ))}
            {!scan && <li className="col-span-4 text-sm text-muted">No scan yet. Click "Run lab scan".</li>}
          </ol>
        </section>
        <section className="card p-5">
          <h2 className="font-display text-lg font-bold flex items-center gap-2"><ShieldX className="size-5 text-bad" /> Authorised targets only</h2>
          <p className="text-sm text-muted">The scanner refuses anything outside the lab ranges before a single packet is sent, and the refusal is audited.</p>
          <div className="flex gap-2 mt-3">
            <label htmlFor="target" className="sr-only">Target</label>
            <input id="target" value={target} onChange={e => setTarget(e.target.value)} className="flex-1 rounded-lg border border-line bg-white px-3 py-2 text-sm font-mono" />
            <button className="btn-ghost" onClick={tryTarget}>Try scan</button>
          </div>
          {refusal && <p role="alert" className="text-sm mt-2 text-bad">{refusal}</p>}
        </section>
      </div>

      {scan && shown === scan.steps.length && (
        <>
          {scan.guardrails.length > 0 && (
            <section className="mt-4 rounded-2xl border border-[#f3c99a] bg-[#fdf1e6] p-4 text-sm">
              <div className="font-semibold flex items-center gap-2"><ShieldAlert className="size-4 text-warn" /> {scan.guardrails.length} guardrail event: instruction-like text quarantined</div>
              {scan.guardrails.map((g: any, i: number) => (
                <div key={i} className="mt-1 text-muted"><code className="font-mono">{g.source}</code>: “{g.detail.text}” → stored as data, never passed to an AI as an instruction.</div>
              ))}
            </section>
          )}
          <section className="card mt-4 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-sand text-left text-xs text-soft uppercase tracking-wide">
                <tr><th className="px-4 py-2.5">Severity</th><th className="px-4 py-2.5">Finding</th><th className="px-4 py-2.5">Tool</th><th className="px-4 py-2.5">Asset</th><th className="px-4 py-2.5">Evidence ID</th></tr>
              </thead>
              <tbody>
                {scan.findings.map((f: any) => (
                  <tr key={f.id} className="border-t border-line/70">
                    <td className="px-4 py-2"><Sev s={f.severity} /></td>
                    <td className="px-4 py-2"><div>{f.title}</div><div className="text-xs text-muted truncate max-w-md">{f.detail}</div></td>
                    <td className="px-4 py-2">{f.tool}</td><td className="px-4 py-2 font-mono text-xs">{f.asset_ip ?? '—'}</td>
                    <td className="px-4 py-2 font-mono text-xs text-soft">{f.id}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
          <p className="text-xs text-soft mt-2">SHA-256 recorded for every evidence file · {Object.keys(scan.sha256).length} files</p>
        </>
      )}
    </div>
  )
}
