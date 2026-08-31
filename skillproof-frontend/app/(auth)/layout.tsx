'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { isAuthenticated } from '@/lib/auth'

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  useEffect(() => {
    if (isAuthenticated()) router.replace('/dashboard')
  }, [router])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-muted/40 p-4">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight">SkillProof</h1>
        <p className="mt-1 text-sm text-muted-foreground">Evidence-grounded developer verification</p>
      </div>
      <div className="w-full max-w-md">
        {children}
      </div>
    </div>
  )
}
