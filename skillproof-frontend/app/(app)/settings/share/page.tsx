'use client'
import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import {
  ArrowLeft, Copy, CheckCircle2, RefreshCw, Trash2,
  Loader2, AlertCircle, UserCheck, Building2, Mail,
  MessageSquare, Clock, Link2,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import api from '@/lib/api'
import { cn } from '@/lib/utils'

interface ShareTokenData {
  id: number
  token: string
  created_at: string
  expires_at?: string
}

interface RecruiterRequest {
  id: number
  recruiter_name: string
  recruiter_email: string
  recruiter_company?: string
  message?: string
  status: string
  created_at: string
}

function relativeTime(iso: string) {
  const diff = Date.now() - new Date(iso).getTime()
  const days = Math.floor(diff / 86_400_000)
  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days} days ago`
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export default function ShareManagementPage() {
  const router = useRouter()
  const [token, setToken] = useState<ShareTokenData | null>(null)
  const [requests, setRequests] = useState<RecruiterRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [revoking, setRevoking] = useState(false)
  const [copied, setCopied] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const shareUrl = token
    ? `${typeof window !== 'undefined' ? window.location.origin : ''}/share/${token.token}`
    : null

  const load = useCallback(async () => {
    setError(null)
    try {
      const [tok, reqs] = await Promise.allSettled([
        api.get<ShareTokenData>('/api/share/token'),
        api.get<RecruiterRequest[]>('/api/share/requests'),
      ])
      if (tok.status === 'fulfilled') setToken(tok.value)
      else setToken(null)
      if (reqs.status === 'fulfilled') setRequests(reqs.value)
    } catch {
      setError('Failed to load share data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function generate() {
    setGenerating(true)
    setError(null)
    try {
      const t = await api.post<ShareTokenData>('/api/share/token')
      setToken(t)
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? 'Failed to generate link')
    } finally {
      setGenerating(false)
    }
  }

  async function revoke() {
    setRevoking(true)
    try {
      await api.delete('/api/share/token')
      setToken(null)
    } finally {
      setRevoking(false)
    }
  }

  async function copyLink() {
    if (!shareUrl) return
    await navigator.clipboard.writeText(shareUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <div className="mx-auto w-full max-w-2xl px-4 py-6 sm:px-6">

        {/* Header */}
        <div className="mb-6 flex items-center gap-3">
          <Button variant="ghost" size="icon-sm" onClick={() => router.push('/settings')}
            className="text-muted-foreground">
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Share Profile</h1>
            <p className="text-sm text-muted-foreground">
              Manage your recruiter share link and incoming requests
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-4 flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/8 px-4 py-3 text-sm text-destructive">
            <AlertCircle className="h-4 w-4 shrink-0" />{error}
          </div>
        )}

        <div className="flex flex-col gap-5">

          {/* ── Share link card ── */}
          <div className="rounded-xl border border-border/60 bg-card p-6">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                <Link2 className="h-4 w-4 text-primary" />
              </div>
              <div>
                <p className="text-sm font-semibold">Recruiter Share Link</p>
                <p className="text-xs text-muted-foreground">
                  Anyone with this link can view your public profile. No login required.
                </p>
              </div>
            </div>

            {loading ? (
              <Skeleton className="h-10 w-full rounded-lg" />
            ) : token ? (
              <div className="flex flex-col gap-3">
                {/* URL bar */}
                <div className="flex items-center gap-2">
                  <code className="flex-1 truncate rounded-lg border border-border/60 bg-muted/30 px-3 py-2 text-xs font-mono text-foreground">
                    {shareUrl}
                  </code>
                  <Button size="sm" onClick={copyLink} className="shrink-0 gap-1.5">
                    {copied
                      ? <><CheckCircle2 className="h-3.5 w-3.5" />Copied!</>
                      : <><Copy className="h-3.5 w-3.5" />Copy</>}
                  </Button>
                </div>

                {/* Meta row */}
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <div className="flex items-center gap-1.5">
                    <Clock className="h-3.5 w-3.5" />
                    {token.expires_at
                      ? `Expires ${new Date(token.expires_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
                      : 'No expiry set'}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline" size="sm"
                      onClick={generate} disabled={generating}
                      className="gap-1.5 text-xs"
                    >
                      {generating
                        ? <Loader2 className="h-3 w-3 animate-spin" />
                        : <RefreshCw className="h-3 w-3" />}
                      Regenerate
                    </Button>
                    <Button
                      variant="destructive" size="sm"
                      onClick={revoke} disabled={revoking}
                      className="gap-1.5 text-xs"
                    >
                      {revoking
                        ? <Loader2 className="h-3 w-3 animate-spin" />
                        : <Trash2 className="h-3 w-3" />}
                      Revoke
                    </Button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3 py-4 text-center">
                <p className="text-sm text-muted-foreground">
                  No share link yet. Generate one to share your profile with recruiters.
                </p>
                <Button onClick={generate} disabled={generating} className="gap-1.5">
                  {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Link2 className="h-4 w-4" />}
                  Generate share link
                </Button>
              </div>
            )}
          </div>

          {/* ── Recruiter requests ── */}
          <div className="rounded-xl border border-border/60 bg-card p-6">
            <div className="mb-4 flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                <UserCheck className="h-4 w-4 text-primary" />
              </div>
              <div>
                <p className="text-sm font-semibold">Recruiter Requests</p>
                <p className="text-xs text-muted-foreground">
                  People who viewed your profile and reached out
                </p>
              </div>
              {requests.length > 0 && (
                <Badge variant="secondary" className="ml-auto">{requests.length}</Badge>
              )}
            </div>

            {loading ? (
              <div className="flex flex-col gap-3">
                {[1, 2].map(i => (
                  <div key={i} className="flex gap-3 rounded-lg border border-border/40 p-3">
                    <Skeleton className="h-8 w-8 rounded-full" />
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-4 w-40" />
                      <Skeleton className="h-3 w-24" />
                    </div>
                  </div>
                ))}
              </div>
            ) : requests.length === 0 ? (
              <div className="flex flex-col items-center gap-2 py-8 text-center">
                <UserCheck className="h-8 w-8 text-muted-foreground/30" />
                <p className="text-sm text-muted-foreground">No recruiter requests yet</p>
                <p className="text-xs text-muted-foreground/70">
                  Share your link with recruiters to receive connection requests here.
                </p>
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                {requests.map(req => (
                  <div key={req.id}
                    className="rounded-lg border border-border/50 bg-muted/20 p-4 transition-colors hover:bg-muted/40">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary">
                          {req.recruiter_name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="text-sm font-medium">{req.recruiter_name}</p>
                          {req.recruiter_company && (
                            <div className="flex items-center gap-1 text-xs text-muted-foreground">
                              <Building2 className="h-3 w-3" />
                              {req.recruiter_company}
                            </div>
                          )}
                        </div>
                      </div>
                      <p className="shrink-0 text-xs text-muted-foreground">
                        {relativeTime(req.created_at)}
                      </p>
                    </div>

                    <div className="mt-2 flex flex-col gap-1.5 pl-12">
                      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                        <Mail className="h-3 w-3" />
                        <a href={`mailto:${req.recruiter_email}`}
                          className="hover:text-foreground hover:underline">
                          {req.recruiter_email}
                        </a>
                      </div>
                      {req.message && (
                        <div className="flex items-start gap-1.5 text-xs text-muted-foreground">
                          <MessageSquare className="mt-0.5 h-3 w-3 shrink-0" />
                          <p className="italic">"{req.message}"</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}
