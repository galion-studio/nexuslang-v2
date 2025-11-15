'use client'

import { useState, useEffect } from 'react'
import { Play, Pause, Square, RotateCcw, Settings, Eye, MessageSquare, AlertCircle } from 'lucide-react'

interface Task {
  id: string
  prompt: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused'
  progress: number
  current_step?: string
  total_steps?: number
  started_at?: string
  completed_at?: string
  result?: any
  error?: string
  steps?: Array<{
    id: string
    description: string
    status: 'pending' | 'running' | 'completed' | 'failed'
    started_at?: string
    completed_at?: string
    output?: any
  }>
}

interface TaskExecutorProps {
  onTaskComplete?: (task: Task) => void
  onTaskError?: (error: string) => void
}

export default function TaskExecutor({ onTaskComplete, onTaskError }: TaskExecutorProps) {
  const [currentTask, setCurrentTask] = useState<Task | null>(null)
  const [taskPrompt, setTaskPrompt] = useState('')
  const [isExecuting, setIsExecuting] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [executionOptions, setExecutionOptions] = useState({
    require_approval: false,
    priority: 'normal' as 'low' | 'normal' | 'high' | 'urgent',
    max_steps: 50,
    timeout_minutes: 30,
    tags: [] as string[]
  })

  const executeTask = async () => {
    if (!taskPrompt.trim()) return

    setIsExecuting(true)

    try {
      // In a real implementation, this would call the backend API
      const response = await fetch('/api/v1/agents/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: taskPrompt,
          ...executionOptions
        })
      })

      if (response.ok) {
        const result = await response.json()

        const newTask: Task = {
          id: result.task_id,
          prompt: taskPrompt,
          status: 'running',
          progress: 0,
          started_at: new Date().toISOString(),
          steps: []
        }

        setCurrentTask(newTask)
        setTaskPrompt('')

        // Simulate task execution progress
        simulateTaskExecution(newTask)
      } else {
        throw new Error('Task execution failed')
      }
    } catch (error) {
      console.error('Failed to execute task:', error)
      onTaskError?.('Failed to start task execution')
    } finally {
      setIsExecuting(false)
    }
  }

  const simulateTaskExecution = (task: Task) => {
    const steps = [
      'Analyzing task requirements',
      'Planning execution strategy',
      'Setting up development environment',
      'Implementing core functionality',
      'Adding error handling',
      'Testing implementation',
      'Finalizing and documenting'
    ]

    let currentStepIndex = 0
    const interval = setInterval(() => {
      if (currentStepIndex < steps.length) {
        const progress = ((currentStepIndex + 1) / steps.length) * 100

        setCurrentTask(prev => prev ? {
          ...prev,
          progress,
          current_step: steps[currentStepIndex],
          total_steps: steps.length,
          steps: steps.slice(0, currentStepIndex + 1).map((step, index) => ({
            id: `step-${index + 1}`,
            description: step,
            status: index < currentStepIndex ? 'completed' : index === currentStepIndex ? 'running' : 'pending',
            started_at: index <= currentStepIndex ? new Date().toISOString() : undefined,
            completed_at: index < currentStepIndex ? new Date().toISOString() : undefined
          }))
        } : null)

        currentStepIndex++
      } else {
        // Task completed
        clearInterval(interval)
        setCurrentTask(prev => prev ? {
          ...prev,
          status: 'completed',
          progress: 100,
          completed_at: new Date().toISOString(),
          result: { message: 'Task completed successfully', artifacts: ['code', 'documentation', 'tests'] }
        } : null)

        onTaskComplete?.(task)
      }
    }, 2000)
  }

  const pauseTask = () => {
    setCurrentTask(prev => prev ? { ...prev, status: 'paused' } : null)
  }

  const resumeTask = () => {
    setCurrentTask(prev => prev ? { ...prev, status: 'running' } : null)
    // In a real implementation, this would call the resume API
  }

  const cancelTask = () => {
    setCurrentTask(prev => prev ? { ...prev, status: 'failed', error: 'Task cancelled by user' } : null)
    // In a real implementation, this would call the cancel API
  }

  const restartTask = () => {
    if (currentTask) {
      setCurrentTask({
        ...currentTask,
        status: 'running',
        progress: 0,
        started_at: new Date().toISOString(),
        completed_at: undefined,
        error: undefined
      })
      simulateTaskExecution(currentTask)
    }
  }

  return (
    <div className="space-y-6">
      {/* Task Input */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Autonomous Task Executor
          </h2>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <Settings className="h-4 w-4 mr-1" />
            {showAdvanced ? 'Hide' : 'Show'} Advanced
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Task Description
            </label>
            <textarea
              value={taskPrompt}
              onChange={(e) => setTaskPrompt(e.target.value)}
              placeholder="Describe what you want the autonomous agent to accomplish..."
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-900 dark:text-white resize-none"
              rows={4}
            />
          </div>

          {showAdvanced && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Priority
                </label>
                <select
                  value={executionOptions.priority}
                  onChange={(e) => setExecutionOptions(prev => ({
                    ...prev,
                    priority: e.target.value as any
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white"
                >
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Max Steps
                </label>
                <input
                  type="number"
                  value={executionOptions.max_steps}
                  onChange={(e) => setExecutionOptions(prev => ({
                    ...prev,
                    max_steps: parseInt(e.target.value) || 50
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white"
                  min="1"
                  max="200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Timeout (minutes)
                </label>
                <input
                  type="number"
                  value={executionOptions.timeout_minutes}
                  onChange={(e) => setExecutionOptions(prev => ({
                    ...prev,
                    timeout_minutes: parseInt(e.target.value) || 30
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white"
                  min="1"
                  max="480"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Require Approval
                </label>
                <div className="flex items-center mt-2">
                  <input
                    type="checkbox"
                    checked={executionOptions.require_approval}
                    onChange={(e) => setExecutionOptions(prev => ({
                      ...prev,
                      require_approval: e.target.checked
                    }))}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                    Human approval for risky operations
                  </span>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-end">
            <button
              onClick={executeTask}
              disabled={isExecuting || !taskPrompt.trim()}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center"
            >
              {isExecuting ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <Play className="h-4 w-4 mr-2" />
              )}
              Execute Task
            </button>
          </div>
        </div>
      </div>

      {/* Current Task Status */}
      {currentTask && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Current Task: {currentTask.id}
            </h3>
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                currentTask.status === 'running' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                currentTask.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                currentTask.status === 'failed' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                currentTask.status === 'paused' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
              }`}>
                {currentTask.status}
              </span>
            </div>
          </div>

          <p className="text-gray-700 dark:text-gray-300 mb-4">{currentTask.prompt}</p>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
              <span>Progress</span>
              <span>{Math.round(currentTask.progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-300 ${
                  currentTask.status === 'completed' ? 'bg-green-600' :
                  currentTask.status === 'failed' ? 'bg-red-600' :
                  'bg-blue-600'
                }`}
                style={{ width: `${currentTask.progress}%` }}
              ></div>
            </div>
          </div>

          {/* Current Step */}
          {currentTask.current_step && (
            <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-3"></div>
                <span className="text-blue-700 dark:text-blue-400 font-medium">
                  {currentTask.current_step}
                </span>
              </div>
            </div>
          )}

          {/* Control Buttons */}
          <div className="flex space-x-3 mb-4">
            {currentTask.status === 'running' && (
              <button
                onClick={pauseTask}
                className="px-4 py-2 border border-yellow-300 dark:border-yellow-600 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400 rounded-lg transition-colors flex items-center"
              >
                <Pause className="h-4 w-4 mr-2" />
                Pause
              </button>
            )}

            {currentTask.status === 'paused' && (
              <button
                onClick={resumeTask}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center"
              >
                <Play className="h-4 w-4 mr-2" />
                Resume
              </button>
            )}

            {(currentTask.status === 'running' || currentTask.status === 'paused') && (
              <button
                onClick={cancelTask}
                className="px-4 py-2 border border-red-300 dark:border-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg transition-colors flex items-center"
              >
                <Square className="h-4 w-4 mr-2" />
                Cancel
              </button>
            )}

            {(currentTask.status === 'completed' || currentTask.status === 'failed') && (
              <button
                onClick={restartTask}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors flex items-center"
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Restart
              </button>
            )}
          </div>

          {/* Task Steps */}
          {currentTask.steps && currentTask.steps.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-3">Execution Steps</h4>
              <div className="space-y-2">
                {currentTask.steps.map((step, index) => (
                  <div key={step.id} className="flex items-center space-x-3 p-2 rounded-lg bg-gray-50 dark:bg-gray-900">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                      step.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                      step.status === 'running' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                      step.status === 'failed' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                    }`}>
                      {step.status === 'completed' ? '✓' :
                       step.status === 'running' ? '●' :
                       step.status === 'failed' ? '✗' :
                       index + 1}
                    </div>
                    <span className={`flex-1 text-sm ${
                      step.status === 'completed' ? 'text-green-700 dark:text-green-400' :
                      step.status === 'running' ? 'text-blue-700 dark:text-blue-400 font-medium' :
                      step.status === 'failed' ? 'text-red-700 dark:text-red-400' :
                      'text-gray-600 dark:text-gray-400'
                    }`}>
                      {step.description}
                    </span>
                    {step.started_at && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {new Date(step.started_at).toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error Display */}
          {currentTask.error && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <div className="flex items-center">
                <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                <span className="text-red-700 dark:text-red-400 font-medium">Error:</span>
              </div>
              <p className="text-red-700 dark:text-red-400 text-sm mt-1">{currentTask.error}</p>
            </div>
          )}

          {/* Result Display */}
          {currentTask.result && (
            <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
              <div className="flex items-center mb-2">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                <span className="text-green-700 dark:text-green-400 font-medium">Task Completed Successfully</span>
              </div>
              <pre className="text-green-700 dark:text-green-400 text-sm bg-green-100 dark:bg-green-900/40 p-2 rounded">
                {JSON.stringify(currentTask.result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
