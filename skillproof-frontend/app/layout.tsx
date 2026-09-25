import type { Metadata, Viewport } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'
import { TooltipProvider } from '@/components/ui/tooltip'

const geistSans = Geist({ variable: '--font-geist-sans', subsets: ['latin'] })
const geistMono = Geist_Mono({ variable: '--font-geist-mono', subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'SkillProof — Developer Readiness Verification',
  description: 'Verify your engineering readiness with evidence-grounded GitHub behavioral analysis',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'SkillProof',
  },
  formatDetection: { telephone: false },
  openGraph: {
    type: 'website',
    title: 'SkillProof — Developer Readiness Verification',
    description: 'Verify your engineering readiness with evidence-grounded GitHub behavioral analysis',
  },
}

export const viewport: Viewport = {
  themeColor: '#18181b',
  width: 'device-width',
  initialScale: 1,
  minimumScale: 1,
  viewportFit: 'cover',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* PWA iOS splash / icon hints */}
        <link rel="apple-touch-icon" sizes="192x192" href="/icons/icon-192x192.png" />
        <link rel="apple-touch-icon" sizes="512x512" href="/icons/icon-512x512.png" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="SkillProof" />
      </head>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}>
        <TooltipProvider>
          {children}
        </TooltipProvider>
      </body>
    </html>
  )
}
