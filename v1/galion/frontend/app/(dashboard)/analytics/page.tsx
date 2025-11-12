"use client"

import { useEffect, useState } from 'react'
import { analyticsApi } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { BarChart3, TrendingUp, Users, Activity } from 'lucide-react'
import type { SystemMetrics } from '@/types'

export default function AnalyticsPage() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await analyticsApi.getMetrics()
        setMetrics(data)
      } catch (error) {
        console.error('Failed to fetch metrics:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchMetrics()
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchMetrics, 30000)
    return () => clearInterval(interval)
  }, [])

  const statCards = [
    {
      title: 'Total Users',
      value: metrics?.total_users || 0,
      icon: Users,
      color: 'text-blue-500',
    },
    {
      title: 'Active Users',
      value: metrics?.active_users || 0,
      icon: Activity,
      color: 'text-green-500',
    },
    {
      title: 'API Calls',
      value: metrics?.total_api_calls || 0,
      icon: BarChart3,
      color: 'text-purple-500',
    },
    {
      title: 'Avg Response Time',
      value: `${metrics?.avg_response_time || 0}ms`,
      icon: TrendingUp,
      color: 'text-orange-500',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground">
          System metrics and performance insights
        </p>
      </div>

      {/* Metrics Grid */}
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
                  <div className="text-2xl font-bold">{stat.value}</div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Charts placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Usage Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <BarChart3 className="h-16 w-16 mx-auto mb-4 opacity-20" />
              <p>Charts visualization coming soon</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

