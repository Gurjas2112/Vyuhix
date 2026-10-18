import { useEffect, useState } from 'react'
import { api } from '../api'
import { PageHeader, StatusPill } from '../components/ui'

export default function Compliance() {
  const [m, setM] = useState<any | null>(null)
  useEffect(() => { api('/compliance').then(setM) }, [])
  if (!m) return <p className="text-muted">Loading…</p>
  return (
    <div className="max-w-[1400px]">
      <PageHeader eyebrow="Compliance" title="One evidence base, every framework" />
      <section className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-ink text-sand text-left">
            <tr>
              <th className="px-4 py-3 font-medium">Control area</th><th className="px-4 py-3 font-medium">Status</th>
              {m.frameworks.map((f: string) => <th key={f} className="px-4 py-3 font-medium whitespace-nowrap">{f}</th>)}
            </tr>
          </thead>
          <tbody>
            {m.rows.map((r: any, i: number) => (
              <tr key={r.area} className={i % 2 ? 'bg-sand/60' : ''}>
                <td className="px-4 py-3 align-top"><div className="font-medium">{r.area}</div><div className="text-xs text-muted mt-0.5 max-w-xs">{r.note}</div></td>
                <td className="px-4 py-3 align-top"><StatusPill status={r.status} /></td>
                {m.frameworks.map((f: string) => <td key={f} className="px-4 py-3 align-top text-xs">{r.map[f]}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <p className="text-xs text-soft mt-3">{m.note}</p>
    </div>
  )
}
