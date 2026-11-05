'use client'
import { useState, useEffect, useCallback } from 'react'
import { Menu, X } from 'lucide-react'
import Sidebar from '@/components/Sidebar'
import NotificationBell from '@/components/NotificationBell'
import CommandPalette from '@/components/CommandPalette'
import ErrorBoundary from '@/components/ErrorBoundary'
import { useRequireAuth } from '@/lib/hooks/useAuth'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const checked = useRequireAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [paletteOpen, setPaletteOpen] = useState(false)

  // ── Global ⌘K keyboard shortcut ──
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault()
      setPaletteOpen(o => !o)
    }
    // Shortcut navigation — only when no input is focused
    if (document.activeElement?.tagName === 'INPUT' ||
        document.activeElement?.tagName === 'TEXTAREA') return
    if (e.metaKey || e.ctrlKey) {
      const map: Record<string, string> = {
        d: '/dashboard',
        r: '/target-roles',   // ⌘R (roles)
        h: '/chat',           // ⌘H (help/chat)
        b: '/notifications',  // ⌘B (bell)
        ',': '/settings',
      }
      if (map[e.key]) {
        e.preventDefault()
        window.location.href = map[e.key]
      }
    }
  }, [])

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])

  // Loading skeleton while auth check is in flight
  if (!checked) {
    return (
      <div className="flex h-screen">
        {/* Sidebar skeleton */}
        <div className="hidden w-64 shrink-0 flex-col border-r border-border bg-sidebar p-4 md:flex">
          <div className="mb-6 flex items-center gap-2 px-2 py-1">
            <Skeleton className="h-5 w-5 rounded" />
            <Skeleton className="h-5 w-24" />
          </div>
          {[1, 2, 3, 4, 5].map(i => (
            <Skeleton key={i} className="mb-1 h-9 w-full rounded-lg" />
          ))}
          <div className="mt-auto">
            <Skeleton className="h-12 w-full rounded-lg" />
          </div>
        </div>
        {/* Content skeleton */}
        <div className="flex flex-1 flex-col p-6 gap-4">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-48 w-full rounded-xl" />
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="flex h-screen overflow-hidden">
        {/* Mobile sidebar backdrop — blur overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm transition-opacity md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar — slides in on mobile */}
        <div className={[
          'fixed inset-y-0 left-0 z-50 transition-transform duration-200 ease-in-out',
          'md:relative md:z-auto md:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        ].join(' ')}>
          <Sidebar onCommandPalette={() => { setSidebarOpen(false); setPaletteOpen(true) }} />
        </div>

        {/* Right side */}
        <div className="flex flex-1 flex-col overflow-hidden">
          {/* Mobile top bar */}
          <div className="flex h-14 shrink-0 items-center justify-between border-b border-border/60 bg-card/80 px-4 backdrop-blur-sm md:hidden">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                aria-label="Toggle menu"
              >
                {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
              <span className="text-base font-bold">SkillProof</span>
            </div>
            {/* Bell visible on mobile top bar */}
            <NotificationBell />
          </div>

          {/* Page content with error boundary */}
          <main className="flex flex-1 flex-col overflow-hidden">
            <ErrorBoundary>
              {children}
            </ErrorBoundary>
          </main>
        </div>
      </div>

      {/* Command palette — rendered outside the layout div to avoid stacking context issues */}
      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} />
    </>
  )
}
