'use client'
import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  LayoutDashboard, Target, MessageSquare, Bell, Settings,
  LogOut, ShieldCheck, ExternalLink, ChevronDown,
  Share2, Command,
} from 'lucide-react'
import { clearTokens } from '@/lib/auth'
import { cn } from '@/lib/utils'
import api from '@/lib/api'
import type { User } from '@/lib/types'

// ---------------------------------------------------------------------------
// Navigation items with keyboard shortcut hints
// ---------------------------------------------------------------------------
const navItems = [
  { href: '/dashboard',    label: 'Dashboard',     icon: LayoutDashboard, shortcut: '⌘D' },
  { href: '/target-roles', label: 'Target Roles',  icon: Target,          shortcut: '⌘R' },
  { href: '/chat',         label: 'Chat',           icon: MessageSquare,   shortcut: '⌘H' },
  { href: '/notifications',label: 'Notifications', icon: Bell,            shortcut: '⌘B' },
  { href: '/settings',     label: 'Settings',       icon: Settings,        shortcut: '⌘,' },
]

// ---------------------------------------------------------------------------
// User avatar section
// ---------------------------------------------------------------------------
function UserSection({ onLogout }: { onLogout: () => void }) {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    api.get<User>('/auth/me').then(setUser).catch(() => {})
  }, [])

  const initials = user?.full_name
    ? user.full_name.split(' ').map(p => p[0]).join('').slice(0, 2).toUpperCase()
    : user?.email?.slice(0, 2).toUpperCase() ?? 'SP'

  return (
    <div className="border-t border-border/60 p-2">
      {/* Avatar trigger row */}
      <button
        onClick={() => setOpen(o => !o)}
        className={cn(
          'flex w-full items-center gap-2.5 rounded-lg px-2 py-2 text-left transition-colors',
          'hover:bg-sidebar-accent/60',
          open && 'bg-sidebar-accent/60',
        )}
      >
        {/* Avatar circle */}
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/15 text-xs font-bold text-primary">
          {initials}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-xs font-semibold text-sidebar-foreground">
            {user?.full_name || user?.email?.split('@')[0] || 'Loading…'}
          </p>
          <p className="truncate text-[10px] text-muted-foreground">
            {user?.email ?? ''}
          </p>
        </div>
        <ChevronDown className={cn(
          'h-3.5 w-3.5 shrink-0 text-muted-foreground transition-transform duration-200',
          open && 'rotate-180',
        )} />
      </button>

      {/* Dropdown */}
      {open && (
        <div className="mt-1 flex flex-col gap-0.5 rounded-lg border border-border/60 bg-card p-1 shadow-sm">
          {/* GitHub link */}
          {user?.github_username && (
            <a
              href={`https://github.com/${user.github_username}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 rounded-md px-2.5 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              <ExternalLink className="h-3.5 w-3.5" />
              @{user.github_username}
            </a>
          )}

          <button
            onClick={() => { setOpen(false); router.push('/settings') }}
            className="flex items-center gap-2 rounded-md px-2.5 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <Settings className="h-3.5 w-3.5" />
            Settings
          </button>

          <button
            onClick={() => { setOpen(false); router.push('/settings/share') }}
            className="flex items-center gap-2 rounded-md px-2.5 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <Share2 className="h-3.5 w-3.5" />
            Share Profile
          </button>

          <div className="my-1 border-t border-border/50" />

          <button
            onClick={onLogout}
            className="flex items-center gap-2 rounded-md px-2.5 py-1.5 text-xs text-destructive transition-colors hover:bg-destructive/10"
          >
            <LogOut className="h-3.5 w-3.5" />
            Sign out
          </button>
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main Sidebar
// ---------------------------------------------------------------------------
export default function Sidebar({ onCommandPalette }: { onCommandPalette?: () => void }) {
  const pathname = usePathname()
  const router = useRouter()

  function handleLogout() {
    clearTokens()
    router.replace('/login')
  }

  return (
    <aside className="flex h-full w-64 flex-col border-r border-border bg-sidebar">
      {/* Brand header */}
      <div className="flex items-center gap-2 border-b border-border/60 px-5 py-4">
        <ShieldCheck className="h-5 w-5 text-primary" />
        <span className="text-base font-bold tracking-tight">SkillProof</span>

        {/* ⌘K palette hint */}
        {onCommandPalette && (
          <button
            onClick={onCommandPalette}
            className="ml-auto flex items-center gap-1 rounded-md border border-border/60 px-1.5 py-0.5 text-[10px] text-muted-foreground transition-colors hover:border-primary/40 hover:text-primary"
            title="Open command palette (⌘K)"
          >
            <Command className="h-2.5 w-2.5" />K
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-0.5 px-2 py-3">
        {navItems.map(({ href, label, icon: Icon, shortcut }) => {
          const isActive = pathname === href || pathname.startsWith(href + '/')
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium',
                'transition-all duration-150',
                isActive
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground',
              )}
            >
              {/* Active left-border accent */}
              {isActive && (
                <span className="absolute inset-y-1 left-0 w-0.5 rounded-full bg-primary" />
              )}
              <Icon className="h-4 w-4 shrink-0" />
              <span className="flex-1">{label}</span>
              {/* Shortcut hint — show on hover */}
              <span className={cn(
                'rounded border border-border/50 px-1 py-px text-[10px] tabular-nums text-muted-foreground/70',
                'opacity-0 transition-opacity duration-150 group-hover:opacity-100',
                isActive && 'opacity-60',
              )}>
                {shortcut}
              </span>
            </Link>
          )
        })}
      </nav>

      {/* User section at bottom */}
      <UserSection onLogout={handleLogout} />
    </aside>
  )
}
