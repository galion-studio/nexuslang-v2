'use client'

import { useState, useEffect } from 'react'
import { Activity, Users, Cpu, Zap, AlertTriangle, CheckCircle, Clock, DollarSign, RefreshCw, Play, Pause } from 'lucide-react'
// Shared components removed for simplified deployment

interface AgentMetrics {
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
  average_completion_time: number
  total_cost: number
  active_agents: number
}

interface AgentInfo {
  role: string
  workload: number
  is_active: boolean
  performance_score: number
  capabilities: string[]
}

interface SystemStatus {
  metrics: AgentMetrics
  agents: Record<string, AgentInfo>
  active_tasks: number
  pending_tasks: number
  completed_tasks: number
}

export function AgentMonitor({ className = '' }: { className?: string }) {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    loadSystemStatus()
    if (autoRefresh) {
      const interval = setInterval(loadSystemStatus, 5000) // Refresh every 5 seconds
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const loadSystemStatus = async () => {
    try {
      const response = await fetch('/api/v2/status')
      if (response.ok) {
        const data = await response.json()
        setSystemStatus(data)
      } else {
        console.error('Failed to load system status')
      }
    } catch (error) {
      console.error('Failed to load agent data:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh)
  }


  if (loading) {
    return (
      <div className={`p-4 space-y-4 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-neutral-300 rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-20 bg-neutral-300 rounded"></div>
            ))}
          </div>
          <div className="space-y-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-12 bg-neutral-300 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!systemStatus) {
    return (
      <div className={`p-4 text-center ${className}`}>
        <p className="text-neutral-500">Failed to load agent monitoring data</p>
        <Button onClick={loadSystemStatus} className="mt-2">
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      </div>
    )
  }

  const { metrics, agents, active_tasks, pending_tasks, completed_tasks } = systemStatus

  return (
    <div className={`p-4 space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-neutral-900">Enhanced Agent Monitor</h3>
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleAutoRefresh}
            className={autoRefresh ? 'text-green-600' : 'text-neutral-500'}
          >
            {autoRefresh ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </Button>
          <Button variant="ghost" size="sm" onClick={loadSystemStatus}>
            <RefreshCw className="w-4 h-4" />
          </Button>
          <div className={`w-2 h-2 rounded-full ${autoRefresh ? 'bg-green-500 animate-pulse' : 'bg-neutral-400'}`}></div>
          <span className="text-sm text-neutral-600">{autoRefresh ? 'Live' : 'Paused'}</span>
        </div>
      </div>

      {/* Task Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-neutral-200 shadow-sm">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-blue-500" />
            <span className="text-sm font-medium text-neutral-600">Total Tasks</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-neutral-900">{metrics.total_tasks}</div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-neutral-200 shadow-sm">
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-amber-500" />
            <span className="text-sm font-medium text-neutral-600">Active Tasks</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-neutral-900">{active_tasks}</div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-neutral-200 shadow-sm">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <span className="text-sm font-medium text-neutral-600">Completed</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-neutral-900">{completed_tasks}</div>
            <div className="text-xs text-neutral-500">
              {metrics.total_tasks > 0 ? ((completed_tasks / metrics.total_tasks) * 100).toFixed(1) : 0}% success rate
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-neutral-200 shadow-sm">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <span className="text-sm font-medium text-neutral-600">Failed</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-neutral-900">{metrics.failed_tasks}</div>
          </div>
        </div>
      </div>

      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-neutral-200 shadow-sm">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-purple-500" />
            <span className="text-sm font-medium text-neutral-600">Avg Completion Time</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-neutral-900">{metrics.average_completion_time.toFixed(1)}s</div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-neutral-200 shadow-sm">
          <div className="flex items-center space-x-2">
            <DollarSign className="w-5 h-5 text-green-500" />
            <span className="text-sm font-medium text-neutral-600">Total Cost</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-neutral-900">${metrics.total_cost.toFixed(2)}</div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-neutral-200 shadow-sm">
          <div className="flex items-center space-x-2">
            <Users className="w-5 h-5 text-indigo-500" />
            <span className="text-sm font-medium text-neutral-600">Active Agents</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-neutral-900">{metrics.active_agents}</div>
            <div className="text-xs text-neutral-500">Specialized AI workers</div>
          </div>
        </div>
      </div>

      {/* Task Queue Status */}
      <div className="bg-white p-4 rounded-lg border border-neutral-200 shadow-sm">
        <h4 className="text-md font-semibold text-neutral-900 mb-3">Task Queue Status</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-amber-600">{pending_tasks}</div>
            <div className="text-sm text-neutral-600">Pending Tasks</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{active_tasks}</div>
            <div className="text-sm text-neutral-600">Running Tasks</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{completed_tasks}</div>
            <div className="text-sm text-neutral-600">Completed Tasks</div>
          </div>
        </div>
      </div>

      {/* Agent Status */}
      <div className="space-y-3">
        <h4 className="text-md font-semibold text-neutral-900">Agent Network Status</h4>
        <div className="space-y-2">
          {Object.entries(agents).map(([name, agent]) => (
            <div key={name} className="bg-white p-4 rounded-lg border border-neutral-200 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    agent.is_active ? (agent.workload > 0 ? 'bg-amber-500 animate-pulse' : 'bg-green-500') : 'bg-red-500'
                  }`} />
                  <div>
                    <div className="font-medium text-neutral-900">{name}</div>
                    <div className="text-sm text-neutral-600 capitalize">{agent.role.replace('_', ' ')}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-6 text-sm">
                  <div className="text-center">
                    <div className="font-medium text-neutral-900">{agent.workload}</div>
                    <div className="text-neutral-500">Workload</div>
                  </div>
                  <div className="text-center">
                    <div className="font-medium text-neutral-900">{(agent.performance_score * 100).toFixed(0)}%</div>
                    <div className="text-neutral-500">Performance</div>
                  </div>
                  <div className="text-center">
                    <div className={`font-medium ${agent.is_active ? 'text-green-600' : 'text-red-600'}`}>
                      {agent.is_active ? 'Active' : 'Inactive'}
                    </div>
                    <div className="text-neutral-500">Status</div>
                  </div>
                </div>
              </div>

              {/* Capabilities */}
              {agent.capabilities.length > 0 && (
                <div className="mt-3 pt-3 border-t border-neutral-100">
                  <div className="flex flex-wrap gap-1">
                    {agent.capabilities.slice(0, 5).map((capability, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-neutral-100 text-neutral-700 text-xs rounded-full"
                      >
                        {capability}
                      </span>
                    ))}
                    {agent.capabilities.length > 5 && (
                      <span className="px-2 py-1 bg-neutral-100 text-neutral-700 text-xs rounded-full">
                        +{agent.capabilities.length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default AgentMonitor
