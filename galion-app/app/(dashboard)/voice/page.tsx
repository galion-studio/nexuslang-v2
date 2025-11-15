'use client'

import * as React from 'react'
import { VoiceActivation } from '@/components/voice/VoiceActivation'
import { ConversationFlow } from '@/components/voice/ConversationFlow'
import { useVoiceProcessor } from '@/lib/voice/use-voice-processor'
import { Container } from '../../../shared/components/layout/ResponsiveContainer'
import VoiceAgentIntegration from '@/components/agents/VoiceAgentIntegration'
import type { ConversationMessage, VoiceCommand } from '../../../shared/types'

export default function VoicePage() {
  const [isActivated, setIsActivated] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(false)
  const [messages, setMessages] = React.useState<ConversationMessage[]>([])
  const [currentTranscript, setCurrentTranscript] = React.useState('')
  const [isTyping, setIsTyping] = React.useState(false)
  const [agentMode, setAgentMode] = React.useState(false)

  const {
    isListening,
    startListening,
    stopListening,
    error: voiceError
  } = useVoiceProcessor()

  // Handle voice activation
  const handleActivate = async () => {
    setIsLoading(true)

    // Simulate activation delay
    await new Promise(resolve => setTimeout(resolve, 1500))

    setIsLoading(false)
    setIsActivated(true)

    // Add welcome message
    const welcomeMessage: ConversationMessage = {
      id: 'welcome',
      type: 'assistant',
      content: "Hello! I'm your AI assistant. How can I help you today?",
      timestamp: new Date(),
    }

    setMessages([welcomeMessage])
  }

  // Handle voice commands
  const handleVoiceCommand = React.useCallback(async (command: VoiceCommand) => {
    // Add user message
    const userMessage: ConversationMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: command.transcription,
      timestamp: command.timestamp,
      voiceCommand: command
    }

    setMessages(prev => [...prev, userMessage])
    setCurrentTranscript('')
    setIsTyping(true)

    // Simulate AI processing
    setTimeout(() => {
      const aiResponse = generateAIResponse(command.transcription)
      const aiMessage: ConversationMessage = {
        id: `ai-${Date.now()}`,
        type: 'assistant',
        content: aiResponse,
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, aiMessage])
      setIsTyping(false)
    }, 1000 + Math.random() * 2000)
  }, [])

  // Generate AI response (placeholder)
  const generateAIResponse = (input: string): string => {
    const responses = [
      `I understand you want to know about "${input}". Let me help you with that.`,
      `That's an interesting request about "${input}". Here's what I can tell you.`,
      `Great question! Regarding "${input}", I can provide you with detailed information.`,
      `I see you're asking about "${input}". Let me give you a comprehensive answer.`,
      `Perfect! About "${input}", here's what you need to know.`
    ]

    return responses[Math.floor(Math.random() * responses.length)]
  }

  // Handle transcript updates
  React.useEffect(() => {
    if (isListening) {
      // In a real implementation, this would come from the voice processor
      const mockTranscript = "This is a mock transcript..."
      setCurrentTranscript(mockTranscript)
    } else {
      setCurrentTranscript('')
    }
  }, [isListening])

  // If not activated, show activation screen
  if (!isActivated) {
    return <VoiceActivation onActivate={handleActivate} isLoading={isLoading} />
  }

  // Show mode selection or conversation flow
  if (!agentMode) {
    return (
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Mode Selection */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Choose Your Voice Experience
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
            Select how you want to interact with your AI assistant
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
            <button
              onClick={() => setAgentMode(false)}
              className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 border-2 border-blue-200 dark:border-blue-800 rounded-xl hover:border-blue-300 dark:hover:border-blue-700 transition-colors"
            >
              <div className="text-4xl mb-4">💬</div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Voice Chat
              </h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                Natural conversation with AI assistant for questions, advice, and general interaction
              </p>
            </button>

            <button
              onClick={() => setAgentMode(true)}
              className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 border-2 border-purple-200 dark:border-purple-800 rounded-xl hover:border-purple-300 dark:hover:border-purple-700 transition-colors"
            >
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Autonomous Agents
              </h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                Voice-powered autonomous task execution with Manus-like AI agents
              </p>
            </button>
          </div>

          <div className="mt-8 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              💡 <strong>Autonomous Agents</strong> can build applications, analyze data, create APIs, and execute complex tasks using natural voice commands.
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Show autonomous agent interface
  return (
    <div className="max-w-6xl mx-auto">
      {/* Mode Toggle */}
      <div className="mb-6 flex justify-center">
        <button
          onClick={() => setAgentMode(false)}
          className="px-4 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg transition-colors text-sm flex items-center"
        >
          ← Back to Voice Chat
        </button>
      </div>

      <VoiceAgentIntegration
        onAgentTaskCreated={(taskId, prompt) => {
          console.log('Agent task created:', taskId, prompt)
        }}
        onAgentTaskCompleted={(task) => {
          console.log('Agent task completed:', task)
        }}
      />
    </div>
  )
}
