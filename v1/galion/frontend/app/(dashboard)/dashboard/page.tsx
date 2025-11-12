"use client"

import { useEffect, useState } from 'react'
import { useAuthStore } from '@/lib/stores/auth'
import { analyticsApi, usersApi, documentsApi } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Users, FileText, Activity, TrendingUp } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'

interface DashboardStats {
  total_users: number
  total_documents: number
  pending_documents: number
  active_users: number
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Fetch system metrics if admin, otherwise fetch user-specific data
        if (user?.role === 'admin') {
          const metrics = await analyticsApi.getMetrics()
          setStats({
            total_users: metrics.total_users,
            total_documents: metrics.total_documents,
            pending_documents: metrics.pending_documents,
            active_users: metrics.active_users,
          })
        } else {
          // For regular users, fetch their documents
          const docs = await documentsApi.list()
          setStats({
            total_users: 1,
            total_documents: docs.length,
            pending_documents: docs.filter(d => d.status === 'pending').length,
            active_users: 1,
          })
        }
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchStats()
  }, [user])

  const statCards = user?.role === 'admin'
    ? [
        {
          title: 'Total Users',
          value: stats?.total_users || 0,
          icon: Users,
          description: 'Registered users',
          color: 'text-blue-500',
        },
        {
          title: 'Active Users',
          value: stats?.active_users || 0,
          icon: Activity,
          description: 'Active in last 24h',
          color: 'text-green-500',
        },
        {
          title: 'Total Documents',
          value: stats?.total_documents || 0,
          icon: FileText,
          description: 'All documents',
          color: 'text-purple-500',
        },
        {
          title: 'Pending Review',
          value: stats?.pending_documents || 0,
          icon: TrendingUp,
          description: 'Awaiting approval',
          color: 'text-orange-500',
        },
      ]
    : [
        {
          title: 'My Documents',
          value: stats?.total_documents || 0,
          icon: FileText,
          description: 'Your uploaded documents',
          color: 'text-purple-500',
        },
        {
          title: 'Pending Review',
          value: stats?.pending_documents || 0,
          icon: TrendingUp,
          description: 'Awaiting approval',
          color: 'text-orange-500',
        },
      ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back, {user?.name || 'User'}! 
          {user?.role === 'admin' && ' Here is your system overview.'}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  <>
                    <div className="text-2xl font-bold">{stat.value}</div>
                    <p className="text-xs text-muted-foreground">
                      {stat.description}
                    </p>
                  </>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {isLoading ? (
              <>
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </>
            ) : (
              <div className="text-sm text-muted-foreground">
                No recent activity to display.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <a
              href="/documents"
              className="flex flex-col items-center justify-center p-6 rounded-lg border border-border hover:bg-accent transition-colors"
            >
              <FileText className="h-8 w-8 mb-2 text-purple-500" />
              <span className="text-sm font-medium">Upload Document</span>
            </a>
            {user?.role === 'admin' && (
              <a
                href="/users"
                className="flex flex-col items-center justify-center p-6 rounded-lg border border-border hover:bg-accent transition-colors"
              >
                <Users className="h-8 w-8 mb-2 text-blue-500" />
                <span className="text-sm font-medium">Manage Users</span>
              </a>
            )}
            <a
              href="/status"
              className="flex flex-col items-center justify-center p-6 rounded-lg border border-border hover:bg-accent transition-colors"
            >
              <Activity className="h-8 w-8 mb-2 text-green-500" />
              <span className="text-sm font-medium">System Status</span>
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

