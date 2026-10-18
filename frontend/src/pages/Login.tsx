import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lock } from 'lucide-react'
import { api, saveSession } from '../api'

const DEMO = [
  { email: 'ananya@acme.demo', who: 'Ananya · CISO', role: 'Org admin' },
  { email: 'rohit@acme.demo', who: 'Rohit · CFO', role: 'Viewer (board)' },
  { email: 'karan@broker.demo', who: 'Karan · Broker', role: 'Broker' },
  { email: 'divya@platform.demo', who: 'Divya · Platform ops', role: 'Platform admin' },
]

export default function Login() {
  const nav = useNavigate()
  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e?: React.FormEvent, override?: { email: string; password: string }) {
    e?.preventDefault(); setErr(''); setBusy(true)
    try {
      const body = override ?? (mode === 'login' ? { email, password } : { email, password, name })
      const s = await api(mode === 'login' || override ? '/auth/login' : '/auth/signup', body)
      saveSession(s)
      nav(s.user.role === 'platform_admin' ? '/admin' : '/')
    } catch (e: any) { setErr(e.message) } finally { setBusy(false) }
  }

  return (
    <div className="min-h-full grid lg:grid-cols-[1.1fr_1fr]">
      <section className="bg-ink text-sand p-12 flex flex-col justify-between">
        <div className="flex items-center gap-3">
          <img src="/favicon.svg" alt="" className="size-10" />
          <span className="font-display text-2xl font-bold">Vyuhix</span>
        </div>
        <div>
          <div className="eyebrow !text-money-lt">Cyber risk in rupees</div>
          <h1 className="font-display text-5xl font-bold leading-[1.05] mt-3 max-w-xl">From attack paths to a number your board and your insurer can act on.</h1>
          <p className="text-[#c3ccd8] mt-5 max-w-lg leading-relaxed">
            Real scanner evidence becomes attack paths, a simulated annual loss, the best fixes for a fixed budget
            and an insurance view, with every rupee traceable back to its evidence.
          </p>
        </div>
        <p className="text-xs text-[#8c97a8]">Proof of concept · demo organisation "Acme Fintech" is fictional · all data synthetic</p>
      </section>

      <section className="p-10 flex items-center justify-center">
        <div className="w-full max-w-sm">
          <div className="flex gap-1 p-1 bg-line/50 rounded-lg mb-6" role="tablist">
            {(['login', 'signup'] as const).map(m => (
              <button key={m} role="tab" aria-selected={mode === m} onClick={() => setMode(m)}
                className={`flex-1 rounded-md py-1.5 text-sm font-medium ${mode === m ? 'bg-paper shadow-sm' : 'text-muted'}`}>
                {m === 'login' ? 'Sign in' : 'Create account'}
              </button>
            ))}
          </div>
          <form onSubmit={submit} className="space-y-3">
            {mode === 'signup' && <Field label="Full name" value={name} onChange={setName} autoComplete="name" />}
            <Field label="Work email" type="email" value={email} onChange={setEmail} autoComplete="email" />
            <Field label="Password" type="password" value={password} onChange={setPassword} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} />
            {mode === 'signup' && <p className="text-xs text-soft">10+ characters with upper, lower, digit and symbol. New accounts join the demo organisation as analysts.</p>}
            {err && <p role="alert" className="text-sm text-bad">{err}</p>}
            <button className="btn-primary w-full justify-center" disabled={busy}><Lock className="size-4" /> {mode === 'login' ? 'Sign in' : 'Create account'}</button>
          </form>

          <div className="mt-8">
            <div className="text-xs font-semibold text-soft uppercase tracking-wide mb-2">Demo accounts · password Demo@12345</div>
            <div className="grid grid-cols-2 gap-2">
              {DEMO.map(d => (
                <button key={d.email} onClick={() => submit(undefined, { email: d.email, password: 'Demo@12345' })}
                  className="card p-3 text-left hover:border-act transition-colors" disabled={busy}>
                  <div className="text-sm font-medium">{d.who}</div>
                  <div className="text-[11px] text-soft">{d.role}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

function Field({ label, value, onChange, type = 'text', autoComplete }: { label: string; value: string; onChange: (v: string) => void; type?: string; autoComplete?: string }) {
  const id = label.toLowerCase().replace(/\s/g, '-')
  return (
    <div>
      <label htmlFor={id} className="text-sm font-medium">{label}</label>
      <input id={id} type={type} value={value} onChange={e => onChange(e.target.value)} autoComplete={autoComplete} required
        className="mt-1 w-full rounded-lg border border-line bg-white px-3 py-2 text-sm" />
    </div>
  )
}
