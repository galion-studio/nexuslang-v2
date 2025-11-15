'use client'

import { useState, useEffect } from 'react'
import { Plus, Play, Pause, Trash2, Edit, Code, Clock, CheckCircle, AlertTriangle, FileText } from 'lucide-react'
// Shared components removed for simplified deployment

interface NexusTask {
  id: string
  title: string
  description: string
  priority: string
  status: string
  assigned_agent: string | null
  dependencies: string[]
  created_at: string
  updated_at: string
  deadline: string | null
  tags: string[]
  nexus_code: string | null
  compiled_binary_size: number | null
  execution_result: any
  cost_estimate: number
  actual_cost: number
  metadata: any
}

interface CreateTaskData {
  title: string
  description: string
  priority: 'low' | 'normal' | 'high' | 'critical'
  dependencies: string[]
  deadline: string
  tags: string[]
  nexus_code: string
  cost_estimate: number
}

export function TaskManager({ className = '' }: { className?: string }) {
  const [tasks, setTasks] = useState<NexusTask[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [creating, setCreating] = useState(false)
  const [formData, setFormData] = useState<CreateTaskData>({
    title: '',
    description: '',
    priority: 'normal',
    dependencies: [],
    deadline: '',
    tags: [],
    nexus_code: '',
    cost_estimate: 0,
  })

  useEffect(() => {
    loadTasks()
  }, [])

  const loadTasks = async () => {
    try {
      const response = await fetch('/api/v2/enhanced-agents/tasks')
      if (response.ok) {
        const data = await response.json()
        setTasks(data)
      }
    } catch (error) {
      console.error('Failed to load tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const createTask = async () => {
    if (!formData.title || !formData.description) return

    setCreating(true)
    try {
      const response = await fetch('/api/v2/enhanced-agents/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        await loadTasks()
        setShowCreateForm(false)
        setFormData({
          title: '',
          description: '',
          priority: 'normal',
          dependencies: [],
          deadline: '',
          tags: [],
          nexus_code: '',
          cost_estimate: 0,
        })
      }
    } catch (error) {
      console.error('Failed to create task:', error)
    } finally {
      setCreating(false)
    }
  }

  const deleteTask = async (taskId: string) => {
    try {
      const response = await fetch(`/api/v2/enhanced-agents/tasks/${taskId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        await loadTasks()
      }
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'running':
        return <Play className="w-4 h-4 text-blue-500" />
      case 'failed':
        return <AlertTriangle className="w-4 h-4 text-red-500" />
      case 'pending':
        return <Clock className="w-4 h-4 text-amber-500" />
      default:
        return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'normal':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'low':
        return 'bg-gray-100 text-gray-800 border-gray-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (loading) {
    return (
      <div className={`p-4 ${className}`}>
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-neutral-300 rounded w-1/3"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-24 bg-neutral-300 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`p-4 space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-neutral-900">NexusLang Task Manager</h3>
          <p className="text-sm text-neutral-600">Create and manage AI agent tasks</p>
        </div>
        <Button
          onClick={() => setShowCreateForm(true)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          New Task
        </Button>
      </div>

      {/* Create Task Form */}
      {showCreateForm && (
        <div className="bg-white p-6 rounded-lg border border-neutral-200 shadow-sm">
          <h4 className="text-md font-semibold text-neutral-900 mb-4">Create New Task</h4>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Task title"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">
                  Priority
                </label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                Description *
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Task description"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-1">
                NexusLang Code (Optional)
              </label>
              <textarea
                value={formData.nexus_code}
                onChange={(e) => setFormData({ ...formData, nexus_code: e.target.value })}
                rows={6}
                className="w-full px-3 py-2 border border-neutral-300 rounded-md font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="// Write your NexusLang code here"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">
                  Deadline (Optional)
                </label>
                <input
                  type="datetime-local"
                  value={formData.deadline}
                  onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-1">
                  Cost Estimate
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.cost_estimate}
                  onChange={(e) => setFormData({ ...formData, cost_estimate: parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <Button
                variant="ghost"
                onClick={() => setShowCreateForm(false)}
              >
                Cancel
              </Button>
              <Button
                onClick={createTask}
                disabled={creating || !formData.title || !formData.description}
                leftIcon={creating ? <Loading size="sm" /> : undefined}
              >
                {creating ? 'Creating...' : 'Create Task'}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Tasks List */}
      <div className="space-y-4">
        {tasks.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-neutral-900 mb-2">No tasks yet</h4>
            <p className="text-neutral-600 mb-4">Create your first NexusLang task to get started</p>
            <Button onClick={() => setShowCreateForm(true)}>
              Create First Task
            </Button>
          </div>
        ) : (
          tasks.map((task) => (
            <div key={task.id} className="bg-white p-6 rounded-lg border border-neutral-200 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start space-x-3">
                  {getStatusIcon(task.status)}
                  <div>
                    <h4 className="text-lg font-semibold text-neutral-900">{task.title}</h4>
                    <p className="text-neutral-600 mt-1">{task.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(task.priority)}`}>
                    {task.priority}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteTask(task.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <div className="text-sm text-neutral-600">Status</div>
                  <div className="font-medium capitalize">{task.status}</div>
                </div>
                <div>
                  <div className="text-sm text-neutral-600">Assigned Agent</div>
                  <div className="font-medium">{task.assigned_agent || 'Unassigned'}</div>
                </div>
                <div>
                  <div className="text-sm text-neutral-600">Created</div>
                  <div className="font-medium">{new Date(task.created_at).toLocaleDateString()}</div>
                </div>
              </div>

              {task.nexus_code && (
                <div className="mb-4">
                  <div className="text-sm text-neutral-600 mb-2">NexusLang Code</div>
                  <div className="bg-neutral-50 p-3 rounded-md">
                    <pre className="text-xs font-mono text-neutral-800 whitespace-pre-wrap">
                      {task.nexus_code.length > 200 ? `${task.nexus_code.substring(0, 200)}...` : task.nexus_code}
                    </pre>
                  </div>
                </div>
              )}

              {task.tags.length > 0 && (
                <div className="mb-4">
                  <div className="text-sm text-neutral-600 mb-2">Tags</div>
                  <div className="flex flex-wrap gap-1">
                    {task.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-neutral-100 text-neutral-700 text-xs rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between pt-4 border-t border-neutral-100">
                <div className="flex items-center space-x-4 text-sm text-neutral-600">
                  <span>Cost: ${task.actual_cost > 0 ? task.actual_cost.toFixed(2) : task.cost_estimate.toFixed(2)}</span>
                  {task.compiled_binary_size && (
                    <span>Binary: {(task.compiled_binary_size / 1024).toFixed(1)} KB</span>
                  )}
                </div>
                <div className="text-xs text-neutral-500">
                  Updated {new Date(task.updated_at).toLocaleString()}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
