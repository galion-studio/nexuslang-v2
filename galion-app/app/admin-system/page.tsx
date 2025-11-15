'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Server,
  Database,
  HardDrive,
  Cpu,
  MemoryStick,
  Network,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Zap,
  Shield,
  Clock,
  TrendingUp,
  TrendingDown
} from 'lucide-react'
import { motion } from 'framer-motion'

interface SystemHealth {
  overall: 'healthy' | 'warning' | 'critical'
  uptime: number
  lastRestart: Date
  services: {
    name: string
    status: 'running' | 'stopped' | 'error'
    uptime: number
    cpu: number
    memory: number
    responseTime: number
  }[]
}

interface PerformanceMetrics {
  timestamp: Date
  cpu: number
  memory: number
  disk: number
  networkIn: number
  networkOut: number
  requestsPerSecond: number
  responseTime: number
  errorRate: number
}

interface SystemLogs {
  id: string
  timestamp: Date
  level: 'info' | 'warning' | 'error'
  service: string
  message: string
  details?: string
}

export default function AdminSystem() {
  const [health, setHealth] = useState<SystemHealth | null>(null)
  const [metrics, setMetrics] = useState<PerformanceMetrics[]>([])
  const [logs, setLogs] = useState<SystemLogs[]>([])
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d'>('1h')

  useEffect(() => {
    loadSystemHealth()
    loadPerformanceMetrics()
    loadSystemLogs()

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      loadSystemHealth()
      loadPerformanceMetrics()
    }, 30000)

    return () => clearInterval(interval)
  }, [timeRange])

  const loadSystemHealth = async () => {
    try {
      // Mock data - in production, this would fetch from monitoring API
      const mockHealth: SystemHealth = {
        overall: 'healthy',
        uptime: 99.9,
        lastRestart: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 days ago
        services: [
          {
            name: 'API Server',
            status: 'running',
            uptime: 99.9,
            cpu: 15.2,
            memory: 234,
            responseTime: 45
          },
          {
            name: 'Database',
            status: 'running',
            uptime: 99.95,
            cpu: 8.5,
            memory: 1567,
            responseTime: 12
          },
          {
            name: 'Voice Processing',
            status: 'running',
            uptime: 99.7,
            cpu: 22.1,
            memory: 456,
            responseTime: 89
          },
          {
            name: 'File Storage',
            status: 'running',
            uptime: 99.99,
            cpu: 3.2,
            memory: 89,
            responseTime: 23
          }
        ]
      }

      setHealth(mockHealth)
    } catch (error) {
      console.error('Failed to load system health:', error)
    }
  }

  const loadPerformanceMetrics = async () => {
    try {
      // Generate mock performance data
      const now = new Date()
      const mockMetrics: PerformanceMetrics[] = []

      for (let i = 23; i >= 0; i--) {
        const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000)
        mockMetrics.push({
          timestamp,
          cpu: Math.random() * 30 + 20,
          memory: Math.random() * 20 + 60,
          disk: Math.random() * 10 + 40,
          networkIn: Math.random() * 100 + 200,
          networkOut: Math.random() * 80 + 150,
          requestsPerSecond: Math.random() * 50 + 100,
          responseTime: Math.random() * 50 + 50,
          errorRate: Math.random() * 2
        })
      }

      setMetrics(mockMetrics)
    } catch (error) {
      console.error('Failed to load performance metrics:', error)
    }
  }

  const loadSystemLogs = async () => {
    try {
      // Mock system logs
      const mockLogs: SystemLogs[] = [
        {
          id: '1',
          timestamp: new Date(Date.now() - 1000 * 60 * 5),
          level: 'info',
          service: 'API Server',
          message: 'User authentication successful',
          details: 'User ID: 12345'
        },
        {
          id: '2',
          timestamp: new Date(Date.now() - 1000 * 60 * 15),
          level: 'warning',
          service: 'Voice Processing',
          message: 'High CPU usage detected',
          details: 'CPU usage: 85%'
        },
        {
          id: '3',
          timestamp: new Date(Date.now() - 1000 * 60 * 30),
          level: 'error',
          service: 'Database',
          message: 'Connection timeout',
          details: 'Failed to connect to primary database'
        },
        {
          id: '4',
          timestamp: new Date(Date.now() - 1000 * 60 * 45),
          level: 'info',
          service: 'File Storage',
          message: 'Backup completed successfully',
          details: 'Backup size: 2.3GB'
        }
      ]

      setLogs(mockLogs)
    } catch (error) {
      console.error('Failed to load system logs:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'stopped':
        return <XCircle className="h-4 w-4 text-red-600" />
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      default:
        return <Activity className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running':
        return <Badge className="bg-green-100 text-green-800">Running</Badge>
      case 'stopped':
        return <Badge variant="destructive">Stopped</Badge>
      case 'error':
        return <Badge className="bg-yellow-100 text-yellow-800">Error</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  const getLogLevelIcon = (level: string) => {
    switch (level) {
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      case 'info':
        return <CheckCircle className="h-4 w-4 text-blue-600" />
      default:
        return <Activity className="h-4 w-4 text-gray-600" />
    }
  }

  const formatBytes = (bytes: number) => {
    const units = ['B', 'KB', 'MB', 'GB']
    let value = bytes
    let unitIndex = 0

    while (value >= 1024 && unitIndex < units.length - 1) {
      value /= 1024
      unitIndex++
    }

    return `${value.toFixed(1)} ${units[unitIndex]}`
  }

  if (loading || !health) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Server className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-muted-foreground">Loading system health...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Health</h1>
          <p className="text-muted-foreground">
            Monitor system performance and service status
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${
              health.overall === 'healthy' ? 'bg-green-500' :
              health.overall === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
            }`} />
            <span className="text-sm font-medium capitalize">{health.overall}</span>
          </div>
          <Button onClick={() => {
            loadSystemHealth()
            loadPerformanceMetrics()
            loadSystemLogs()
          }}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{health.uptime}%</div>
            <p className="text-xs text-muted-foreground">
              Last restart: {health.lastRestart.toLocaleDateString()}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Services</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {health.services.filter(s => s.status === 'running').length}/{health.services.length}
            </div>
            <p className="text-xs text-muted-foreground">
              All critical services running
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(health.services.reduce((acc, s) => acc + s.responseTime, 0) / health.services.length)}ms
            </div>
            <p className="text-xs text-muted-foreground">
              Across all services
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total CPU Usage</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(health.services.reduce((acc, s) => acc + s.cpu, 0))}%
            </div>
            <p className="text-xs text-muted-foreground">
              Combined across services
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Service Status */}
      <Card>
        <CardHeader>
          <CardTitle>Service Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {health.services.map((service) => (
              <motion.div
                key={service.name}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
              >
                <div className="flex items-center gap-4">
                  {getStatusIcon(service.status)}
                  <div>
                    <h4 className="font-medium">{service.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      Uptime: {service.uptime}% | Response: {service.responseTime}ms
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <div className="text-sm font-medium">CPU: {service.cpu.toFixed(1)}%</div>
                    <div className="text-sm text-muted-foreground">
                      Memory: {formatBytes(service.memory * 1024 * 1024)}
                    </div>
                  </div>
                  {getStatusBadge(service.status)}
                </div>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>System Resources</CardTitle>
            <div className="flex gap-2">
              {(['1h', '24h', '7d'] as const).map((range) => (
                <Button
                  key={range}
                  variant={timeRange === range ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTimeRange(range)}
                >
                  {range}
                </Button>
              ))}
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">CPU Usage</span>
                <span className="text-sm text-muted-foreground">
                  {metrics[metrics.length - 1]?.cpu.toFixed(1)}%
                </span>
              </div>
              <Progress value={metrics[metrics.length - 1]?.cpu || 0} className="h-2" />
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Memory Usage</span>
                <span className="text-sm text-muted-foreground">
                  {metrics[metrics.length - 1]?.memory.toFixed(1)}%
                </span>
              </div>
              <Progress value={metrics[metrics.length - 1]?.memory || 0} className="h-2" />
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">Disk Usage</span>
                <span className="text-sm text-muted-foreground">
                  {metrics[metrics.length - 1]?.disk.toFixed(1)}%
                </span>
              </div>
              <Progress value={metrics[metrics.length - 1]?.disk || 0} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Network & Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {metrics[metrics.length - 1]?.requestsPerSecond.toFixed(0)}
                </div>
                <div className="text-sm text-muted-foreground">Requests/sec</div>
              </div>

              <div className="text-center p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {metrics[metrics.length - 1]?.responseTime.toFixed(0)}ms
                </div>
                <div className="text-sm text-muted-foreground">Avg Response</div>
              </div>

              <div className="text-center p-4 bg-purple-50 dark:bg-purple-950/20 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {formatBytes(metrics[metrics.length - 1]?.networkIn || 0)}
                </div>
                <div className="text-sm text-muted-foreground">Network In</div>
              </div>

              <div className="text-center p-4 bg-orange-50 dark:bg-orange-950/20 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {metrics[metrics.length - 1]?.errorRate.toFixed(2)}%
                </div>
                <div className="text-sm text-muted-foreground">Error Rate</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Logs */}
      <Card>
        <CardHeader>
          <CardTitle>Recent System Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {logs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className={`flex items-start gap-3 p-3 rounded-lg ${
                  log.level === 'error'
                    ? 'bg-red-50 dark:bg-red-950/20'
                    : log.level === 'warning'
                    ? 'bg-yellow-50 dark:bg-yellow-950/20'
                    : 'bg-blue-50 dark:bg-blue-950/20'
                }`}
              >
                {getLogLevelIcon(log.level)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium">{log.service}</span>
                    <Badge variant="outline" className="text-xs">
                      {log.level}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {log.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm">{log.message}</p>
                  {log.details && (
                    <p className="text-xs text-muted-foreground mt-1">{log.details}</p>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
