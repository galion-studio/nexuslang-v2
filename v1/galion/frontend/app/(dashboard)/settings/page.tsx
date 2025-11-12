"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { useUIStore } from '@/lib/stores/ui'
import { Moon, Sun } from 'lucide-react'

export default function SettingsPage() {
  const { darkMode, toggleDarkMode } = useUIStore()

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your application preferences
        </p>
      </div>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>
            Customize how the app looks
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label>Theme</Label>
              <p className="text-sm text-muted-foreground">
                Choose your preferred theme
              </p>
            </div>
            <Button variant="outline" onClick={toggleDarkMode}>
              {darkMode ? (
                <>
                  <Sun className="mr-2 h-4 w-4" />
                  Light Mode
                </>
              ) : (
                <>
                  <Moon className="mr-2 h-4 w-4" />
                  Dark Mode
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>
            Configure notification preferences
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Notification settings coming soon
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

