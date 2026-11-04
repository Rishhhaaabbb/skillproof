'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2, AlertCircle, Eye, EyeOff, ArrowRight, Github } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { setTokens } from '@/lib/auth'
import api from '@/lib/api'
import type { TokenResponse } from '@/lib/types'
import { cn } from '@/lib/utils'

const schema = z.object({
  full_name: z.string().min(2, 'Full name must be at least 2 characters'),
  email: z.string().email('Enter a valid email address'),
  github_username: z
    .string()
    .min(1, 'GitHub username is required')
    .regex(/^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$/, 'Enter a valid GitHub username'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters'),
})
type FormValues = z.infer<typeof schema>

function FieldInput({
  id,
  label,
  error,
  hint,
  children,
}: {
  id: string
  label: string
  error?: string
  hint?: string
  children: React.ReactNode
}) {
  return (
    <div className="space-y-1.5">
      <label className="text-sm font-medium text-foreground" htmlFor={id}>
        {label}
      </label>
      {children}
      {hint && !error && <p className="text-xs text-muted-foreground">{hint}</p>}
      {error && (
        <p className="flex items-center gap-1 text-xs text-destructive">
          <AlertCircle className="h-3 w-3 shrink-0" />
          {error}
        </p>
      )}
    </div>
  )
}

export default function SignupPage() {
  const router = useRouter()
  const [apiError, setApiError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  async function onSubmit(values: FormValues) {
    setApiError(null)
    try {
      const data = await api.post<TokenResponse>('/auth/signup', values)
      setTokens(data.access_token, data.refresh_token)
      router.replace('/onboarding')
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Something went wrong. Please try again.'
      setApiError(msg)
    }
  }

  const inputClass = (hasError: boolean) =>
    cn(
      'flex h-9 w-full rounded-lg border bg-background px-3 py-2 text-sm outline-none transition-colors',
      'placeholder:text-muted-foreground/50',
      'focus:border-ring focus:ring-2 focus:ring-ring/20',
      hasError ? 'border-destructive focus:ring-destructive/20' : 'border-input'
    )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-bold tracking-tight">Create your account</h2>
          <Badge variant="secondary" className="text-xs">Free</Badge>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Connect your GitHub and start verifying your readiness
        </p>
      </div>

      {/* Error banner */}
      {apiError && (
        <div className="flex items-start gap-2.5 rounded-lg border border-destructive/30 bg-destructive/8 px-4 py-3 text-sm text-destructive">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{apiError}</span>
        </div>
      )}

      <Card className="border-border/60 shadow-sm">
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            {/* Full name */}
            <FieldInput id="full_name" label="Full name" error={errors.full_name?.message}>
              <input
                id="full_name"
                type="text"
                autoComplete="name"
                placeholder="Rishab Shetty"
                {...register('full_name')}
                className={inputClass(!!errors.full_name)}
              />
            </FieldInput>

            {/* Email */}
            <FieldInput id="email" label="Email address" error={errors.email?.message}>
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                {...register('email')}
                className={inputClass(!!errors.email)}
              />
            </FieldInput>

            {/* GitHub username */}
            <FieldInput
              id="github_username"
              label="GitHub username"
              error={errors.github_username?.message}
              hint="This is used to fetch your public activity for analysis."
            >
              <div className="relative">
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                  <Github className="h-4 w-4" />
                </div>
                <input
                  id="github_username"
                  type="text"
                  autoComplete="off"
                  placeholder="your-github-handle"
                  {...register('github_username')}
                  className={cn(inputClass(!!errors.github_username), 'pl-9')}
                />
              </div>
            </FieldInput>

            {/* Password */}
            <FieldInput
              id="password"
              label="Password"
              error={errors.password?.message}
              hint="Minimum 8 characters."
            >
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  placeholder="••••••••"
                  {...register('password')}
                  className={cn(inputClass(!!errors.password), 'pr-9')}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(v => !v)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </FieldInput>

            {/* Submit */}
            <Button
              type="submit"
              size="lg"
              disabled={isSubmitting}
              className="mt-2 w-full gap-2"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Creating account…
                </>
              ) : (
                <>
                  Create account
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </Button>

            {/* Terms note */}
            <p className="text-center text-xs text-muted-foreground">
              By creating an account you agree to our{' '}
              <span className="underline underline-offset-2 cursor-pointer hover:text-foreground transition-colors">
                terms of service
              </span>
              .
            </p>
          </form>
        </CardContent>
      </Card>

      {/* Footer link */}
      <p className="text-center text-sm text-muted-foreground">
        Already have an account?{' '}
        <Link
          href="/login"
          className="font-medium text-foreground underline-offset-4 hover:underline transition-colors"
        >
          Sign in
        </Link>
      </p>
    </div>
  )
}
