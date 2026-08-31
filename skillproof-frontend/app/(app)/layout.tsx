'use client'
import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import Sidebar from '@/components/Sidebar'
import { useRequireAuth } from '@/lib/hooks/useAuth'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const checked = useRequireAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  if (!checked) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="space-y-3 w-64">
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-black/50 md:hidden" onClick={() => setSidebarOpen(false)} />
      )}
      <div className={`fixed inset-y-0 left-0 z-50 md:relative md:flex md:z-auto transition-transform duration-200 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <Sidebar />
      </div>
      <div className="flex flex-1 flex-col overflow-hidden">
        <div className="flex h-14 items-center border-b border-border bg-background px-4 md:hidden">
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <span className="ml-3 text-lg font-semibold">SkillProof</span>
        </div>
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
