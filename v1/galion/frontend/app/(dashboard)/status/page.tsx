"use client"

import { useEffect, useState } from 'react'
import { analyticsApi } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Activity, CheckCircle2, XCircle, Clock } from 'lucide-react'
import type { ServiceHealth } from '@/types'

export default function StatusPage() {
  const [services, setServices] = useState<ServiceHealth[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchServiceHealth()
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchServiceHealth, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchServiceHealth = async () => {
    try {
      const health = await analyticsApi.getServiceHealth()
      setServices(health)
    } catch (error) {
      console.error('Failed to fetch service health:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-500'
      case 'unhealthy':
        return 'text-red-500'
      default:
        return 'text-yellow-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle2 className="h-5 w-5" />
      case 'unhealthy':
        return <XCircle className="h-5 w-5" />
      default:
        return <Clock className="h-5 w-5" />
    }
  }

  const healthyCount = services.filter(s => s.status === 'healthy').length
  const totalCount = services.length
  const healthPercentage = totalCount > 0 ? Math.round((healthyCount / totalCount) * 100) : 0

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Service Status</h1>
        <p className="text-muted-foreground">
          Real-time monitoring of all Nexus Core services
        </p>
      </div>

      {/* Overall Health */}
      <Card>
        <CardHeader>
          <CardTitle>System Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-4xl font-bold">{healthPercentage}%</div>
              <p className="text-sm text-muted-foreground">
                {healthyCount} of {totalCount} services operational
              </p>
            </div>
            <Activity className={`h-16 w-16 ${healthPercentage === 100 ? 'text-green-500' : 'text-yellow-500'}`} />
          </div>
        </CardContent>
      </Card>

      {/* Service List */}
      <div className="grid gap-4 md:grid-cols-2">
        {isLoading ? (
          <>
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </>
        ) : (
          services.map((service) => (
            <Card key={service.service}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{service.service}</CardTitle>
                  <div className={getStatusColor(service.status)}>
                    {getStatusIcon(service.status)}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Status:</span>
                    <span className={`font-medium ${getStatusColor(service.status)}`}>
                      {service.status}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Response Time:</span>
                    <span className="font-medium">{service.response_time}ms</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Last Checked:</span>
                    <span className="font-medium">
                      {new Date(service.last_checked).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      <p className="text-xs text-muted-foreground text-center">
        Auto-refreshes every 10 seconds
      </p>
    </div>
  )
}

