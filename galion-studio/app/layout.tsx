import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Galion Studio - AI Content Creation Platform',
  description: 'Create stunning images, videos, and content with AI. Professional tools for creators.',
  keywords: ['AI', 'Content Creation', 'Image Generation', 'Video Generation', 'Galion Studio'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        {children}
        <Toaster position="bottom-right" />
      </body>
    </html>
  )
}

