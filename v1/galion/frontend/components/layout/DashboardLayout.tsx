"use client"

import { useEffect } from 'react'
import { useUIStore } from '@/lib/stores/ui'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import { Footer } from './Footer'

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { setDarkMode } = useUIStore()

  useEffect(() => {
    // Initialize dark mode on mount
    setDarkMode(true)
  }, [setDarkMode])

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 lg:ml-64 p-6">
          {children}
        </main>
      </div>
      <Footer />
    </div>
  )
}

