export type User = { email: string; name: string; role: string; org: string | null }

const KEY = 'vyuhix.session'
export function session(): { token: string; user: User } | null {
  try { const raw = sessionStorage.getItem(KEY); return raw ? JSON.parse(raw) : null } catch { return null }
}
export function saveSession(s: { token: string; user: User } | null) {
  try { s ? sessionStorage.setItem(KEY, JSON.stringify(s)) : sessionStorage.removeItem(KEY) } catch { /* storage blocked */ }
}

export class ApiError extends Error { status: number; constructor(status: number, msg: string) { super(msg); this.status = status } }

export async function api<T = any>(path: string, body?: unknown, method?: string): Promise<T> {
  const s = session()
  const res = await fetch(`/api${path}`, {
    method: method ?? (body === undefined ? 'GET' : 'POST'),
    headers: { 'Content-Type': 'application/json', ...(s ? { Authorization: `Bearer ${s.token}` } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const detail = typeof data.detail === 'string' ? data.detail : 'Something went wrong.'
    if (res.status === 401 && path !== '/auth/login') { saveSession(null); location.href = '/login' }
    throw new ApiError(res.status, detail)
  }
  return data as T
}
