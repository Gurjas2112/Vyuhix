export function groupIndian(n: number): string {
  const sign = n < 0 ? '-' : ''
  const s = String(Math.abs(Math.round(n)))
  if (s.length <= 3) return sign + s
  let head = s.slice(0, -3)
  const tail = s.slice(-3)
  const parts: string[] = []
  while (head.length > 2) { parts.unshift(head.slice(-2)); head = head.slice(0, -2) }
  if (head) parts.unshift(head)
  return sign + [...parts, tail].join(',')
}
/** Same rules as the backend's money.inr so the UI and the copilot always agree. */
export function inr(x: number): string {
  if (Math.abs(x) >= 1e7) return `₹${(x / 1e7).toFixed(2)} Cr`
  if (Math.abs(x) >= 1e5) return `₹${(x / 1e5).toFixed(1)} L`
  return '₹' + groupIndian(x)
}
export const pct = (x: number) => `${Math.round(x * 100)}%`
