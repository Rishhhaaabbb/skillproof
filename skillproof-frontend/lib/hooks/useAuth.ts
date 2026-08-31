'use client'
import { useState, useEffect } from 'react'
import { isAuthenticated } from '../auth'
import { useRouter } from 'next/navigation'

export function useRequireAuth() {
  const router = useRouter()
  const [checked, setChecked] = useState(false)

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace('/login')
    } else {
      setChecked(true)
    }
  }, [router])

  return checked
}
