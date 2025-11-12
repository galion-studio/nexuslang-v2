'use client'

/**
 * AI Chat Widget - Floating chat interface
 * Provides instant AI assistance throughout the platform
 * Uses Claude Sonnet for intelligent, context-aware responses
 */

import { useState, useEffect, useRef } from 'react'
import { MessageCircle, X, Send, Zap, Minimize2, Maximize2 } from 'lucide-react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface ChatWidgetProps {
  defaultOpen?: boolean
}

export default function ChatWidget({ defaultOpen = false }: ChatWidgetProps) {
  // State management
  const [isOpen, setIsOpen] = useState(defaultOpen)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Refs for auto-scroll and input focus
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus()
    }
  }, [isOpen, isMinimized])
  
  // Load conversation history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('nexuslang_chat_history')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        setMessages(parsed.map((m: any) => ({
          ...m,
          timestamp: new Date(m.timestamp)
        })))
      } catch (e) {
        console.error('Failed to load chat history:', e)
      }
    } else {
      // Welcome message
      setMessages([{
        role: 'assistant',
        content: "👋 Hi! I'm your NexusLang AI assistant. Ask me anything about:\n\n• Writing NexusLang code\n• Debugging errors\n• Platform features\n• AI concepts\n• Or just chat!",
        timestamp: new Date()
      }])
    }
  }, [])
  
  // Save conversation to localStorage
  useEffect(() => {
    if (messages.length > 1) {  // Skip saving just the welcome message
      localStorage.setItem('nexuslang_chat_history', JSON.stringify(messages))
    }
  }, [messages])
  
  // Send message to AI
  const sendMessage = async () => {
    if (!input.trim() || isLoading) return
    
    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)
    
    try {
      // Get auth token
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        throw new Error('Please login to use the AI chat')
      }
      
      // Call AI API
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          messages: messages.concat(userMessage).map(m => ({
            role: m.role,
            content: m.content
          })),
          model: 'anthropic/claude-3.5-sonnet',  // Using Claude Sonnet for best reasoning
          temperature: 0.7,
          max_tokens: 1000
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to get AI response')
      }
      
      const data = await response.json()
      
      // Add AI response
      const aiMessage: Message = {
        role: 'assistant',
        content: data.content,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, aiMessage])
      
    } catch (err) {
      console.error('Chat error:', err)
      setError(err instanceof Error ? err.message : 'Failed to send message')
      
      // Add error message to chat
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ Error: ${err instanceof Error ? err.message : 'Something went wrong'}`,
        timestamp: new Date()
      }])
    } finally {
      setIsLoading(false)
    }
  }
  
  // Handle Enter key
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }
  
  // Clear conversation
  const clearChat = () => {
    setMessages([{
      role: 'assistant',
      content: "Chat cleared! How can I help you?",
      timestamp: new Date()
    }])
    localStorage.removeItem('nexuslang_chat_history')
  }
  
  // Render nothing if closed
  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 
                   hover:from-blue-700 hover:to-purple-700 text-white rounded-full shadow-lg 
                   flex items-center justify-center transition-all hover:scale-110 z-50"
        aria-label="Open AI Chat"
      >
        <MessageCircle size={24} />
      </button>
    )
  }
  
  // Minimized view
  if (isMinimized) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsMinimized(false)}
          className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 
                     rounded-lg shadow-lg flex items-center gap-2 hover:from-blue-700 hover:to-purple-700"
        >
          <MessageCircle size={20} />
          <span className="font-medium">AI Chat</span>
          <span className="bg-white/20 px-2 py-0.5 rounded-full text-xs">
            {messages.length}
          </span>
        </button>
      </div>
    )
  }
  
  // Full chat widget
  return (
    <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-zinc-900 rounded-lg shadow-2xl 
                    border border-zinc-800 flex flex-col z-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-3 rounded-t-lg 
                      flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Zap size={20} className="text-white" />
          <span className="font-semibold text-white">AI Assistant</span>
          <span className="text-xs text-white/80">(Claude Sonnet)</span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setIsMinimized(true)}
            className="text-white/80 hover:text-white transition"
            aria-label="Minimize"
          >
            <Minimize2 size={18} />
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="text-white/80 hover:text-white transition"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] px-4 py-2 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-zinc-800 text-zinc-100'
              }`}
            >
              <div className="text-sm whitespace-pre-wrap">{message.content}</div>
              <div className={`text-xs mt-1 ${
                message.role === 'user' ? 'text-blue-200' : 'text-zinc-500'
              }`}>
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-zinc-800 px-4 py-2 rounded-lg">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Error display */}
      {error && (
        <div className="px-4 py-2 bg-red-500/10 border-t border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}
      
      {/* Input */}
      <div className="p-4 border-t border-zinc-800">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything..."
            className="flex-1 px-4 py-2 bg-zinc-800 text-white rounded-lg border border-zinc-700 
                       focus:outline-none focus:border-blue-500 transition"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-700 
                       disabled:cursor-not-allowed text-white rounded-lg transition flex items-center gap-2"
          >
            <Send size={18} />
          </button>
        </div>
        
        {/* Quick actions */}
        <div className="mt-2 flex gap-2 text-xs">
          <button
            onClick={clearChat}
            className="text-zinc-500 hover:text-zinc-300 transition"
          >
            Clear
          </button>
          <a
            href="/chat"
            className="text-zinc-500 hover:text-zinc-300 transition"
          >
            Full Screen
          </a>
        </div>
      </div>
    </div>
  )
}

