'use client'

import { useState } from 'react'
import { Send, Bot, User, Settings, Zap, MessageSquare, Code, Play, Terminal } from 'lucide-react'
// Shared components removed for simplified deployment
// Shared components removed for simplified deployment

interface AgentPromptProps {
  onSubmit?: (prompt: string, agent: string) => void
  className?: string
}

interface NexusExecutionResult {
  success: boolean
  result?: any
  error?: string
  binary_compiled?: boolean
  execution_time?: number
  binary_size?: number
}

const availableAgents = [
  { id: 'code_generator', name: 'Code Generator', icon: '⚡', description: 'AI-powered code generation and optimization', role: 'code_generator' },
  { id: 'code_reviewer', name: 'Code Reviewer', icon: '👁️', description: 'Automated code review and quality assurance', role: 'code_reviewer' },
  { id: 'tester', name: 'Tester', icon: '🧪', description: 'Comprehensive testing and validation', role: 'tester' },
  { id: 'optimizer', name: 'Optimizer', icon: '🚀', description: 'Performance optimization and refactoring', role: 'optimizer' },
  { id: 'documentation', name: 'Documentation', icon: '📚', description: 'Technical documentation generation', role: 'documentation' },
  { id: 'security_auditor', name: 'Security Auditor', icon: '🔒', description: 'Security analysis and vulnerability detection', role: 'security_auditor' },
  { id: 'ux_ui', name: 'UX/UI Designer', icon: '🎨', description: 'User experience and interface design', role: 'ux_ui' },
]

