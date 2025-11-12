"use client"

import { useAuthStore } from '@/lib/stores/auth'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Shield, Users, FileText, Activity, Database, Settings } from 'lucide-react'
import Link from 'next/link'

export default function AdminPage() {
  const { user } = useAuthStore()

  if (user?.role !== 'admin') {
    return (
      <div className="flex items-center justify-center h-full">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Access Denied</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              You do not have permission to view this page.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const adminTools = [
    {
      title: 'User Management',
      description: 'Manage all users, roles, and permissions',
      icon: Users,
      href: '/users',
      color: 'text-blue-500',
    },
    {
      title: 'Document Review',
      description: 'Approve or reject pending documents',
      icon: FileText,
      href: '/documents',
      color: 'text-purple-500',
    },
    {
      title: 'System Analytics',
      description: 'View system metrics and performance',
      icon: Activity,
      href: '/analytics',
      color: 'text-green-500',
    },
    {
      title: 'Service Status',
      description: 'Monitor all backend services',
      icon: Database,
      href: '/status',
      color: 'text-orange-500',
    },
    {
      title: 'System Settings',
      description: 'Configure system-wide settings',
      icon: Settings,
      href: '/settings',
      color: 'text-red-500',
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Shield className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Admin Panel</h1>
          <p className="text-muted-foreground">
            CEO Control Center - Full System Access
          </p>
        </div>
      </div>

      <Card className="bg-primary/5 border-primary">
        <CardHeader>
          <CardTitle>Welcome, {user.name}</CardTitle>
          <CardDescription>
            You have full administrative control over the GALION.APP platform
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {adminTools.map((tool) => {
          const Icon = tool.icon
          return (
            <Link key={tool.href} href={tool.href}>
              <Card className="hover:bg-accent transition-colors cursor-pointer h-full">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <Icon className={`h-6 w-6 ${tool.color}`} />
                    <CardTitle className="text-lg">{tool.title}</CardTitle>
                  </div>
                  <CardDescription>{tool.description}</CardDescription>
                </CardHeader>
              </Card>
            </Link>
          )
        })}
      </div>
    </div>
  )
}

