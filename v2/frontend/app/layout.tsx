import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'
import ChatWidget from '@/components/chat/ChatWidget'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NexusLang v2 - AI Development Platform',
  description: 'The 22nd Century AI Development Platform',
  keywords: ['NexusLang', 'AI', 'Programming Language', 'IDE', 'Grokopedia'],
  authors: [{ name: 'NexusLang Team' }],
  viewport: 'width=device-width, initial-scale=1',
  themeColor: '#000000',
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
        <Toaster
          position="bottom-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#18181b',
              color: '#fff',
              border: '1px solid #27272a',
            },
          }}
        />
        {/* Global AI Chat Widget - available on all pages */}
        <ChatWidget />
      </body>
    </html>
  )
}

