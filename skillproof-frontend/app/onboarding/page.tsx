'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { ShieldCheck } from 'lucide-react'
import OnboardingWizard from '@/components/OnboardingWizard'
import { isAuthenticated } from '@/lib/auth'
import api from '@/lib/api'
import type { User } from '@/lib/types'

export default function OnboardingPage() {
  const router = useRouter()
  const [ready, setReady] = useState(false)

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isAuthenticated()) {
      router.replace('/login')
      return
    }

    // If user already has analyses, skip onboarding → go straight to dashboard
    api.get<User>('/auth/me')
      .then(() => {
        // Check if they've already done an analysis
        return api.get('/api/analysis/latest').then(() => {
          // Has an analysis — already onboarded
          router.replace('/dashboard')
        }).catch(() => {
          // No analysis yet — show onboarding
          setReady(true)
        })
      })
      .catch(() => {
        // Can't load user — probably not authed
        router.replace('/login')
      })
  }, [router])

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex items-center gap-2 text-muted-foreground">
          <ShieldCheck className="h-5 w-5 animate-pulse text-primary" />
          <span className="text-sm">Loading…</span>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* Top brand bar */}
      <header className="border-b border-border/60 bg-card/80 px-6 py-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-primary" />
          <span className="text-sm font-bold">SkillProof</span>
        </div>
      </header>

      {/* Wizard centred on page */}
      <main className="flex flex-1 items-start justify-center px-4 py-12 sm:items-center">
        <OnboardingWizard onComplete={() => router.replace('/dashboard')} />
      </main>
    </div>
  )
}
