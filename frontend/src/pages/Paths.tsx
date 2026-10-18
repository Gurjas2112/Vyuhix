import { useEffect, useMemo, useState } from 'react'
import { Background, Controls, MarkerType, Position, ReactFlow, type Edge, type Node } from '@xyflow/react'
import { api } from '../api'
import { useRisk } from '../App'
import { PageHeader, inr, pct } from '../components/ui'

const TYPE_STYLE: Record<string, { bg: string; fg: string; tag: string }> = {
  entry: { bg: '#0e1726', fg: '#f4f2ec', tag: 'Entry' },
  asset: { bg: '#fbfbf8', fg: '#0e1726', tag: 'Asset' },
  secret: { bg: '#fdf3d8', fg: '#5c3b00', tag: 'Secret' },
  identity: { bg: '#e4ebfb', fg: '#1b3a85', tag: 'Identity' },
  crown_jewel: { bg: '#b85c12', fg: '#fff8f0', tag: 'Crown jewel' },
}

function layout(nodes: any[], edges: any[]) {
  const depth: Record<string, number> = {}
  const queue = nodes.filter(n => n.type === 'entry').map(n => { depth[n.id] = 0; return n.id })
  while (queue.length) {
    const id = queue.shift()!
    for (const e of edges.filter(e => e.src === id)) {
      if (depth[e.dst] === undefined || depth[e.dst] < depth[id] + 1) {
        if ((depth[e.dst] ?? -1) < 6) { depth[e.dst] = depth[id] + 1; queue.push(e.dst) }
      }
    }
  }
  for (const n of nodes) if (n.type === 'crown_jewel') depth[n.id] = Math.max(...Object.values(depth))
  const cols: Record<number, string[]> = {}
  for (const n of nodes) (cols[depth[n.id] ?? 0] ??= []).push(n.id)
  const pos: Record<string, { x: number; y: number }> = {}
  for (const [d, ids] of Object.entries(cols)) ids.forEach((id, i) => { pos[id] = { x: Number(d) * 280, y: i * 130 + (3 - ids.length) * 65 } })
  return pos
}

