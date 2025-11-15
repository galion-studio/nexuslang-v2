'use client'

import { useState, useEffect } from 'react'
import {
  Users,
  Activity,
  AlertTriangle,
  Settings,
  Play,
  Pause,
  RefreshCw,
  Shield,
  Database,
  Zap,
  BarChart3,
  Clock,
  DollarSign,
  TrendingUp,
  Server,
  HardDrive,
  Wifi,
  Mic,
  Bot,
  CheckCircle,
  XCircle,
  AlertCircle,
  UserCheck,
  UserX,
  Key,
  Automation
} from 'lucide-react'
// Shared components removed for simplified deployment

interface AdminMetrics {
  total_users: number
  active_users_24h: number
  active_users_7d: number
  total_credits_used: number
  average_session_time: number
  system_health_score: number
  active_agents: number
  pending_tasks: number
  completed_tasks_24h: number
  failed_tasks_24h: number
  api_response_time_avg: number
  error_rate_24h: number
  voice_sessions_24h: number
  storage_usage_gb: number
  bandwidth_usage_gb: number
}

interface AdminDashboardData {
  metrics: AdminMetrics
  user_stats: any
  system_health: any
  agent_stats: any
  voice_stats: any
  recent_activity: any[]
  alerts: any[]
}

interface AutomationTask {
  id: string
  name: string
  description: string
  schedule: string
  enabled: bool
  last_run: string | null
  next_run: string | null
  success_count: number
  failure_count: number
}