export function AgentPrompt({ onSubmit, className = '' }: AgentPromptProps) {
  const [prompt, setPrompt] = useState('')
  const [selectedAgent, setSelectedAgent] = useState('code_generator')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [nexusCode, setNexusCode] = useState('')
  const [isExecuting, setIsExecuting] = useState(false)
  const [executionResult, setExecutionResult] = useState<NexusExecutionResult | null>(null)
  const [conversation, setConversation] = useState<Array<{
    id: string
    role: 'user' | 'assistant' | 'system'
    content: string
    agent?: string
    timestamp: Date
    nexusResult?: NexusExecutionResult
  }>>([
    {
      id: '1',
      role: 'assistant',
      content: 'Welcome to the Enhanced NexusLang Development Environment! I can help you create tasks for our specialized AI agents or execute NexusLang code directly. Choose an agent above or write NexusLang code below.',
      agent: 'system',
      timestamp: new Date()
    }
  ])

  const executeNexusCode = async () => {
    if (!nexusCode.trim() || isExecuting) return

    setIsExecuting(true)
    setExecutionResult(null)

    try {
      const response = await fetch('/api/v2/enhanced-agents/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: nexusCode,
          compile_binary: true, // Always compile for performance
          optimize: true,
        }),
      })

      const result: NexusExecutionResult = await response.json()
      setExecutionResult(result)

      // Add execution result to conversation
      const resultMessage = {
        id: Date.now().toString(),
        role: 'system' as const,
        content: result.success
          ? `✅ NexusLang code executed successfully!\n\nExecution time: ${result.execution_time?.toFixed(3)}s\n${result.binary_compiled ? `Binary compiled (${(result.binary_size || 0) / 1024} KB)` : 'Interpreted execution'}`
          : `❌ Execution failed: ${result.error}`,
        timestamp: new Date(),
        nexusResult: result,
      }

      setConversation(prev => [...prev, resultMessage])

    } catch (error) {
      console.error('Failed to execute NexusLang code:', error)
      setExecutionResult({
        success: false,
        error: 'Failed to execute code',
      })
    } finally {
      setIsExecuting(false)
    }
  }

  const createAgentTask = async () => {
    if (!prompt.trim() || isSubmitting) return

    setIsSubmitting(true)

    try {
      const response = await fetch('/api/v2/enhanced-agents/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: prompt.length > 50 ? prompt.substring(0, 50) + '...' : prompt,
          description: prompt,
          priority: 'normal',
          tags: ['agent_request'],
          cost_estimate: 0.01,
        }),
      })

      if (response.ok) {
        const task = await response.json()

        const userMessage = {
          id: Date.now().toString(),
          role: 'user' as const,
          content: prompt,
          timestamp: new Date()
        }

        const agent = availableAgents.find(a => a.id === selectedAgent)
        const taskMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant' as const,
          content: `✅ Task created for ${agent?.name}!\n\nTask ID: ${task.id}\nStatus: ${task.status}\n\nThe agent will process this request and I'll notify you when it's complete.`,
          agent: selectedAgent,
          timestamp: new Date()
        }

        setConversation(prev => [...prev, userMessage, taskMessage])
        setPrompt('')
      }
    } catch (error) {
      console.error('Failed to create agent task:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim() || isSubmitting) return

    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: prompt,
      timestamp: new Date()
    }

    setConversation(prev => [...prev, userMessage])
    setIsSubmitting(true)

    try {
      // Call the onSubmit callback
      await onSubmit?.(prompt, selectedAgent)

      // Create agent task instead of simulating response
      await createAgentTask()

      // Simulate AI response
      setTimeout(() => {
        const aiResponse = {
          id: (Date.now() + 1).toString(),
          role: 'assistant' as const,
          content: 'Task submitted successfully. Processing your request...',
          timestamp: new Date()
        }

        setConversation(prev => [...prev, aiResponse])
        setIsSubmitting(false)
      }, 2000)

    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        agent: selectedAgent,
        timestamp: new Date()
      }
      setConversation(prev => [...prev, errorMessage])
      setIsSubmitting(false)
    }

    setPrompt('')
  }

  const handleVoiceSubmit = () => {
    if (prompt.trim()) {
      handleSubmit(new Event('submit') as any)
    }
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Agent Selection */}
      <div className="bg-white p-6 rounded-lg border border-neutral-200 shadow-sm">
        <div className="flex items-center space-x-3 mb-4">
          <Settings className="w-5 h-5 text-neutral-600" />
          <span className="text-lg font-semibold text-neutral-900">AI Agent Selection</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {availableAgents.map((agent) => (
            <button
              key={agent.id}
              onClick={() => setSelectedAgent(agent.id)}
              className={`p-4 rounded-lg border text-left transition-all hover:shadow-md ${
                selectedAgent === agent.id
                  ? 'border-blue-500 bg-blue-50 text-blue-700 shadow-md'
                  : 'border-neutral-200 hover:border-blue-300 hover:bg-neutral-50'
              }`}
            >
              <div className="flex items-center space-x-3 mb-2">
                <span className="text-2xl">{agent.icon}</span>
                <span className="text-sm font-semibold">{agent.name}</span>
              </div>
              <p className="text-sm text-neutral-600">{agent.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* NexusLang Code Execution */}
      <div className="bg-white p-6 rounded-lg border border-neutral-200 shadow-sm">
        <div className="flex items-center space-x-3 mb-4">
          <Code className="w-5 h-5 text-neutral-600" />
          <span className="text-lg font-semibold text-neutral-900">NexusLang Code Execution</span>
        </div>

        <div className="space-y-4">
          <textarea
            value={nexusCode}
            onChange={(e) => setNexusCode(e.target.value)}
            placeholder={`// Write your NexusLang v2 code here
// Example:
function fibonacci(n: int) -> int {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

print("Fibonacci sequence:");
for (let i = 0; i < 10; i++) {
    print(fibonacci(i));
}`}
            rows={8}
            className="w-full px-4 py-3 border border-neutral-300 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                onClick={executeNexusCode}
                disabled={!nexusCode.trim() || isExecuting}
                leftIcon={isExecuting ? <Loading size="sm" /> : <Play className="w-4 h-4" />}
              >
                {isExecuting ? 'Executing...' : 'Execute Code'}
              </Button>
              <span className="text-sm text-neutral-600">
                Binary compilation enabled for optimal performance
              </span>
            </div>

            {executionResult && (
              <div className={`text-sm px-3 py-1 rounded-full ${
                executionResult.success
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {executionResult.success ? 'Success' : 'Failed'}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Agent Task Creation */}
      <div className="bg-white p-6 rounded-lg border border-neutral-200 shadow-sm">
        <div className="flex items-center space-x-3 mb-4">
          <MessageSquare className="w-5 h-5 text-neutral-600" />
          <span className="text-lg font-semibold text-neutral-900">Create Agent Task</span>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={`Describe the task for the selected agent...

Examples:
- "Generate a React component for user authentication"
- "Review this code for security vulnerabilities"
- "Create unit tests for the payment system"
- "Optimize this database query for better performance"`}
            rows={4}
            className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Button
                type="submit"
                disabled={!prompt.trim() || isSubmitting}
                leftIcon={isSubmitting ? <Loading size="sm" /> : <Send className="w-4 h-4" />}
              >
                {isSubmitting ? 'Creating Task...' : 'Create Task'}
              </Button>
              <VoiceButton
                onTranscription={(text) => {
                  setPrompt(text)
                  if (text.trim()) {
                    // Auto-submit after voice input
                    setTimeout(() => handleSubmit(new Event('submit') as any), 500)
                  }
                }}
                platform="developer"
              />
            </div>

            <div className="text-sm text-neutral-600">
              Selected: <span className="font-medium">
                {availableAgents.find(a => a.id === selectedAgent)?.name}
              </span>
            </div>
          </div>
        </form>
      </div>

      {/* Conversation History */}
      <div className="bg-white p-6 rounded-lg border border-neutral-200 shadow-sm">
        <div className="flex items-center space-x-3 mb-4">
          <Terminal className="w-5 h-5 text-neutral-600" />
          <span className="text-lg font-semibold text-neutral-900">Activity Log</span>
        </div>

        <div className="max-h-96 overflow-y-auto space-y-4">
          {conversation.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-lg px-4 py-3 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white ml-auto'
                    : message.role === 'system'
                    ? 'bg-neutral-100 text-neutral-800 border border-neutral-200'
                    : 'bg-neutral-50 text-neutral-900 border border-neutral-200'
                }`}
              >
                <div className="flex items-center space-x-2 mb-2">
                  {message.role === 'user' ? (
                    <User className="w-4 h-4" />
                  ) : message.role === 'system' ? (
                    <Terminal className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                  {message.agent && (
                    <span className="text-xs opacity-75">
                      {availableAgents.find(a => a.id === message.agent)?.name || message.agent}
                    </span>
                  )}
                </div>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                {message.nexusResult && (
                  <div className="mt-3 p-3 bg-black/10 rounded text-xs font-mono">
                    <div>Execution Time: {message.nexusResult.execution_time?.toFixed(3)}s</div>
                    {message.nexusResult.binary_size && (
                      <div>Binary Size: {(message.nexusResult.binary_size / 1024).toFixed(1)} KB</div>
                    )}
                  </div>
                )}
                <span className="text-xs opacity-50 mt-2 block">
                  {message.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}

          {isSubmitting && (
            <div className="flex justify-start">
              <div className="bg-neutral-50 border border-neutral-200 rounded-lg px-4 py-3 max-w-lg">
                <div className="flex items-center space-x-2">
                  <Loading size="sm" />
                  <span className="text-sm text-neutral-600">Processing...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AgentPrompt
