'use client'

import { useState, useEffect, useRef } from 'react'
import { Activity, Zap, AlertTriangle, CheckCircle, Clock, Users, Cpu } from 'lucide-react'

interface MonitoringData {
  active_executions: number
  active_clients: number
  total_alerts: number
  uptime: number
  cpu_usage: number
  memory_usage: number
  recent_events: Array<{
    id: string
    type: string
    message: string
    timestamp: string
    severity: 'info' | 'warning' | 'error' | 'success'
  }>
}

export default function RealtimeMonitor() {
  const [data, setData] = useState<MonitoringData>({
    active_executions: 0,
    active_clients: 0,
    total_alerts: 0,
    uptime: 0,
    cpu_usage: 0,
    memory_usage: 0,
    recent_events: []
  })

  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Connect to WebSocket for real-time monitoring
    const connectWebSocket = () => {
      try {
        // In a real implementation, this would connect to your backend WebSocket
        // wsRef.current = new WebSocket('ws://localhost:8010/ws/agents/monitor')

        // For demo purposes, simulate real-time updates
        const interval = setInterval(() => {
          setData(prev => ({
            ...prev,
            active_executions: Math.floor(Math.random() * 10),
            active_clients: Math.floor(Math.random() * 20) + 5,
            cpu_usage: Math.floor(Math.random() * 30) + 20,
            memory_usage: Math.floor(Math.random() * 40) + 30,
            recent_events: [
              {
                id: Date.now().toString(),
                type: 'task_started',
                message: 'New autonomous task initiated',
                timestamp: new Date().toISOString(),
                severity: 'info'
              },
              ...prev.recent_events.slice(0, 9) // Keep only last 10 events
            ]
          }))
        }, 3000)

        setIsConnected(true)

        return () => clearInterval(interval)
      } catch (error) {
        console.error('WebSocket connection failed:', error)
        setIsConnected(false)
      }
    }

    connectWebSocket()

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'error': return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case 'success': return <CheckCircle className="h-4 w-4 text-green-500" />
      default: return <Activity className="h-4 w-4 text-blue-500" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error': return 'text-red-700 dark:text-red-400'
      case 'warning': return 'text-yellow-700 dark:text-yellow-400'
      case 'success': return 'text-green-700 dark:text-green-400'
      default: return 'text-blue-700 dark:text-blue-400'
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
          <Activity className="h-5 w-5 mr-2 text-blue-500" />
          Real-time Monitoring
        </h2>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-full mb-2">
            <Zap className="h-6 w-6 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">{data.active_executions}</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Active Tasks</div>
        </div>

        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full mb-2">
            <Users className="h-6 w-6 text-green-600 dark:text-green-400" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">{data.active_clients}</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Active Clients</div>
        </div>

        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-yellow-100 dark:bg-yellow-900 rounded-full mb-2">
            <AlertTriangle className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">{data.total_alerts}</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Total Alerts</div>
        </div>

        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-full mb-2">
            <Clock className="h-6 w-6 text-purple-600 dark:text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">{Math.floor(data.uptime / 3600)}h</div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Uptime</div>
        </div>
      </div>

      {/* System Resources */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">System Resources</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
              <span>CPU Usage</span>
              <span>{data.cpu_usage}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${data.cpu_usage}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
              <span>Memory Usage</span>
              <span>{data.memory_usage}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
              <div
                className="bg-green-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${data.memory_usage}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Events */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Recent Events</h3>
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {data.recent_events.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No recent events</p>
            </div>
          ) : (
            data.recent_events.map((event) => (
              <div key={event.id} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                {getSeverityIcon(event.severity)}
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium ${getSeverityColor(event.severity)}`}>
                    {event.message}
                  </p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {event.type.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-400 dark:text-gray-500">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Connection Status */}
      {!isConnected && (
        <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="h-4 w-4 text-red-500 mr-2" />
            <span className="text-sm text-red-700 dark:text-red-400">
              Real-time monitoring disconnected. Attempting to reconnect...
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