export default function Paths() {
  const { run: baseRun, org } = useRisk()
  const [graph, setGraph] = useState<any | null>(null)
  const [controls, setControls] = useState<string[]>([])
  const [run, setRun] = useState<any | null>(null)
  const [sel, setSel] = useState<string | null>(null)

  useEffect(() => { api('/graph').then(setGraph) }, [])
  useEffect(() => { api('/run', { controls }).then(setRun) }, [controls])
  const r = run ?? baseRun

  const ranked = useMemo(() => (r?.paths ?? []).slice().sort((a: any, b: any) => b.eal - a.eal), [r])
  const selPath = ranked.find((p: any) => p.id === (sel ?? ranked[0]?.id))
  const selEdges = new Set<string>(selPath?.edges ?? [])

  const { nodes, edges } = useMemo(() => {
    if (!graph || !r) return { nodes: [] as Node[], edges: [] as Edge[] }
    const pos = layout(graph.nodes, graph.edges)
    const ns: Node[] = graph.nodes.map((n: any) => {
      const st = TYPE_STYLE[n.type]
      return {
        id: n.id, position: pos[n.id], draggable: true, sourcePosition: Position.Right, targetPosition: Position.Left,
        data: { label: <div><div style={{ fontSize: 10, opacity: 0.75, textTransform: 'uppercase', letterSpacing: 1 }}>{st.tag}</div><div style={{ fontWeight: 600 }}>{n.label}</div></div> },
        style: { background: st.bg, color: st.fg, border: '1px solid #dad6cc', borderRadius: 12, width: 200, fontSize: 13, padding: 10, textAlign: 'left' },
      }
    })
    const es: Edge[] = graph.edges.map((e: any) => {
      const p = r.edge_p[e.id]
      const on = selEdges.has(e.id)
      const dead = p <= 1e-9
      return {
        id: e.id, source: e.src, target: e.dst, label: dead ? 'cut' : pct(p), type: 'smoothstep',
        animated: on && !dead,
        style: { stroke: dead ? '#b8b3a7' : on ? '#b85c12' : '#8c97a8', strokeWidth: on ? 3 : 1.5, strokeDasharray: dead ? '6 4' : undefined },
        labelStyle: { fontSize: 11, fill: on ? '#b85c12' : '#4a5568', fontWeight: 600 },
        labelBgStyle: { fill: '#fbfbf8' },
        markerEnd: { type: MarkerType.ArrowClosed, color: on ? '#b85c12' : '#8c97a8' },
      }
    })
    return { nodes: ns, edges: es }
  }, [graph, r, sel, controls])

  if (!r || !org) return <p className="text-muted">Loading…</p>
  const toggle = (id: string) => setControls(c => c.includes(id) ? c.filter(x => x !== id) : [...c, id])

  return (
    <div className="max-w-[1400px]">
      <PageHeader eyebrow="Attack paths" title="Every route in, priced">
        <span className="text-xs text-soft">Edge labels: chance a single attempt succeeds at that step</span>
      </PageHeader>
      <div className="grid grid-cols-[1fr_380px] gap-4">
        <section className="card overflow-hidden" style={{ height: 560 }} aria-label="Attack path map">
          <ReactFlow nodes={nodes} edges={edges} fitView fitViewOptions={{ padding: 0.04 }} proOptions={{ hideAttribution: true }} minZoom={0.4}>
            <Background color="#e7e3d9" gap={20} />
            <Controls showInteractive={false} />
          </ReactFlow>
        </section>

        <div className="space-y-4">
          <section className="card p-4">
            <h2 className="font-display font-bold mb-2">Paths</h2>
            <ul className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
              {ranked.map((p: any) => {
                const live = p.probability_per_attempt > 1e-9
                return (
                  <li key={p.id}>
                    <button onClick={() => setSel(p.id)} aria-pressed={selPath?.id === p.id}
                      className={`w-full text-left rounded-lg px-3 py-2 text-sm border ${selPath?.id === p.id ? 'border-money bg-[#fdf1e6]' : 'border-transparent hover:bg-sand'}`}>
                      <div className="flex gap-2">
                        <span className="num font-semibold w-7">{p.id}</span>
                        <span className={`flex-1 ${live ? '' : 'line-through text-soft'}`}>{p.nodes.length - 1} hop{p.nodes.length === 2 ? "" : "s"} to {p.jewel.replace('_', ' ')}</span>
                        <span className="num font-semibold text-money">{inr(p.eal)}</span>
                      </div>
                    </button>
                  </li>
                )
              })}
            </ul>
            {selPath && <p className="text-xs text-muted mt-3 leading-relaxed">{selPath.text}</p>}
          </section>

          <section className="card p-4">
            <h2 className="font-display font-bold">What if we fix…</h2>
            <p className="text-xs text-soft mb-2">Toggle controls; the map and numbers re-simulate with the same random draws.</p>
            <div className="space-y-1 max-h-48 overflow-y-auto pr-1">
              {org.controls.map((c: any) => (
                <label key={c.id} className="flex items-center gap-2 text-sm py-1 cursor-pointer">
                  <input type="checkbox" checked={controls.includes(c.id)} onChange={() => toggle(c.id)} className="accent-[#2f5fd0]" />
                  <span className="flex-1">{c.label}</span><span className="num text-xs text-soft">{inr(c.cost_inr)}</span>
                </label>
              ))}
            </div>
            <div className="mt-3 rounded-xl bg-sand p-3 text-sm">
              <div className="flex justify-between"><span>EAL</span><span className="num font-semibold">{inr(r.baseline_summary.eal)} → <span className="text-money">{inr(r.summary.eal)}</span></span></div>
              <div className="text-xs text-muted mt-1">Removed: {r.diff.removed.join(', ') || 'none'} · New: {r.diff.new.join(', ') || 'none'}</div>
            </div>
          </section>
        </div>
      </div>

      <section className="card p-5 mt-4">
        <h2 className="font-display text-lg font-bold">Choke points: fix these edges first</h2>
        <div className="grid grid-cols-5 gap-3 mt-3">
          {r.choke_points.map((c: any) => (
            <div key={c.edge} className="rounded-xl border border-line p-3">
              <div className="num text-money font-bold">{inr(c.eal_through)}</div>
              <div className="text-xs text-muted">of yearly loss flows through</div>
              <div className="text-sm mt-1.5">{c.text}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