export function AdminDashboard({ className = '' }: { className?: string }) {
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(null)
  const [automationTasks, setAutomationTasks] = useState<AutomationTask[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'system' | 'agents' | 'automation'>('overview')
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    loadDashboardData()
    loadAutomationTasks()
  }, [])

  const loadDashboardData = async () => {
    try {
      const response = await fetch('/api/v2/admin/dashboard')
      if (response.ok) {
        const data = await response.json()
        setDashboardData(data)
      } else {
        console.error('Failed to load dashboard data')
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const loadAutomationTasks = async () => {
    try {
      const response = await fetch('/api/v2/admin/automation/tasks')
      if (response.ok) {
        const data = await response.json()
        setAutomationTasks(data)
      }
    } catch (error) {
      console.error('Failed to load automation tasks:', error)
    }
  }

  const refreshData = async () => {
    setRefreshing(true)
    await Promise.all([loadDashboardData(), loadAutomationTasks()])
  }

  const runAutomationTask = async (taskId: string) => {
    try {
      const response = await fetch(`/api/v2/admin/automation/tasks/${taskId}/run`, {
        method: 'POST',
      })
      if (response.ok) {
        await loadAutomationTasks() // Refresh the tasks list
      }
    } catch (error) {
      console.error('Failed to run automation task:', error)
    }
  }

  const toggleAutomationTask = async (taskId: string, enabled: boolean) => {
    try {
      const response = await fetch(`/api/v2/admin/automation/tasks/${taskId}/toggle?enabled=${enabled}`, {
        method: 'POST',
      })
      if (response.ok) {
        await loadAutomationTasks()
      }
    } catch (error) {
      console.error('Failed to toggle automation task:', error)
    }
  }

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100'
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100'
      case 'error':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  if (loading) {
    return (
      <div className={`p-6 ${className}`}>
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-neutral-300 rounded w-1/4"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-24 bg-neutral-300 rounded"></div>
            ))}
          </div>
          <div className="h-64 bg-neutral-300 rounded"></div>
        </div>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className={`p-6 text-center ${className}`}>
        <p className="text-neutral-500">Failed to load admin dashboard data</p>
        <Button onClick={refreshData} className="mt-4">
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      </div>
    )
  }

  const { metrics, user_stats, system_health, agent_stats, voice_stats, recent_activity, alerts } = dashboardData

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'system', label: 'System', icon: Server },
    { id: 'agents', label: 'Agents', icon: Bot },
    { id: 'automation', label: 'Automation', icon: Automation },
  ]

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">Admin Dashboard</h1>
          <p className="text-neutral-600">Comprehensive system monitoring and management</p>
        </div>
        <Button
          onClick={refreshData}
          disabled={refreshing}
          variant="outline"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </Button>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5 mr-3" />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-800">System Alerts</h3>
              <div className="mt-2 space-y-1">
                {alerts.map((alert, index) => (
                  <div key={index} className="text-sm text-red-700">
                    • {alert.title}: {alert.description}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-neutral-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => {
            const IconComponent = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300'
                }`}
              >
                <IconComponent className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="p-4">
                <div className="flex items-center space-x-2">
                  <Users className="w-5 h-5 text-blue-500" />
                  <span className="text-sm font-medium text-neutral-600">Total Users</span>
                </div>
                <div className="mt-2">
                  <div className="text-2xl font-bold text-neutral-900">{metrics.total_users.toLocaleString()}</div>
                  <div className="text-xs text-neutral-500">
                    {user_stats.active_users_24h} active today
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <div className="flex items-center space-x-2">
                  <Activity className="w-5 h-5 text-green-500" />
                  <span className="text-sm font-medium text-neutral-600">System Health</span>
                </div>
                <div className="mt-2">
                  <div className="text-2xl font-bold text-neutral-900">{metrics.system_health_score.toFixed(1)}%</div>
                  <div className="text-xs text-neutral-500">Overall score</div>
                </div>
              </Card>

              <Card className="p-4">
                <div className="flex items-center space-x-2">
                  <Bot className="w-5 h-5 text-purple-500" />
                  <span className="text-sm font-medium text-neutral-600">Active Agents</span>
                </div>
                <div className="mt-2">
                  <div className="text-2xl font-bold text-neutral-900">{metrics.active_agents}</div>
                  <div className="text-xs text-neutral-500">
                    {agent_stats.total_tasks} total tasks
                  </div>
                </div>
              </Card>

              <Card className="p-4">
                <div className="flex items-center space-x-2">
                  <Mic className="w-5 h-5 text-indigo-500" />
                  <span className="text-sm font-medium text-neutral-600">Voice Sessions</span>
                </div>
                <div className="mt-2">
                  <div className="text-2xl font-bold text-neutral-900">{metrics.voice_sessions_24h}</div>
                  <div className="text-xs text-neutral-500">Last 24 hours</div>
                </div>
              </Card>
            </div>

            {/* System Health Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Database</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-neutral-600">Status</span>
                    <span className={`px-2 py-1 text-xs rounded-full ${getHealthStatusColor(system_health.database.status)}`}>
                      {system_health.database.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-neutral-600">Response Time</span>
                    <span className="text-sm font-medium">{system_health.database.response_time_ms.toFixed(1)}ms</span>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">API</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-neutral-600">Status</span>
                    <span className={`px-2 py-1 text-xs rounded-full ${getHealthStatusColor(system_health.api.status)}`}>
                      {system_health.api.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-neutral-600">Uptime</span>
                    <span className="text-sm font-medium">{system_health.api.uptime_percent}%</span>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Agents</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-neutral-600">Status</span>
                    <span className={`px-2 py-1 text-xs rounded-full ${getHealthStatusColor(system_health.agents.status)}`}>
                      {system_health.agents.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-neutral-600">Active Count</span>
                    <span className="text-sm font-medium">{system_health.agents.active_count}</span>
                  </div>
                </div>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">Recent Activity</h3>
              <div className="space-y-3">
                {recent_activity.slice(0, 10).map((activity, index) => (
                  <div key={index} className="flex items-center space-x-3 py-2 border-b border-neutral-100 last:border-b-0">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm text-neutral-900">{activity.description}</p>
                      <p className="text-xs text-neutral-500">
                        {new Date(activity.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">User Statistics</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Total Users</span>
                    <span className="text-sm font-medium">{user_stats.total_users}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Verified Users</span>
                    <span className="text-sm font-medium">{user_stats.verified_users}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Verification Rate</span>
                    <span className="text-sm font-medium">{user_stats.verification_rate.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">New Users (30d)</span>
                    <span className="text-sm font-medium">{user_stats.new_users_30d}</span>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Subscription Tiers</h3>
                <div className="space-y-3">
                  {Object.entries(user_stats.subscription_tiers).map(([tier, count]) => (
                    <div key={tier} className="flex justify-between">
                      <span className="text-sm text-neutral-600 capitalize">{tier}</span>
                      <span className="text-sm font-medium">{count}</span>
                    </div>
                  ))}
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Quick Actions</h3>
                <div className="space-y-2">
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <UserCheck className="w-4 h-4 mr-2" />
                    View All Users
                  </Button>
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <UserX className="w-4 h-4 mr-2" />
                    Manage Inactive Users
                  </Button>
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <Key className="w-4 h-4 mr-2" />
                    Reset User Passwords
                  </Button>
                </div>
              </Card>
            </div>
          </div>
        )}

        {activeTab === 'system' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Performance Metrics</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">API Response Time</span>
                    <span className="text-sm font-medium">{metrics.api_response_time_avg.toFixed(1)}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Error Rate (24h)</span>
                    <span className="text-sm font-medium">{(metrics.error_rate_24h * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Storage Usage</span>
                    <span className="text-sm font-medium">{metrics.storage_usage_gb.toFixed(1)} GB</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Bandwidth Usage</span>
                    <span className="text-sm font-medium">{metrics.bandwidth_usage_gb.toFixed(1)} GB</span>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">System Actions</h3>
                <div className="space-y-2">
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <Database className="w-4 h-4 mr-2" />
                    Trigger Backup
                  </Button>
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <Shield className="w-4 h-4 mr-2" />
                    Run Security Audit
                  </Button>
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <Zap className="w-4 h-4 mr-2" />
                    Optimize Performance
                  </Button>
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <Server className="w-4 h-4 mr-2" />
                    Health Check
                  </Button>
                </div>
              </Card>
            </div>
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Agent Statistics</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Total Agents</span>
                    <span className="text-sm font-medium">{agent_stats.total_agents}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Active Agents</span>
                    <span className="text-sm font-medium">{agent_stats.active_agents}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Total Tasks</span>
                    <span className="text-sm font-medium">{agent_stats.total_tasks}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Completed Tasks</span>
                    <span className="text-sm font-medium">{agent_stats.completed_tasks}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Avg Completion Time</span>
                    <span className="text-sm font-medium">{agent_stats.average_completion_time.toFixed(1)}s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Total Cost</span>
                    <span className="text-sm font-medium">${agent_stats.total_cost.toFixed(2)}</span>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Task Status</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Pending Tasks</span>
                    <span className="text-sm font-medium">{metrics.pending_tasks}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Completed (24h)</span>
                    <span className="text-sm font-medium">{metrics.completed_tasks_24h}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-neutral-600">Failed (24h)</span>
                    <span className="text-sm font-medium">{metrics.failed_tasks_24h}</span>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="text-lg font-semibold text-neutral-900 mb-4">Agent Controls</h3>
                <div className="space-y-2">
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <Play className="w-4 h-4 mr-2" />
                    Start All Agents
                  </Button>
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <Pause className="w-4 h-4 mr-2" />
                    Stop All Agents
                  </Button>
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Restart Agents
                  </Button>
                  <Button variant="outline" size="sm" className="w-full justify-start">
                    <BarChart3 className="w-4 h-4 mr-2" />
                    View Agent Logs
                  </Button>
                </div>
              </Card>
            </div>
          </div>
        )}

        {activeTab === 'automation' && (
          <div className="space-y-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4">Automation Tasks</h3>
              <div className="space-y-4">
                {automationTasks.map((task) => (
                  <div key={task.id} className="border border-neutral-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="font-medium text-neutral-900">{task.name}</h4>
                        <p className="text-sm text-neutral-600">{task.description}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          onClick={() => runAutomationTask(task.id)}
                          leftIcon={<Play className="w-4 h-4" />}
                        >
                          Run Now
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleAutomationTask(task.id, !task.enabled)}
                          leftIcon={task.enabled ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        >
                          {task.enabled ? 'Disable' : 'Enable'}
                        </Button>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-neutral-600">Schedule:</span>
                        <div className="font-medium capitalize">{task.schedule}</div>
                      </div>
                      <div>
                        <span className="text-neutral-600">Last Run:</span>
                        <div className="font-medium">
                          {task.last_run ? new Date(task.last_run).toLocaleString() : 'Never'}
                        </div>
                      </div>
                      <div>
                        <span className="text-neutral-600">Success:</span>
                        <div className="font-medium text-green-600">{task.success_count}</div>
                      </div>
                      <div>
                        <span className="text-neutral-600">Failed:</span>
                        <div className="font-medium text-red-600">{task.failure_count}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
