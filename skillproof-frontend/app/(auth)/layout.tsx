'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { isAuthenticated } from '@/lib/auth'
import { ShieldCheck, GitCommit, Users, CheckCircle2 } from 'lucide-react'
import { cn } from '@/lib/utils'

const proofPoints = [
  {
    icon: GitCommit,
    title: 'Evidence-grounded',
    body: 'Every verdict traces back to a specific commit, PR, or review — never a guess.',
  },
  {
    icon: Users,
    title: 'Adversarial evaluation',
    body: 'A Skeptic, Advocate, and Judge examine the same evidence and argue both sides.',
  },
  {
    icon: CheckCircle2,
    title: 'Verified gap closure',
    body: 'Tasks are assigned for every gap, and completion is automatically confirmed.',
  },
]

function RotatingProofPoints() {
  const [active, setActive] = useState(0)

  useEffect(() => {
    const t = setInterval(() => setActive(i => (i + 1) % proofPoints.length), 3500)
    return () => clearInterval(t)
  }, [])

  return (
    <div className="mt-10 space-y-3">
      {proofPoints.map((p, i) => {
        const Icon = p.icon
        return (
          <div
            key={i}
            className={cn(
              'flex items-start gap-3 rounded-xl border p-4 transition-all duration-500',
              active === i
                ? 'border-white/20 bg-white/10 opacity-100 translate-x-0'
                : 'border-white/5 bg-white/5 opacity-40 translate-x-0'
            )}
          >
            <div className={cn(
              'mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg transition-colors duration-500',
              active === i ? 'bg-white/20' : 'bg-white/5'
            )}>
              <Icon className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white">{p.title}</p>
              <p className="mt-0.5 text-xs leading-relaxed text-white/60">{p.body}</p>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  useEffect(() => {
    if (isAuthenticated()) router.replace('/dashboard')
  }, [router])

  return (
    <div className="flex min-h-screen bg-background">
      {/* ── Left panel — brand + proof points ── */}
      <div className="relative hidden lg:flex lg:w-[52%] flex-col justify-between overflow-hidden p-12"
        style={{
          background: 'linear-gradient(135deg, oklch(0.13 0 0) 0%, oklch(0.18 0.02 264) 50%, oklch(0.13 0 0) 100%)',
        }}
      >
        {/* Subtle grid overlay */}
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              'linear-gradient(rgba(255,255,255,0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.8) 1px, transparent 1px)',
            backgroundSize: '40px 40px',
          }}
        />

        {/* Glowing orb */}
        <div
          className="pointer-events-none absolute -left-32 top-1/3 h-[500px] w-[500px] rounded-full opacity-10 blur-[120px]"
          style={{ background: 'oklch(0.6 0.2 264)' }}
        />

        {/* Top — logo */}
        <div className="relative flex items-center gap-2.5">
          <div className="relative flex h-9 w-9 items-center justify-center">
            <div className="absolute inset-0 animate-ping rounded-full bg-white/10" />
            <ShieldCheck className="relative h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-bold tracking-tight text-white">SkillProof</span>
        </div>

        {/* Middle — headline + proof points */}
        <div className="relative">
          <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
            <span className="text-xs font-medium text-white/70">AI-powered verification</span>
          </div>
          <h1 className="mt-4 text-4xl font-bold leading-tight tracking-tight text-white">
            Verify real<br />engineering capability.<br />
            <span className="text-white/50">Not just keywords.</span>
          </h1>
          <p className="mt-4 text-sm leading-relaxed text-white/50">
            SkillProof analyzes your GitHub activity through adversarial AI evaluation
            and produces a calibrated, evidence-grounded readiness signal.
          </p>
          <RotatingProofPoints />
        </div>

        {/* Bottom — social proof line */}
        <div className="relative">
          <p className="text-xs text-white/30">
            Built for developers who want to prove capability, not just claim it.
          </p>
        </div>
      </div>

      {/* ── Right panel — auth form ── */}
      <div className="flex flex-1 flex-col items-center justify-center px-6 py-12 lg:px-16">
        {/* Mobile logo */}
        <div className="mb-8 flex items-center gap-2 lg:hidden">
          <ShieldCheck className="h-6 w-6 text-foreground" />
          <span className="text-xl font-bold tracking-tight">SkillProof</span>
        </div>

        <div className="w-full max-w-[400px]">
          {children}
        </div>
      </div>
    </div>
  )
}
