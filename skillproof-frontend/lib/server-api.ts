// Server-side fetch helper for Server Components (public endpoints only)
// Does NOT attach auth tokens — sessionStorage not available server-side

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export async function serverGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    cache: 'no-store',
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw Object.assign(new Error('Request failed'), {
      response: { status: res.status, data: err },
    })
  }
  return res.json() as Promise<T>
}
