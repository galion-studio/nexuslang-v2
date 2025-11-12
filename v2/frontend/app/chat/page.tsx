'use client'

/**
 * AI Chat Page - Full-screen conversation interface
 * Multi-model AI chat with conversation persistence
 * Features model selection, export, and advanced settings
 */

import { useState, useEffect, useRef } from 'react'
import { Send, Trash2, Download, Settings, Zap, User, Bot } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  model?: string
}

// Available AI models
const AI_MODELS = [
  { id: 'anthropic/claude-3.5-sonnet', name: 'Claude 3.5 Sonnet', description: 'Best reasoning' },
  { id: 'openai/gpt-4-turbo', name: 'GPT-4 Turbo', description: 'General purpose' },
  { id: 'openai/gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Fast & cheap' },
  { id: 'meta-llama/llama-3-70b-instruct', name: 'Llama 3 70B', description: 'Open source' },
  { id: 'google/gemini-pro', name: 'Gemini Pro', description: 'Google AI' },
]

export default function ChatPage() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState(AI_MODELS[0].id)
  const [showSettings, setShowSettings] = useState(false)
  const [temperature, setTemperature] = useState(0.7)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  
  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  // Load history
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
    }
    
    // Welcome message if empty
    if (!saved) {
      setMessages([{
        role: 'assistant',
        content: "# Welcome to NexusLang AI Chat! 🚀\n\nI'm powered by Claude 3.5 Sonnet and I can help you with:\n\n- **Writing NexusLang code** - Get instant code generation\n- **Debugging** - Find and fix errors quickly\n- **Learning** - Understand AI and programming concepts\n- **Platform help** - Navigate features and settings\n\nWhat would you like to build today?",
        timestamp: new Date(),
        model: 'claude-3.5-sonnet'
      }])
    }
  }, [])
  
  // Save history
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('nexuslang_chat_history', JSON.stringify(messages))
    }
  }, [messages])
  
  // Send message
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
    
    try {
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        router.push('/auth/login')
        return
      }
      
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
          model: selectedModel,
          temperature,
          max_tokens: 2000
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to get AI response')
      }
      
      const data = await response.json()
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.content,
        timestamp: new Date(),
        model: data.model
      }])
      
    } catch (err) {
      console.error('Chat error:', err)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ Error: ${err instanceof Error ? err.message : 'Failed to send message'}`,
        timestamp: new Date()
      }])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }
  
  // Export conversation
  const exportChat = () => {
    const text = messages.map(m => 
      `[${m.timestamp.toLocaleString()}] ${m.role.toUpperCase()}: ${m.content}`
    ).join('\n\n')
    
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `nexuslang-chat-${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }
  
  // Clear conversation
  const clearChat = () => {
    if (confirm('Clear entire conversation?')) {
      setMessages([])
      localStorage.removeItem('nexuslang_chat_history')
    }
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950">
      <div className="max-w-6xl mx-auto h-screen flex flex-col">
        {/* Header */}
        <div className="border-b border-zinc-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <Zap className="text-purple-400" size={28} />
                AI Chat
              </h1>
              <p className="text-zinc-400 text-sm mt-1">
                Powered by {AI_MODELS.find(m => m.id === selectedModel)?.name}
              </p>
            </div>
            
            <div className="flex gap-3">
              {/* Model selector */}
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="px-4 py-2 bg-zinc-800 text-white rounded-lg border border-zinc-700 
                           focus:outline-none focus:border-blue-500"
              >
                {AI_MODELS.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name}
                  </option>
                ))}
              </select>
              
              {/* Actions */}
              <button
                onClick={exportChat}
                className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg 
                           transition flex items-center gap-2"
                title="Export conversation"
              >
                <Download size={18} />
                Export
              </button>
              
              <button
                onClick={clearChat}
                className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg 
                           transition flex items-center gap-2"
                title="Clear conversation"
              >
                <Trash2 size={18} />
              </button>
            </div>
          </div>
        </div>
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
          {messages.length === 0 ? (
            <div className="text-center py-20">
              <Zap className="mx-auto text-purple-400 mb-4" size={48} />
              <h2 className="text-xl font-bold text-white mb-2">Start a Conversation</h2>
              <p className="text-zinc-400">
                Ask me anything about NexusLang, coding, AI, or just chat!
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-4 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
              >
                {/* Avatar */}
                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.role === 'user' 
                    ? 'bg-blue-600' 
                    : 'bg-gradient-to-r from-purple-600 to-pink-600'
                }`}>
                  {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                </div>
                
                {/* Message bubble */}
                <div className={`flex-1 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <div
                    className={`inline-block px-6 py-4 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-zinc-800 text-zinc-100'
                    } max-w-[80%] text-left`}
                  >
                    {/* Render message with markdown-like formatting */}
                    <div className="prose prose-invert prose-sm max-w-none">
                      {message.content.split('\n').map((line, i) => {
                        // Handle headers
                        if (line.startsWith('# ')) {
                          return <h1 key={i} className="text-xl font-bold mb-2">{line.slice(2)}</h1>
                        }
                        if (line.startsWith('## ')) {
                          return <h2 key={i} className="text-lg font-bold mb-2">{line.slice(3)}</h2>
                        }
                        // Handle code blocks
                        if (line.startsWith('```')) {
                          return null // Handle in future enhancement
                        }
                        // Handle bullet points
                        if (line.startsWith('- ') || line.startsWith('• ')) {
                          return <li key={i} className="ml-4">{line.slice(2)}</li>
                        }
                        // Regular text
                        return line ? <p key={i} className="mb-2">{line}</p> : <br key={i} />
                      })}
                    </div>
                    
                    {/* Metadata */}
                    <div className={`text-xs mt-2 ${
                      message.role === 'user' ? 'text-blue-200' : 'text-zinc-500'
                    }`}>
                      {message.timestamp.toLocaleTimeString()}
                      {message.model && ` • ${message.model}`}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          
          {/* Loading */}
          {isLoading && (
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-600 to-pink-600 
                              flex items-center justify-center">
                <Bot size={20} />
              </div>
              <div className="bg-zinc-800 px-6 py-4 rounded-lg">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  <span className="ml-2 text-zinc-400 text-sm">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input area */}
        <div className="border-t border-zinc-800 px-6 py-4 bg-zinc-900/50 backdrop-blur">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-3">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    sendMessage()
                  }
                }}
                placeholder="Ask anything... (Shift+Enter for new line)"
                rows={3}
                className="flex-1 px-4 py-3 bg-zinc-800 text-white rounded-lg border border-zinc-700 
                           focus:outline-none focus:border-purple-500 transition resize-none"
                disabled={isLoading}
              />
              
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 
                           hover:from-blue-700 hover:to-purple-700 disabled:from-zinc-700 
                           disabled:to-zinc-700 disabled:cursor-not-allowed text-white rounded-lg 
                           transition flex items-center gap-2 font-medium"
              >
                <Send size={20} />
                Send
              </button>
            </div>
            
            {/* Quick info */}
            <div className="mt-3 flex items-center justify-between text-xs text-zinc-500">
              <div>
                Model: <span className="text-purple-400 font-medium">{AI_MODELS.find(m => m.id === selectedModel)?.name}</span>
                {' • '}
                Temperature: <span className="text-purple-400">{temperature}</span>
              </div>
              <div>
                Messages: <span className="text-purple-400">{messages.length}</span>
                {' • '}
                Press <kbd className="px-1 py-0.5 bg-zinc-800 rounded">Enter</kbd> to send
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

