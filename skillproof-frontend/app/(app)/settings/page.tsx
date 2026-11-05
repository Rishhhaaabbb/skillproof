'use client'
import { useEffect, useState, useCallback } from 'react'
import {
  User, GitBranch, FileText, Globe, ShieldAlert,
  CheckCircle2, AlertCircle, Loader2, ExternalLink, Trash2,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { clearTokens } from '@/lib/auth'
import api from '@/lib/api'
import { cn } from '@/lib/utils'
import { useRouter } from 'next/navigation'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface UserProfile {
  id: number
  email: string
  full_name?: string
  github_username?: string
  profile_headline?: string
  is_public: boolean
  created_at: string
}

interface AccountInfo {
  email: string
  member_since: string
  total_analyses: number
}

// ---------------------------------------------------------------------------
// Reusable form field
// ---------------------------------------------------------------------------
function Field({
  id, label, hint, children,
}: { id: string; label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-medium">{label}</label>
      {children}
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}

const inputClass = (dirty = false) => cn(
  'h-9 w-full rounded-lg border bg-background px-3 text-sm outline-none transition-colors',
  'placeholder:text-muted-foreground/50',
  'focus:border-ring focus:ring-2 focus:ring-ring/20',
  'disabled:cursor-not-allowed disabled:opacity-50',
  dirty && 'border-primary/60',
)

// ---------------------------------------------------------------------------
// Section wrapper
// ---------------------------------------------------------------------------
function Section({
  title, description, icon: Icon, danger = false, children,
}: {
  title: string
  description?: string
  icon: React.ElementType
  danger?: boolean
  children: React.ReactNode
}) {
  return (
    <div className={cn(
      'rounded-xl border p-6',
      danger ? 'border-destructive/40 bg-destructive/5' : 'border-border/60 bg-card',
    )}>
      <div className="mb-5 flex items-start gap-3">
        <div className={cn(
          'mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg',
          danger ? 'bg-destructive/10' : 'bg-primary/10',
        )}>
          <Icon className={cn('h-4 w-4', danger ? 'text-destructive' : 'text-primary')} />
        </div>
        <div>
          <h2 className={cn('text-sm font-semibold', danger && 'text-destructive')}>{title}</h2>
          {description && (
            <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>
          )}
        </div>
      </div>
      {children}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Toggle switch
// ---------------------------------------------------------------------------
function Toggle({
  checked, onChange, disabled,
}: { checked: boolean; onChange: (v: boolean) => void; disabled?: boolean }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={cn(
        'relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent',
        'transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50',
        'disabled:cursor-not-allowed disabled:opacity-50',
        checked ? 'bg-primary' : 'bg-muted',
      )}
    >
      <span className={cn(
        'pointer-events-none block h-4 w-4 rounded-full bg-white shadow-sm transition-transform',
        checked ? 'translate-x-4' : 'translate-x-0',
      )} />
    </button>
  )
}

// ---------------------------------------------------------------------------
// Public share card — shown when profile is public
// Generates a share token and gives a one-click copy button
// ---------------------------------------------------------------------------
interface ShareTokenData { id: number; token: string; expires_at?: string }

function PublicShareCard() {
  const [tokenData, setTokenData] = useState<ShareTokenData | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    api.get<ShareTokenData>('/api/share/token')
      .then(setTokenData)
      .catch(() => setTokenData(null))
      .finally(() => setLoading(false))
  }, [])

  async function generate() {
    setGenerating(true)
    try {
      const t = await api.post<ShareTokenData>('/api/share/token')
      setTokenData(t)
    } finally {
      setGenerating(false)
    }
  }

  async function copyLink() {
    if (!tokenData) return
    const url = `${window.location.origin}/share/${tokenData.token}`
    await navigator.clipboard.writeText(url)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const shareUrl = tokenData
    ? `${typeof window !== 'undefined' ? window.location.origin : ''}/share/${tokenData.token}`
    : null

  return (
    <div className="mt-3 rounded-lg border border-emerald-500/20 bg-emerald-500/8 p-3">
      <p className="mb-2 text-xs font-medium text-emerald-700 dark:text-emerald-400">
        Your profile is public
      </p>
      {loading ? (
        <Skeleton className="h-8 w-full" />
      ) : tokenData ? (
        <div className="flex items-center gap-2">
          <code className="flex-1 truncate rounded border border-border/60 bg-background px-2 py-1 text-xs font-mono text-foreground">
            {shareUrl}
          </code>
          <Button size="sm" variant="outline" onClick={copyLink} className="shrink-0 gap-1.5 text-xs">
            {copied ? <><CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />Copied!</> : 'Copy link'}
          </Button>
        </div>
      ) : (
        <div className="flex items-center gap-2">
          <p className="flex-1 text-xs text-muted-foreground">
            Generate a link to share your profile with recruiters.
          </p>
          <Button size="sm" variant="outline" onClick={generate} disabled={generating} className="shrink-0 gap-1.5 text-xs">
            {generating ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : null}
            Generate link
          </Button>
        </div>
      )}
      {tokenData?.expires_at && (
        <p className="mt-1.5 text-[10px] text-muted-foreground">
          Expires {new Date(tokenData.expires_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
        </p>
      )}
    </div>
  )
}
function DeleteDialog({
  onConfirm, onCancel, loading,
}: { onConfirm: () => void; onCancel: () => void; loading: boolean }) {
  const [typed, setTyped] = useState('')
  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm" onClick={onCancel} />
      <div className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-xl border border-destructive/40 bg-card p-6 shadow-2xl">
        <h3 className="mb-1 text-lg font-semibold text-destructive">Delete Account</h3>
        <p className="mb-4 text-sm text-muted-foreground">
          This permanently deletes your account, all analyses, roles, tasks, and chat history.
          <strong className="text-foreground"> This cannot be undone.</strong>
        </p>
        <p className="mb-2 text-sm">
          Type <span className="font-mono font-bold">delete my account</span> to confirm:
        </p>
        <input
          type="text"
          value={typed}
          onChange={(e) => setTyped(e.target.value)}
          placeholder="delete my account"
          className={inputClass()}
        />
        <div className="mt-4 flex gap-2">
          <Button variant="outline" onClick={onCancel} disabled={loading} className="flex-1">
            Cancel
          </Button>
          <Button
            variant="destructive"
            disabled={typed !== 'delete my account' || loading}
            onClick={onConfirm}
            className="flex-1 gap-1.5"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
            Delete
          </Button>
        </div>
      </div>
    </>
  )
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export default function SettingsPage() {
  const router = useRouter()

  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [accountInfo, setAccountInfo] = useState<AccountInfo | null>(null)
  const [loading, setLoading] = useState(true)

  // Form state
  const [fullName, setFullName] = useState('')
  const [githubUsername, setGithubUsername] = useState('')
  const [headline, setHeadline] = useState('')
  const [isPublic, setIsPublic] = useState(false)

  // Dirty tracking (anything changed from saved)
  const [dirty, setDirty] = useState(false)

  // Save state
  const [saving, setSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  // Toggle saving (separate from profile form)
  const [togglingPublic, setTogglingPublic] = useState(false)

  // Delete dialog
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [deleting, setDeleting] = useState(false)

  // ------------------------------------------------------------------
  // Load profile + account info
  // ------------------------------------------------------------------
  const loadData = useCallback(async () => {
    try {
      const [p, a] = await Promise.all([
        api.get<UserProfile>('/api/settings'),
        api.get<AccountInfo>('/api/settings/account-info'),
      ])
      setProfile(p)
      setAccountInfo(a)
      setFullName(p.full_name ?? '')
      setGithubUsername(p.github_username ?? '')
      setHeadline(p.profile_headline ?? '')
      setIsPublic(p.is_public)
    } catch {
      // handled by loading state
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  // Track dirtiness against saved profile values
  useEffect(() => {
    if (!profile) return
    const changed =
      fullName !== (profile.full_name ?? '') ||
      githubUsername !== (profile.github_username ?? '') ||
      headline !== (profile.profile_headline ?? '')
    setDirty(changed)
  }, [fullName, githubUsername, headline, profile])

  // ------------------------------------------------------------------
  // Save profile fields
  // ------------------------------------------------------------------
  async function handleSave() {
    if (!dirty || saving) return
    setSaving(true)
    setSaveError(null)
    setSaveSuccess(false)
    try {
      const updated = await api.patch<UserProfile>('/api/settings', {
        full_name: fullName,
        github_username: githubUsername,
        profile_headline: headline,
      })
      setProfile(updated)
      setDirty(false)
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
    } catch (err: any) {
      setSaveError(err?.response?.data?.detail ?? 'Failed to save profile')
    } finally {
      setSaving(false)
    }
  }

  function handleCancel() {
    if (!profile) return
    setFullName(profile.full_name ?? '')
    setGithubUsername(profile.github_username ?? '')
    setHeadline(profile.profile_headline ?? '')
    setDirty(false)
    setSaveError(null)
  }

  // ------------------------------------------------------------------
  // Toggle public profile
  // ------------------------------------------------------------------
  async function handleTogglePublic(val: boolean) {
    setIsPublic(val)
    setTogglingPublic(true)
    try {
      const updated = await api.patch<UserProfile>('/api/settings', { is_public: val })
      setProfile(updated)
    } catch {
      setIsPublic(!val) // revert
    } finally {
      setTogglingPublic(false)
    }
  }

  // ------------------------------------------------------------------
  // Delete account
  // ------------------------------------------------------------------
  async function handleDelete() {
    setDeleting(true)
    try {
      await api.delete('/api/settings/account')
      clearTokens()
      router.replace('/login')
    } catch {
      setDeleting(false)
      setShowDeleteDialog(false)
    }
  }

  const memberSince = accountInfo?.member_since
    ? new Date(accountInfo.member_since).toLocaleDateString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric',
      })
    : '—'

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      <div className="mx-auto w-full max-w-2xl px-4 py-6 sm:px-6">

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage your profile, privacy, and account
          </p>
        </div>

        <div className="flex flex-col gap-5">

          {/* ── Profile Section ── */}
          <Section icon={User} title="Profile" description="Your public-facing developer identity">
            {loading ? (
              <div className="flex flex-col gap-4">
                <Skeleton className="h-9 w-full" />
                <Skeleton className="h-9 w-full" />
                <Skeleton className="h-9 w-full" />
              </div>
            ) : (
              <div className="flex flex-col gap-4">
                {saveError && (
                  <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/8 px-3 py-2 text-sm text-destructive">
                    <AlertCircle className="h-4 w-4 shrink-0" />
                    {saveError}
                  </div>
                )}
                {saveSuccess && (
                  <div className="flex items-center gap-2 rounded-lg border border-emerald-500/30 bg-emerald-500/8 px-3 py-2 text-sm text-emerald-600 dark:text-emerald-400">
                    <CheckCircle2 className="h-4 w-4 shrink-0" />
                    Profile saved successfully
                  </div>
                )}

                <Field id="full_name" label="Full name" hint="Displayed on your public profile and dashboard greeting.">
                  <input
                    id="full_name"
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Your full name"
                    className={inputClass(fullName !== (profile?.full_name ?? ''))}
                  />
                </Field>

                <Field
                  id="github_username"
                  label="GitHub username"
                  hint="Used to fetch your public activity for analysis. Changing this will affect your next analysis run."
                >
                  <div className="relative">
                    <div className="pointer-events-none absolute inset-y-0 left-3 flex items-center">
                      <GitBranch className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <input
                      id="github_username"
                      type="text"
                      value={githubUsername}
                      onChange={(e) => setGithubUsername(e.target.value)}
                      placeholder="your-github-handle"
                      className={cn(inputClass(githubUsername !== (profile?.github_username ?? '')), 'pl-9 pr-24')}
                    />
                    {githubUsername && (
                      <a
                        href={`https://github.com/${githubUsername}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="absolute inset-y-0 right-2 flex items-center gap-1 rounded px-2 text-xs text-muted-foreground hover:text-foreground"
                      >
                        View <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                </Field>

                <Field
                  id="headline"
                  label="Profile headline"
                  hint={'A short bio shown on your public profile, e.g. "Full-stack developer · Open to work".'}
                >
                  <div className="relative">
                    <div className="pointer-events-none absolute inset-y-0 left-3 flex items-center">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <input
                      id="headline"
                      type="text"
                      value={headline}
                      onChange={(e) => setHeadline(e.target.value)}
                      placeholder="e.g. Full-stack developer · Open to work"
                      maxLength={120}
                      className={cn(inputClass(headline !== (profile?.profile_headline ?? '')), 'pl-9')}
                    />
                  </div>
                  {headline.length > 80 && (
                    <p className="text-right text-xs text-muted-foreground">{headline.length}/120</p>
                  )}
                </Field>

                {/* Save / Cancel */}
                {dirty && (
                  <div className="flex items-center gap-2 pt-1">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCancel}
                      disabled={saving}
                    >
                      Cancel
                    </Button>
                    <Button
                      size="sm"
                      onClick={handleSave}
                      disabled={saving}
                      className="gap-1.5"
                    >
                      {saving
                        ? <><Loader2 className="h-3.5 w-3.5 animate-spin" />Saving…</>
                        : 'Save changes'
                      }
                    </Button>
                  </div>
                )}
              </div>
            )}
          </Section>

          {/* ── Privacy Section ── */}
          <Section
            icon={Globe}
            title="Privacy"
            description="Control who can see your developer profile"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium">Public profile</p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  When on, anyone with your share link can view your TPR score, skill tags,
                  matched requirements, and profile headline. Your email is never shown.
                </p>
              </div>
              {loading ? (
                <Skeleton className="h-5 w-9 rounded-full" />
              ) : (
                <Toggle
                  checked={isPublic}
                  onChange={handleTogglePublic}
                  disabled={togglingPublic}
                />
              )}
            </div>
            {isPublic && (
              <>
                <PublicShareCard />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push('/settings/share')}
                  className="mt-3 gap-1.5 text-xs"
                >
                  Manage share link & recruiter requests →
                </Button>
              </>
            )}
          </Section>

          {/* ── Account Info Section ── */}
          <Section
            icon={User}
            title="Account information"
            description="Read-only details about your account"
          >
            <div className="flex flex-col divide-y divide-border/50">
              {[
                {
                  label: 'Email address',
                  value: accountInfo?.email ?? profile?.email,
                  loading,
                },
                {
                  label: 'Member since',
                  value: memberSince,
                  loading,
                },
                {
                  label: 'Total analyses run',
                  value: accountInfo?.total_analyses != null
                    ? String(accountInfo.total_analyses)
                    : undefined,
                  loading,
                },
              ].map(({ label, value, loading: l }) => (
                <div key={label} className="flex items-center justify-between py-3">
                  <p className="text-sm text-muted-foreground">{label}</p>
                  {l ? (
                    <Skeleton className="h-4 w-32" />
                  ) : (
                    <p className="text-sm font-medium">{value ?? '—'}</p>
                  )}
                </div>
              ))}
            </div>
          </Section>

          {/* ── Danger Zone ── */}
          <Section
            icon={ShieldAlert}
            title="Danger zone"
            description="Irreversible account actions"
            danger
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-destructive">Delete account</p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  Permanently deletes your account, all analyses, target roles, tasks, chat history,
                  and notifications. This action cannot be reversed.
                </p>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setShowDeleteDialog(true)}
                className="shrink-0 gap-1.5"
              >
                <Trash2 className="h-3.5 w-3.5" />
                Delete account
              </Button>
            </div>
          </Section>

        </div>
      </div>

      {/* Delete confirmation dialog */}
      {showDeleteDialog && (
        <DeleteDialog
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteDialog(false)}
          loading={deleting}
        />
      )}
    </div>
  )
}
