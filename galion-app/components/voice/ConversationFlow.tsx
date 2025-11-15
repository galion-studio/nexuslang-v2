'use client'

import { useState, useEffect, useRef } from 'react'
import { Mic, MicOff, Volume2, Settings, MessageCircle } from 'lucide-react'
import { ChatWindow, useChatMessages } from '@/shared/components/ui/ChatWindow'
import { VoiceButton } from '@/shared/components/ui/VoiceButton'
import { LoadingStates } from '@/shared/components/ui/LoadingStates'
import { VoiceWaveform } from './VoiceWaveform'

interface ConversationFlowProps {
  className?: string
}

export function ConversationFlow({ className = '' }: ConversationFlowProps) {
  const [isListening, setIsListening] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [volume, setVolume] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const { messages, addMessage, updateMessageStatus } = useChatMessages([
    {
      id: 'welcome',
      content: "Hello! I'm Galion, your AI assistant. How can I help you today?",
      sender: 'assistant',
      timestamp: new Date(),
      type: 'text'
    }
  ])

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  useEffect(() => {
    // Initialize audio context for volume monitoring
    const initAudio = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        streamRef.current = stream

        const audioContext = new AudioContext()
        const analyser = audioContext.createAnalyser()
        const microphone = audioContext.createMediaStreamSource(stream)
        const dataArray = new Uint8Array(analyser.frequencyBinCount)

        microphone.connect(analyser)
        analyser.fftSize = 256

        const updateVolume = () => {
          if (isListening) {
            analyser.getByteFrequencyData(dataArray)
            const average = dataArray.reduce((a, b) => a + b) / dataArray.length
            setVolume(Math.round((average / 255) * 100))
            requestAnimationFrame(updateVolume)
          }
        }

        if (isListening) {
          updateVolume()
        }
      } catch (err) {
        console.error('Failed to initialize audio:', err)
      }
    }

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [isListening])

  const startListening = async () => {
    try {
      setError(null)
      setIsListening(true)

      // Mock voice processing - in real implementation, this would connect to the voice API
      setTimeout(() => {
        setIsListening(false)
        setIsProcessing(true)

        // Simulate processing delay
        setTimeout(() => {
          setIsProcessing(false)
          setIsSpeaking(true)

          // Add user message
          const userMessageId = addMessage("Hello, can you help me with something?", 'user', 'voice')

          // Add AI response
          setTimeout(() => {
            addMessage("Of course! I'd be happy to help you. What would you like to know or do?", 'assistant', 'text')
            setIsSpeaking(false)
          }, 2000)
        }, 1500)
      }, 2000)

    } catch (err: any) {
      setError(err.message || 'Failed to start listening')
      setIsListening(false)
    }
  }

  const stopListening = () => {
    setIsListening(false)
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
    }
  }

  const handleSendMessage = (message: string) => {
    const messageId = addMessage(message, 'user', 'text')
    updateMessageStatus(messageId, 'sending')

    // Simulate AI response
    setTimeout(() => {
      updateMessageStatus(messageId, 'sent')
      setIsProcessing(true)

      setTimeout(() => {
        addMessage(`I understand you said: "${message}". This is a mock response from Galion.`, 'assistant', 'text')
        setIsProcessing(false)
      }, 1500)
    }, 500)
  }

  const toggleVoice = () => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }

  return (
    <div className={`max-w-4xl mx-auto p-4 space-y-6 ${className}`}>
      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-foreground mb-2">
          Galion Voice Assistant
        </h1>
        <p className="text-foreground-muted">
          Speak naturally or type your messages
        </p>
      </div>

      {/* Voice Controls */}
      <div className="flex justify-center items-center space-x-6">
        <VoiceButton
          size="large"
          state={isListening ? 'listening' : isProcessing ? 'processing' : isSpeaking ? 'speaking' : 'idle'}
          platform="galion-app"
          onClick={toggleVoice}
          disabled={isProcessing}
        />

        <div className="text-center">
          <p className="text-sm font-medium text-foreground">
            {isListening && 'Listening...'}
            {isProcessing && 'Processing...'}
            {isSpeaking && 'Speaking...'}
            {!isListening && !isProcessing && !isSpeaking && 'Ready to listen'}
          </p>
          {error && (
            <p className="text-sm text-error mt-1">{error}</p>
          )}
        </div>
      </div>

      {/* Voice Waveform */}
      <div className="flex justify-center">
        <VoiceWaveform
          isActive={isListening}
          volume={volume}
          className="w-64 h-16"
        />
      </div>

      {/* Chat Interface */}
      <div className="bg-surface rounded-lg shadow-lg">
        <ChatWindow
          messages={messages}
          onSendMessage={handleSendMessage}
          onVoiceToggle={toggleVoice}
          isTyping={isProcessing}
          isVoiceActive={isListening}
          placeholder="Type your message or click the microphone..."
          maxHeight="max-h-96"
        />
      </div>

      {/* Quick Actions */}
      <div className="flex justify-center space-x-4">
        <button className="flex items-center space-x-2 px-4 py-2 bg-surface-hover hover:bg-surface-active rounded-lg transition-colors">
          <MessageCircle className="w-4 h-4" />
          <span className="text-sm">New Conversation</span>
        </button>

        <button className="flex items-center space-x-2 px-4 py-2 bg-surface-hover hover:bg-surface-active rounded-lg transition-colors">
          <Settings className="w-4 h-4" />
          <span className="text-sm">Settings</span>
        </button>
      </div>

      {/* Status Indicator */}
      <div className="flex justify-center">
        <div className="flex items-center space-x-2 px-3 py-1 bg-surface-hover rounded-full">
          {isListening ? (
            <>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs text-green-600 dark:text-green-400">Voice Active</span>
            </>
          ) : isProcessing ? (
            <>
              <LoadingStates type="spinner" size="sm" />
              <span className="text-xs text-yellow-600 dark:text-yellow-400">Processing</span>
            </>
          ) : (
            <>
              <div className="w-2 h-2 bg-gray-400 rounded-full" />
              <span className="text-xs text-gray-600 dark:text-gray-400">Ready</span>
            </>
          )}
        </div>
      </div>
    </div>
  )
}