import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import { BrowserRouter, Navigate, NavLink, Outlet, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import {
  Activity, BadgeIndianRupee, FileText, Gauge, LayoutDashboard, LogOut, MessageSquareText, Route as RouteIcon,
  ScanSearch, ShieldCheck, Shield, Umbrella, Wallet,
} from 'lucide-react'
import { api, saveSession, session, type User } from './api'
import { inr, pct } from './format'
import Login from './pages/Login'
import Overview from './pages/Overview'
import Paths from './pages/Paths'
import Loss from './pages/Loss'
import Plan from './pages/Plan'
import Insurance from './pages/Insurance'
import Compliance from './pages/Compliance'
import Evidence from './pages/Evidence'
import Admin from './pages/Admin'
import Report from './pages/Report'
import Copilot from './components/Copilot'
import TraceDrawer, { type TraceTarget } from './components/TraceDrawer'

type Ctx = {
  user: User
  run: any | null
  org: any | null
  alerts: any[]
  reload: () => Promise<void>
  trace: (t: TraceTarget) => void
  logout: () => void
}
const RiskCtx = createContext<Ctx | null>(null)
export const useRisk = () => useContext(RiskCtx)!

const NAV = [
  { to: '/', label: 'Overview', icon: LayoutDashboard, roles: ['org_admin', 'analyst', 'viewer', 'broker'] },
  { to: '/paths', label: 'Attack paths', icon: RouteIcon, roles: ['org_admin', 'analyst', 'viewer'] },
  { to: '/loss', label: 'Loss', icon: BadgeIndianRupee, roles: ['org_admin', 'analyst', 'viewer'] },
  { to: '/plan', label: 'Plan', icon: Wallet, roles: ['org_admin', 'analyst', 'viewer'] },
  { to: '/insurance', label: 'Insurance', icon: Umbrella, roles: ['org_admin', 'analyst', 'viewer', 'broker'] },
  { to: '/compliance', label: 'Compliance', icon: ShieldCheck, roles: ['org_admin', 'analyst', 'viewer'] },
  { to: '/evidence', label: 'Evidence', icon: ScanSearch, roles: ['org_admin', 'analyst'] },
  { to: '/report', label: 'Board report', icon: FileText, roles: ['org_admin', 'analyst', 'viewer'] },
  { to: '/admin', label: 'Admin console', icon: Gauge, roles: ['platform_admin'] },
]
const ROLE_LABEL: Record<string, string> = {
  org_admin: 'Org admin', analyst: 'Analyst', viewer: 'Viewer (board)', broker: 'Broker', platform_admin: 'Platform admin',
}

function Shell() {
  const s = session()
  const nav = useNavigate()
  const [run, setRun] = useState<any | null>(null)
  const [org, setOrg] = useState<any | null>(null)
  const [alerts, setAlerts] = useState<any[]>([])
  const [copilotOpen, setCopilotOpen] = useState(false)
  const [traceTarget, setTraceTarget] = useState<TraceTarget | null>(null)
  const user = s?.user
  const mainRef = useRef<HTMLElement>(null)
  const location = useLocation()
  useEffect(() => { mainRef.current?.scrollTo({ top: 0 }) }, [location.pathname])

  const reload = useCallback(async () => {
    if (!user) return
    const [o, a] = await Promise.all([api('/org'), api('/alerts')])
    setOrg(o); setAlerts(a)
    if (user.role !== 'platform_admin') setRun(await api('/run', {}))
  }, [user?.email])

  useEffect(() => { reload() }, [reload])
  if (!s || !user) return <Navigate to="/login" replace />

  const logout = () => { saveSession(null); nav('/login') }
  const items = NAV.filter(n => n.roles.includes(user.role))
  const sm = run?.summary
  const kevFresh = org?.feeds?.kev
  const latestAlert = alerts[0]

  return (
    <RiskCtx.Provider value={{ user, run, org, alerts, reload, trace: setTraceTarget, logout }}>
      <div className="flex h-full">
        <aside className="w-60 shrink-0 bg-ink text-sand flex flex-col">
          <div className="px-5 pt-6 pb-5 flex items-center gap-2.5">
            <img src="/favicon.svg" alt="" className="size-8" />
            <div>
              <div className="font-display text-lg font-bold tracking-tight leading-none">Vyuhix</div>
              <div className="text-[11px] text-[#8c97a8] mt-1">Cyber risk in rupees</div>
            </div>
          </div>
          <div className="mx-4 mb-4 rounded-lg bg-ink-2 px-3 py-2.5 text-xs">
            <div className="text-[#8c97a8]">Organisation</div>
            <div className="font-medium mt-0.5">{user.role === 'platform_admin' ? 'Platform (all tenants)' : org?.org?.name ?? '…'}</div>
            {user.role !== 'platform_admin' && <div className="text-[#8c97a8] mt-0.5">{org?.org?.label}</div>}
          </div>
          <nav className="flex-1 px-3 space-y-0.5" aria-label="Main">
            {items.map(({ to, label, icon: Icon }) => (
              <NavLink key={to} to={to} end={to === '/'}
                className={({ isActive }) => `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${isActive ? 'bg-ink-3 text-white' : 'text-[#c3ccd8] hover:bg-ink-2'}`}>
                <Icon className="size-4" aria-hidden /> {label}
              </NavLink>
            ))}
          </nav>
          <div className="p-4 border-t border-ink-3 text-xs">
            <div className="font-medium text-sm">{user.name}</div>
            <div className="text-[#8c97a8]">{ROLE_LABEL[user.role]} · {user.email}</div>
            <button onClick={logout} className="mt-3 flex items-center gap-2 text-[#c3ccd8] hover:text-white">
              <LogOut className="size-3.5" /> Sign out
            </button>
          </div>
        </aside>

        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-14 shrink-0 bg-paper border-b border-line flex items-center gap-6 px-6" aria-label="Risk ticker">
            {sm ? (
              <>
                <Tick label="Expected annual loss" value={inr(sm.eal)} onClick={run.paths ? () => setTraceTarget({ kind: 'eal' }) : undefined} />
                <Tick label="1-in-20-year loss (VaR95)" value={inr(sm.var95)} onClick={run.paths ? () => setTraceTarget({ kind: 'var95' }) : undefined} />
                <Tick label="Chance of any loss this year" value={pct(sm.p_any_loss)} />
                {run.paths && <Tick label="Live attack paths" value={String(run.paths.filter((p: any) => p.probability_per_attempt > 0).length)} />}
              </>
            ) : user.role === 'platform_admin' ? (
              <div className="flex items-center gap-2 text-sm text-muted"><Shield className="size-4" /> Platform operations</div>
            ) : <div className="text-sm text-muted">Loading risk…</div>}
            <div className="flex-1" />
            {kevFresh && (
              <span className={`chip ${kevFresh.simulated ? 'bg-[#fdecd8] text-warn' : 'bg-[#e3f1ea] text-ok'}`}>
                <Activity className="size-3" /> KEV {kevFresh.version}{kevFresh.simulated ? ' · simulated update' : ''}
              </span>
            )}
            {user.role !== 'platform_admin' && (
              <button className="btn-primary" onClick={() => setCopilotOpen(o => !o)} aria-expanded={copilotOpen}>
                <MessageSquareText className="size-4" /> Copilot
              </button>
            )}
          </header>
          {latestAlert && user.role !== 'broker' && (
            <div role="status" className="bg-[#fdecd8] text-[#7a3f00] text-sm px-6 py-2 border-b border-[#f3c99a] flex gap-2">
              <span className="font-semibold">Drift alert:</span> {latestAlert.message}
            </div>
          )}
          <div className="flex-1 flex min-h-0">
            <main ref={mainRef} className="flex-1 overflow-y-auto p-6 min-w-0"><Outlet /></main>
            {copilotOpen && <Copilot onClose={() => setCopilotOpen(false)} />}
          </div>
        </div>
      </div>
      {traceTarget && <TraceDrawer target={traceTarget} onClose={() => setTraceTarget(null)} />}
    </RiskCtx.Provider>
  )
}

function Tick({ label, value, onClick }: { label: string; value: string; onClick?: () => void }) {
  const inner = (
    <div className="text-left">
      <div className="text-[11px] text-soft leading-none">{label}</div>
      <div className={`num text-lg font-semibold leading-tight mt-1 ${onClick ? 'text-money underline decoration-dotted underline-offset-4' : ''}`}>{value}</div>
    </div>
  )
  return onClick ? <button onClick={onClick} title="Trace this figure">{inner}</button> : inner
}

function Home() {
  const s = session()
  if (s?.user.role === 'platform_admin') return <Navigate to="/admin" replace />
  return <Overview />
}

function Guard({ roles, children }: { roles: string[]; children: ReactNode }) {
  const s = session()
  return s && roles.includes(s.user.role) ? <>{children}</> : <Navigate to="/" replace />
}

export default function App() {
  const r = (to: string) => NAV.find(n => n.to === to)!.roles
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<Shell />}>
          <Route index element={<Home />} />
          <Route path="paths" element={<Guard roles={r('/paths')}><Paths /></Guard>} />
          <Route path="loss" element={<Guard roles={r('/loss')}><Loss /></Guard>} />
          <Route path="plan" element={<Guard roles={r('/plan')}><Plan /></Guard>} />
          <Route path="insurance" element={<Guard roles={r('/insurance')}><Insurance /></Guard>} />
          <Route path="compliance" element={<Guard roles={r('/compliance')}><Compliance /></Guard>} />
          <Route path="evidence" element={<Guard roles={r('/evidence')}><Evidence /></Guard>} />
          <Route path="report" element={<Guard roles={r('/report')}><Report /></Guard>} />
          <Route path="admin" element={<Guard roles={r('/admin')}><Admin /></Guard>} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
