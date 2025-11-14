import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'NexusLang v2 - AI-Native Programming Language',
  description: 'The world\'s first AI-native programming language with binary optimization, personality-driven behavior, and voice-first interaction.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  )
}
