'use client'

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Paperclip, Smile, Mic, MicOff } from 'lucide-react'
import { EnhancedButton } from '@/components/ui/enhanced-button'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'

interface Message {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
  type: 'text' | 'image' | 'file' | 'voice'
  metadata?: {
    imageUrl?: string
    fileUrl?: string
    voiceDuration?: number
    processing?: boolean
  }
}

interface ChatInterfaceProps {
  initialMessages?: Message[]
  onSendMessage?: (message: string) => void
  onVoiceMessage?: (audioBlob: Blob) => void
  placeholder?: string
  disabled?: boolean
  className?: string
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  initialMessages = [],
  onSendMessage,
  onVoiceMessage,
  placeholder = "Type your message...",
  disabled = false,
  className
}) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || disabled) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    onSendMessage?.(userMessage.content)

    // Simulate AI response
    setIsTyping(true)
    setTimeout(() => {
      const aiResponse = generateAIResponse(userMessage.content)
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: aiResponse,
        sender: 'ai',
        timestamp: new Date(),
        type: 'text'
      }
      setMessages(prev => [...prev, aiMessage])
      setIsTyping(false)
    }, 1000 + Math.random() * 2000)
  }

  const generateAIResponse = (userInput: string): string => {
    // Simple response generation - in real app, this would call your AI API
    const responses = [
      `I understand you're asking about "${userInput}". Let me help you with that.`,
      `That's an interesting question about ${userInput}. Here's what I can tell you:`,
      `Regarding ${userInput}, I can provide you with detailed information.`,
      `Great question! Let me share some insights about ${userInput}.`,
      `I see you're interested in ${userInput}. Let me provide you with comprehensive information.`
    ]

    return responses[Math.floor(Math.random() * responses.length)]
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      const audioChunks: Blob[] = []

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data)
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
        onVoiceMessage?.(audioBlob)

        // Add voice message to chat
        const voiceMessage: Message = {
          id: Date.now().toString(),
          content: 'Voice message',
          sender: 'user',
          timestamp: new Date(),
          type: 'voice',
          metadata: {
            voiceDuration: audioChunks.length * 0.1 // Rough estimate
          }
        }
        setMessages(prev => [...prev, voiceMessage])

        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)

      toast.success('Recording... Tap to stop')
    } catch (error) {
      console.error('Error starting voice recording:', error)
      toast.error('Could not access microphone')
    }
  }

  const stopVoiceRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      toast.success('Voice message sent')
    }
  }

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className={cn('flex flex-col h-full max-h-[600px] bg-white dark:bg-gray-900 rounded-lg border', className)}>
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b bg-gray-50 dark:bg-gray-800 rounded-t-lg">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
          <div>
            <h3 className="font-semibold text-sm">AI Assistant</h3>
            <p className="text-xs text-muted-foreground">
              {isTyping ? 'Typing...' : 'Online'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-blue-500" />
          <span className="text-xs text-muted-foreground">Galion AI</span>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={cn(
                'flex gap-3 max-w-[80%]',
                message.sender === 'user' ? 'ml-auto flex-row-reverse' : ''
              )}
            >
              <Avatar className="w-8 h-8 flex-shrink-0">
                <AvatarFallback className={cn(
                  'text-xs',
                  message.sender === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-green-500 text-white'
                )}>
                  {message.sender === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </AvatarFallback>
              </Avatar>

              <div className={cn(
                'rounded-lg px-4 py-2 max-w-full',
                message.sender === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
              )}>
                {message.type === 'voice' && (
                  <div className="flex items-center gap-2 mb-2">
                    <Mic className="h-4 w-4" />
                    <span className="text-sm font-medium">Voice Message</span>
                    {message.metadata?.voiceDuration && (
                      <span className="text-xs opacity-70">
                        ({message.metadata.voiceDuration.toFixed(1)}s)
                      </span>
                    )}
                  </div>
                )}

                <p className="text-sm leading-relaxed">{message.content}</p>

                <div className={cn(
                  'text-xs mt-2 opacity-70',
                  message.sender === 'user' ? 'text-right' : 'text-left'
                )}>
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            </motion.div>
          ))}

          {isTyping && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex gap-3 max-w-[80%]"
            >
              <Avatar className="w-8 h-8 flex-shrink-0">
                <AvatarFallback className="bg-green-500 text-white">
                  <Bot className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
              <div className="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t bg-gray-50 dark:bg-gray-800 rounded-b-lg">
        <div className="flex items-center gap-3">
          {/* Voice Recording Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
            className={cn(
              'p-2 rounded-full transition-colors',
              isRecording
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
            )}
            disabled={disabled}
          >
            {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </motion.button>

          {/* Text Input */}
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={disabled ? 'Chat disabled...' : placeholder}
              disabled={disabled}
              className="w-full px-4 py-2 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />

            {/* Attachment Button */}
            <button className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 transition-colors">
              <Paperclip className="h-4 w-4" />
            </button>
          </div>

          {/* Send Button */}
          <EnhancedButton
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || disabled}
            size="sm"
            className="px-4"
          >
            <Send className="h-4 w-4" />
          </EnhancedButton>
        </div>

        {/* Quick Actions */}
        <div className="flex gap-2 mt-3">
          {[
            { label: 'Help', action: () => setInputValue('Help me with...') },
            { label: 'Code', action: () => setInputValue('Write code for...') },
            { label: 'Research', action: () => setInputValue('Research...') },
            { label: 'Image', action: () => setInputValue('Generate an image of...') }
          ].map((quickAction) => (
            <button
              key={quickAction.label}
              onClick={quickAction.action}
              disabled={disabled}
              className="px-3 py-1 text-xs bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-full transition-colors disabled:opacity-50"
            >
              {quickAction.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
