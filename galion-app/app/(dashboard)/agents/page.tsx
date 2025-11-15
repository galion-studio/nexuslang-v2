'use client'

import { useState, useEffect } from 'react'
import { Bot, Play, Pause, Square, Eye, Users, AlertTriangle, CheckCircle, Clock, Zap, MessageSquare, Activity } from 'lucide-react'
import Link from 'next/link'
import RealtimeMonitor from '../../../components/agents/RealtimeMonitor'
import TaskExecutor from '../../../components/agents/TaskExecutor'

// Types
interface Task {
  id: string
  prompt: string
  status: 'running' | 'completed' | 'failed' | 'pending'
  progress: number
  started_at?: string
  completed_at?: string
  result?: any
  error?: string
}

interface Agent {
  id: string
  name: string
  type: string
  status: 'active' | 'idle' | 'busy'
  tasks_completed: number
  specialization: string
}

interface Approval {
  id: string
  task_id: string
  type: string
  title: string
  description: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  created_at: string
}

export default function AutonomousAgentsPage() {
  const [activeTab, setActiveTab] = useState('tasks')
  const [tasks, setTasks] = useState<Task[]>([])
  const [agents, setAgents] = useState<Agent[]>([])
  const [approvals, setApprovals] = useState<Approval[]>([])
  const [newTaskPrompt, setNewTaskPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Mock data for demonstration
  useEffect(() => {
    setTasks([
      {
        id: 'task-1',
        prompt: 'Build a complete user authentication system with login, registration, and password reset',
        status: 'running',
        progress: 65,
        started_at: new Date().toISOString()
      },
      {
        id: 'task-2',
        prompt: 'Analyze customer feedback data and generate insights report',
        status: 'completed',
        progress: 100,
        started_at: new Date(Date.now() - 3600000).toISOString(),
        completed_at: new Date().toISOString(),
        result: { insights: 15, recommendations: 8 }
      }
    ])

    setAgents([
      {
        id: 'agent-1',
        name: 'Code Architect',
        type: 'engineering',
        status: 'active',
        tasks_completed: 45,
        specialization: 'Full-stack development'
      },
      {
        id: 'agent-2',
        name: 'Data Analyst',
        type: 'analytics',
        status: 'busy',
        tasks_completed: 32,
        specialization: 'Data science & ML'
      },
      {
        id: 'agent-3',
        name: 'Project Manager',
        type: 'management',
        status: 'idle',
        tasks_completed: 28,
        specialization: 'Agile & Scrum'
      }
    ])

    setApprovals([
      {
        id: 'approval-1',
        task_id: 'task-1',
        type: 'security',
        title: 'Database Schema Changes',
        description: 'The task requires creating new database tables for user authentication. This involves schema modifications.',
        priority: 'high',
        created_at: new Date().toISOString()
      }
    ])
  }, [])

  const executeTask = async () => {
    if (!newTaskPrompt.trim()) return

    setIsLoading(true)
    try {
      // In a real implementation, this would call the backend API
      const response = await fetch('/api/v1/agents/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: newTaskPrompt,
          require_approval: false,
          priority: 'normal'
        })
      })

      if (response.ok) {
        const result = await response.json()
        const newTask: Task = {
          id: result.task_id,
          prompt: newTaskPrompt,
          status: 'running',
          progress: 0,
          started_at: new Date().toISOString()
        }
        setTasks(prev => [newTask, ...prev])
        setNewTaskPrompt('')
      }
    } catch (error) {
      console.error('Failed to execute task:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-blue-400'
      case 'completed': return 'text-green-400'
      case 'failed': return 'text-red-400'
      case 'pending': return 'text-yellow-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Clock className="h-4 w-4" />
      case 'completed': return <CheckCircle className="h-4 w-4" />
      case 'failed': return <AlertTriangle className="h-4 w-4" />
      case 'pending': return <Clock className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
              <Bot className="h-8 w-8 mr-3 text-blue-500" />
              Autonomous Agents
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Manus-like autonomous agent system for intelligent task execution
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-500">{agents.filter(a => a.status === 'active').length}</div>
              <div className="text-sm text-gray-500">Active Agents</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-500">{tasks.filter(t => t.status === 'running').length}</div>
              <div className="text-sm text-gray-500">Running Tasks</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-500">{approvals.length}</div>
              <div className="text-sm text-gray-500">Pending Approvals</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('tasks')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'tasks'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
              }`}
            >
              <Play className="h-4 w-4 inline mr-2" />
              Task Execution
            </button>
            <button
              onClick={() => setActiveTab('agents')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'agents'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
              }`}
            >
              <Bot className="h-4 w-4 inline mr-2" />
              Agent Management
            </button>
            <button
              onClick={() => setActiveTab('monitoring')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'monitoring'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
              }`}
            >
              <Activity className="h-4 w-4 inline mr-2" />
              Real-time Monitoring
            </button>
            <button
              onClick={() => setActiveTab('approvals')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'approvals'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
              }`}
            >
              <Eye className="h-4 w-4 inline mr-2" />
              Human Approvals
            </button>
            <button
              onClick={() => setActiveTab('collaboration')}
              className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'collaboration'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
              }`}
            >
              <Users className="h-4 w-4 inline mr-2" />
              Collaboration
            </button>
          </nav>
        </div>

        <div className="p-6">
          {/* Task Execution Tab */}
          {activeTab === 'tasks' && (
            <div className="space-y-6">
              <TaskExecutor
                onTaskComplete={(task) => {
                  console.log('Task completed:', task)
                  // Update local task list
                }}
                onTaskError={(error) => {
                  console.error('Task error:', error)
                }}
              />

              {/* Task History */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Task History
                </h3>
                <div className="space-y-4">
                  {tasks.map((task) => (
                    <div key={task.id} className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(task.status)}
                          <span className={`font-medium ${getStatusColor(task.status)}`}>
                            {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                          </span>
                        </div>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          ID: {task.id}
                        </span>
                      </div>

                      <p className="text-gray-900 dark:text-white mb-3">{task.prompt}</p>

                      {task.status === 'running' && (
                        <div className="mb-3">
                          <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                            <span>Progress</span>
                            <span>{task.progress}%</span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${task.progress}%` }}
                            ></div>
                          </div>
                        </div>
                      )}

                      <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400">
                        <span>
                          Started: {task.started_at ? new Date(task.started_at).toLocaleString() : 'N/A'}
                        </span>
                        {task.completed_at && (
                          <span>
                            Completed: {new Date(task.completed_at).toLocaleString()}
                          </span>
                        )}
                      </div>

                      {task.error && (
                        <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                          <p className="text-red-700 dark:text-red-400 text-sm">{task.error}</p>
                        </div>
                      )}

                      {task.result && (
                        <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                          <p className="text-green-700 dark:text-green-400 text-sm">
                            Task completed successfully. Results: {JSON.stringify(task.result)}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Agent Management Tab */}
          {activeTab === 'agents' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {agents.map((agent) => (
                  <div key={agent.id} className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                          <Bot className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white">{agent.name}</h3>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{agent.type}</p>
                        </div>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        agent.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                        agent.status === 'busy' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                        'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                      }`}>
                        {agent.status}
                      </span>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">Tasks Completed</span>
                        <span className="font-medium text-gray-900 dark:text-white">{agent.tasks_completed}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">Specialization</span>
                        <span className="font-medium text-gray-900 dark:text-white">{agent.specialization}</span>
                      </div>
                    </div>

                    <div className="mt-4 flex space-x-2">
                      <button className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors">
                        Configure
                      </button>
                      <button className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 text-sm rounded-lg transition-colors">
                        Monitor
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Agent Marketplace
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Discover and deploy specialized agents for your use cases.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 transition-colors cursor-pointer">
                    <h4 className="font-medium text-gray-900 dark:text-white">Code Review Agent</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Automated code quality analysis and suggestions</p>
                  </div>
                  <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 transition-colors cursor-pointer">
                    <h4 className="font-medium text-gray-900 dark:text-white">Data Science Agent</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Statistical analysis and machine learning workflows</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Real-time Monitoring Tab */}
          {activeTab === 'monitoring' && (
            <RealtimeMonitor />
          )}

          {/* Human Approvals Tab */}
          {activeTab === 'approvals' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Pending Approvals
                </h3>

                {approvals.length === 0 ? (
                  <div className="text-center py-12">
                    <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                    <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">All Clear!</h4>
                    <p className="text-gray-600 dark:text-gray-400">No pending approvals at this time.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {approvals.map((approval) => (
                      <div key={approval.id} className="bg-white dark:bg-gray-900 border border-orange-200 dark:border-orange-800 rounded-lg p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-start space-x-3">
                            <AlertTriangle className="h-5 w-5 text-orange-500 mt-0.5" />
                            <div>
                              <h4 className="font-medium text-gray-900 dark:text-white">{approval.title}</h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{approval.description}</p>
                              <div className="flex items-center space-x-4 mt-2">
                                <span className="text-xs text-gray-500 dark:text-gray-400">
                                  Task: {approval.task_id}
                                </span>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  approval.priority === 'urgent' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                                  approval.priority === 'high' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' :
                                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                                }`}>
                                  {approval.priority}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="flex space-x-3">
                          <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition-colors">
                            Approve
                          </button>
                          <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors">
                            Deny
                          </button>
                          <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 text-sm rounded-lg transition-colors">
                            Modify
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Collaboration Tab */}
          {activeTab === 'collaboration' && (
            <div className="space-y-6">
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Start Collaboration Session
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <input
                    type="text"
                    placeholder="Session name"
                    className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white"
                  />
                  <input
                    type="text"
                    placeholder="Goal or objective"
                    className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white"
                  />
                </div>
                <button className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center">
                  <Users className="h-4 w-4 mr-2" />
                  Create Session
                </button>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Active Sessions
                </h3>
                <div className="text-center py-12">
                  <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No Active Sessions</h4>
                  <p className="text-gray-600 dark:text-gray-400">Create a collaboration session to get started.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
