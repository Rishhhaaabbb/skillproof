'use client'
import { useEffect, useState, useCallback, useRef } from 'react'
import { useRouter } from 'next/navigation'
import {
  LayoutDashboard, Target, MessageSquare, Bell, Settings,
  Share2, Search, ArrowRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'

// ---------------------------------------------------------------------------
// Searchable pages / commands
// ---------------------------------------------------------------------------
const COMMANDS = [
  { id: 'dashboard',    label: 'Dashboard',          description: 'Your TPR score and activity overview', icon: LayoutDashboard, href: '/dashboard',      shortcut: '⌘D' },
  { id: 'target-roles', label: 'Target Roles',        description: 'Manage job roles and gap analysis',     icon: Target,           href: '/target-roles',   shortcut: '⌘R' },
  { id: 'chat',         label: 'Chat',                description: 'Ask SkillProof AI anything',            icon: MessageSquare,    href: '/chat',           shortcut: '⌘H' },
  { id: 'notifications',label: 'Notifications',       description: 'View unread score alerts and tasks',    icon: Bell,             href: '/notifications',  shortcut: '⌘B' },
  { id: 'settings',     label: 'Settings',            description: 'Edit profile, privacy, and account',   icon: Settings,         href: '/settings',       shortcut: '⌘,' },
  { id: 'share',        label: 'Share Profile',       description: 'Manage recruiter share link',           icon: Share2,           href: '/settings/share', shortcut: null  },
]

// ---------------------------------------------------------------------------
// Fuzzy match — returns true if all chars of query appear in order in text
// ---------------------------------------------------------------------------
function fuzzyMatch(query: string, text: string): boolean {
  if (!query) return true
  const q = query.toLowerCase()
  const t = text.toLowerCase()
  let qi = 0
  for (let i = 0; i < t.length && qi < q.length; i++) {
    if (t[i] === q[qi]) qi++
  }
  return qi === q.length
}

interface CommandPaletteProps {
  open: boolean
  onClose: () => void
}

export default function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const router = useRouter()
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const results = COMMANDS.filter(
    c => fuzzyMatch(query, c.label) || fuzzyMatch(query, c.description)
  )

  // Reset state when opening
  useEffect(() => {
    if (open) {
      setQuery('')
      setSelected(0)
      // Autofocus after paint
      requestAnimationFrame(() => inputRef.current?.focus())
    }
  }, [open])

  // Keep selection in bounds when results change
  useEffect(() => {
    setSelected(s => Math.min(s, Math.max(results.length - 1, 0)))
  }, [results.length])

  const navigate = useCallback((href: string) => {
    onClose()
    router.push(href)
  }, [router, onClose])

  // Keyboard navigation
  useEffect(() => {
    if (!open) return
    function handler(e: KeyboardEvent) {
      if (e.key === 'Escape') { onClose(); return }
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelected(s => Math.min(s + 1, results.length - 1))
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelected(s => Math.max(s - 1, 0))
      }
      if (e.key === 'Enter' && results[selected]) {
        navigate(results[selected].href)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open, results, selected, navigate, onClose])

  if (!open) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Palette */}
      <div className="fixed left-1/2 top-[20%] z-50 w-full max-w-lg -translate-x-1/2 overflow-hidden rounded-2xl border border-border/60 bg-card shadow-2xl">
        {/* Search input */}
        <div className="flex items-center gap-3 border-b border-border/60 px-4 py-3">
          <Search className="h-4 w-4 shrink-0 text-muted-foreground" />
          <input
            ref={inputRef}
            value={query}
            onChange={e => { setQuery(e.target.value); setSelected(0) }}
            placeholder="Search pages…"
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground/60"
          />
          <kbd className="rounded border border-border/60 px-1.5 py-0.5 text-[10px] text-muted-foreground">
            ESC
          </kbd>
        </div>

        {/* Results */}
        <ul className="max-h-72 overflow-y-auto py-1.5">
          {results.length === 0 && (
            <li className="px-4 py-8 text-center text-sm text-muted-foreground">
              No pages match "{query}"
            </li>
          )}
          {results.map((cmd, i) => {
            const Icon = cmd.icon
            const isSelected = i === selected
            return (
              <li key={cmd.id}>
                <button
                  onMouseEnter={() => setSelected(i)}
                  onClick={() => navigate(cmd.href)}
                  className={cn(
                    'flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors',
                    isSelected ? 'bg-primary/8' : 'hover:bg-muted/50',
                  )}
                >
                  <div className={cn(
                    'flex h-7 w-7 shrink-0 items-center justify-center rounded-lg',
                    isSelected ? 'bg-primary/15' : 'bg-muted',
                  )}>
                    <Icon className={cn('h-3.5 w-3.5', isSelected ? 'text-primary' : 'text-muted-foreground')} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={cn('text-sm font-medium', isSelected && 'text-primary')}>
                      {cmd.label}
                    </p>
                    <p className="truncate text-xs text-muted-foreground">{cmd.description}</p>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0">
                    {cmd.shortcut && (
                      <kbd className="rounded border border-border/50 px-1.5 py-0.5 text-[10px] text-muted-foreground">
                        {cmd.shortcut}
                      </kbd>
                    )}
                    {isSelected && <ArrowRight className="h-3.5 w-3.5 text-primary" />}
                  </div>
                </button>
              </li>
            )
          })}
        </ul>

        {/* Footer hint */}
        <div className="flex items-center justify-end gap-3 border-t border-border/60 px-4 py-2 text-[10px] text-muted-foreground">
          <span><kbd className="font-mono">↑↓</kbd> navigate</span>
          <span><kbd className="font-mono">↵</kbd> open</span>
          <span><kbd className="font-mono">ESC</kbd> close</span>
        </div>
      </div>
    </>
  )
}
