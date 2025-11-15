'use client'

import { useState, useEffect } from 'react'
import { Bot, Mic, MessageSquare, Zap, CheckCircle, AlertTriangle, Clock } from 'lucide-react'
import { VoiceAssistant } from '../voice/VoiceAssistant'

interface VoiceAgentIntegrationProps {
  onAgentTaskCreated?: (taskId: string, prompt: string) => void
  onAgentTaskCompleted?: (task: any) => void
}

export default function VoiceAgentIntegration({
  onAgentTaskCreated,
  onAgentTaskCompleted
}: VoiceAgentIntegrationProps) {
  const [isAgentMode, setIsAgentMode] = useState(false)
  const [agentTasks, setAgentTasks] = useState<Array<{
    id: string
    prompt: string
    status: 'processing' | 'completed' | 'error'
    result?: string
    createdAt: Date
  }>>([])
  const [currentProcessingTask, setCurrentProcessingTask] = useState<string | null>(null)

  // Keywords that trigger autonomous agent mode
  const agentKeywords = [
    'build', 'create', 'develop', 'implement', 'generate', 'design',
    'analyze', 'research', 'optimize', 'automate', 'deploy', 'setup',
    'configure', 'integrate', 'test', 'validate', 'document'
  ]

  const handleVoiceCommand = async (command: string) => {
    const lowerCommand = command.toLowerCase()

    // Check if this looks like an autonomous task request
    const containsAgentKeyword = agentKeywords.some(keyword =>
      lowerCommand.includes(keyword)
    )

    // Check for explicit agent requests
    const isExplicitAgentRequest = lowerCommand.includes('agent') ||
                                   lowerCommand.includes('autonomous') ||
                                   lowerCommand.includes('manus')

    if (containsAgentKeyword || isExplicitAgentRequest) {
      setIsAgentMode(true)

      // Create autonomous task
      const taskId = `voice-task-${Date.now()}`
      const newTask = {
        id: taskId,
        prompt: command,
        status: 'processing' as const,
        createdAt: new Date()
      }

      setAgentTasks(prev => [newTask, ...prev])
      setCurrentProcessingTask(taskId)

      onAgentTaskCreated?.(taskId, command)

      // Simulate task processing
      setTimeout(() => {
        processVoiceAgentTask(taskId, command)
      }, 2000)

      return `I've started an autonomous task for you: "${command}". I'll work on this in the background and let you know when it's complete.`
    }

    return `I heard: "${command}". This doesn't seem to require autonomous agent capabilities. Would you like me to help you with something that involves building, creating, or analyzing?`
  }

  const processVoiceAgentTask = async (taskId: string, prompt: string) => {
    try {
      // In a real implementation, this would call the autonomous agent API
      const response = await fetch('/api/v1/agents/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          require_approval: false,
          priority: 'normal',
          source: 'voice_command'
        })
      })

      if (response.ok) {
        const result = await response.json()

        // Update task status
        setAgentTasks(prev => prev.map(task =>
          task.id === taskId
            ? { ...task, status: 'completed', result: 'Task completed successfully' }
            : task
        ))

        setCurrentProcessingTask(null)

        // Call completion callback
        onAgentTaskCompleted?.({
          id: taskId,
          prompt,
          status: 'completed',
          result: 'Task completed successfully',
          task_api_id: result.task_id
        })

      } else {
        throw new Error('Task execution failed')
      }

    } catch (error) {
      console.error('Voice agent task failed:', error)

      setAgentTasks(prev => prev.map(task =>
        task.id === taskId
          ? { ...task, status: 'error', result: 'Task execution failed' }
          : task
      ))

      setCurrentProcessingTask(null)
    }
  }

  const handleVoiceResponse = (response: string) => {
    // Process the AI response to see if it contains task results
    console.log('Voice response:', response)
  }

  const clearCompletedTasks = () => {
    setAgentTasks(prev => prev.filter(task => task.status !== 'completed'))
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processing': return <Clock className="h-4 w-4 text-blue-500 animate-spin" />
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'error': return <AlertTriangle className="h-4 w-4 text-red-500" />
      default: return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processing': return 'text-blue-700 dark:text-blue-400'
      case 'completed': return 'text-green-700 dark:text-green-400'
      case 'error': return 'text-red-700 dark:text-red-400'
      default: return 'text-gray-700 dark:text-gray-400'
    }
  }

  return (
    <div className="space-y-6">
      {/* Mode Indicator */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${isAgentMode ? 'bg-blue-100 dark:bg-blue-900/20' : 'bg-gray-100 dark:bg-gray-800'}`}>
              <Bot className={`h-5 w-5 ${isAgentMode ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500'}`} />
            </div>
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white">
                Autonomous Agent Mode
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {isAgentMode
                  ? 'Voice commands will trigger autonomous task execution'
                  : 'Standard voice interaction mode'
                }
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              isAgentMode
                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
            }`}>
              {isAgentMode ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>

        {isAgentMode && (
          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="flex items-start space-x-2">
              <Zap className="h-4 w-4 text-blue-500 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-blue-700 dark:text-blue-400">
                  Agent Mode Active
                </p>
                <p className="text-sm text-blue-600 dark:text-blue-500">
                  Try saying things like "Build a user authentication system" or "Create a dashboard component" to trigger autonomous task execution.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Voice Assistant Integration */}
      <VoiceAssistant
        onVoiceCommand={handleVoiceCommand}
        onVoiceResponse={handleVoiceResponse}
        className="mb-6"
      />

      {/* Agent Tasks History */}
      {agentTasks.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
              <MessageSquare className="h-5 w-5 mr-2" />
              Voice-Triggered Agent Tasks
            </h3>
            <button
              onClick={clearCompletedTasks}
              className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              Clear Completed
            </button>
          </div>

          <div className="space-y-3">
            {agentTasks.map((task) => (
              <div
                key={task.id}
                className={`p-4 rounded-lg border ${
                  task.status === 'processing'
                    ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
                    : task.status === 'completed'
                    ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                    : task.status === 'error'
                    ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                    : 'bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-700'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    {getStatusIcon(task.status)}
                    <div className="flex-1">
                      <p className={`font-medium ${getStatusColor(task.status)}`}>
                        "{task.prompt}"
                      </p>
                      <div className="flex items-center space-x-4 mt-1">
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {task.createdAt.toLocaleTimeString()}
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          ID: {task.id}
                        </span>
                        {currentProcessingTask === task.id && (
                          <span className="text-xs text-blue-600 dark:text-blue-400 font-medium animate-pulse">
                            Processing...
                          </span>
                        )}
                      </div>
                      {task.result && (
                        <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">
                          {task.result}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              💡 <strong>Pro tip:</strong> Use action verbs like "build", "create", "analyze", or "implement" to trigger autonomous tasks
            </p>
          </div>
        </div>
      )}

      {/* Agent Capabilities Info */}
      <div className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 rounded-lg p-6 border border-blue-200 dark:border-blue-800">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Autonomous Agent Capabilities
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">Development Tasks</h4>
            <ul className="space-y-1 text-gray-600 dark:text-gray-400">
              <li>• Build complete applications</li>
              <li>• Create API endpoints</li>
              <li>• Generate documentation</li>
              <li>• Set up databases</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">Analysis Tasks</h4>
            <ul className="space-y-1 text-gray-600 dark:text-gray-400">
              <li>• Research topics</li>
              <li>• Analyze data</li>
              <li>• Generate reports</li>
              <li>• Optimize performance</li>
            </ul>
          </div>
        </div>

        <div className="mt-4 p-3 bg-white/50 dark:bg-gray-800/50 rounded-lg">
          <p className="text-sm text-gray-700 dark:text-gray-300">
            <strong>Example commands:</strong> "Build a React dashboard with charts",
            "Create a user authentication API", "Analyze customer feedback data",
            "Set up a CI/CD pipeline"
          </p>
        </div>
      </div>
    </div>
  )
}
