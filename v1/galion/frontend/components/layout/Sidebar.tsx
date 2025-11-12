"use client"

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/lib/stores/ui'
import { useAuthStore } from '@/lib/stores/auth'
import {
  LayoutDashboard,
  Users,
  FileText,
  Mic,
  BarChart3,
  Activity,
  BookOpen,
  MessageSquare,
  Settings,
  X,
} from 'lucide-react'
import { Button } from '@/components/ui/button'

interface NavItem {
  title: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  adminOnly?: boolean
}

const navItems: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    title: 'Admin Panel',
    href: '/admin',
    icon: Settings,
    adminOnly: true,
  },
  {
    title: 'Users',
    href: '/users',
    icon: Users,
    adminOnly: true,
  },
  {
    title: 'Documents',
    href: '/documents',
    icon: FileText,
  },
  {
    title: 'Voice Commands',
    href: '/voice',
    icon: Mic,
  },
  {
    title: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    adminOnly: true,
  },
  {
    title: 'Service Status',
    href: '/status',
    icon: Activity,
  },
  {
    title: 'Documentation',
    href: '/docs',
    icon: BookOpen,
  },
  {
    title: 'AI Chat',
    href: '/chat',
    icon: MessageSquare,
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const { sidebarOpen, setSidebarOpen } = useUIStore()
  const { user } = useAuthStore()

  const filteredNavItems = navItems.filter((item) => {
    if (item.adminOnly && user?.role !== 'admin') {
      return false
    }
    return true
  })

  return (
    <>
      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-16 z-40 h-[calc(100vh-4rem)] w-64 border-r bg-background transition-transform duration-300 ease-in-out",
          sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        <div className="flex h-full flex-col overflow-y-auto p-4">
          {/* Close button for mobile */}
          <Button
            variant="ghost"
            size="icon"
            className="ml-auto mb-4 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </Button>

          {/* Navigation */}
          <nav className="space-y-2">
            {filteredNavItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                  onClick={() => {
                    // Close sidebar on mobile after clicking
                    if (window.innerWidth < 1024) {
                      setSidebarOpen(false)
                    }
                  }}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.title}</span>
                </Link>
              )
            })}
          </nav>

          {/* User info at bottom */}
          <div className="mt-auto pt-4 border-t">
            <div className="flex items-center space-x-3 px-3 py-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm font-medium">
                {user?.name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {user?.name || 'User'}
                </p>
                <p className="text-xs text-muted-foreground truncate">
                  {user?.role === 'admin' ? 'Admin' : 'User'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}

