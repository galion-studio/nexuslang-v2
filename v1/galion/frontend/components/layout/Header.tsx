"use client"

import { Menu, Bell, User, LogOut, Settings, Moon, Sun } from 'lucide-react'
import { useAuthStore } from '@/lib/stores/auth'
import { useUIStore } from '@/lib/stores/ui'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export function Header() {
  const { user, logout } = useAuthStore()
  const { toggleSidebar, darkMode, toggleDarkMode } = useUIStore()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center px-4">
        {/* Menu button for mobile */}
        <Button
          variant="ghost"
          size="icon"
          className="mr-4"
          onClick={toggleSidebar}
        >
          <Menu className="h-5 w-5" />
        </Button>

        {/* Logo / Brand */}
        <Link href="/dashboard" className="flex items-center space-x-2">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
            GALION.APP
          </div>
        </Link>

        <div className="flex-1" />

        {/* Right side actions */}
        <div className="flex items-center space-x-2">
          {/* Dark mode toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleDarkMode}
          >
            {darkMode ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </Button>

          {/* Notifications */}
          <Button variant="ghost" size="icon">
            <Bell className="h-5 w-5" />
          </Button>

          {/* User menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                <User className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">
                    {user?.name || 'User'}
                  </p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {user?.email || ''}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => router.push('/profile')}>
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => router.push('/settings')}>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout}>
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}

