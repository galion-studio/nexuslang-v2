'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Search, MessageCircle, Sparkles } from 'lucide-react'
import { apiClient } from '../../lib/api-client'
import toast from 'react-hot-toast'

interface SearchResultItem {
  title: string
  url: string
  snippet: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  searchResults?: SearchResultItem[]
  searchPerformed?: boolean
  confidenceScore?: number
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your AI assistant at Galion Studio. I can help you with creative projects, content generation, and technical questions. Enable deep search to access our knowledge base for more accurate answers.',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [deepSearchEnabled, setDeepSearchEnabled] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Convert messages to API format
      const apiMessages = messages.concat(userMessage).map(msg => ({
        role: msg.role === 'assistant' ? 'assistant' : 'user',
        content: msg.content
      }))

      let response;
      if (deepSearchEnabled) {
        // Use deep search API
        response = await apiClient.deepSearch(apiMessages, input.trim())
      } else {
        // Use regular chat API
        response = await apiClient.chat(apiMessages)
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.content || 'I apologize, but I couldn\'t generate a response.',
        timestamp: new Date(),
        searchResults: response.search_results || [],
        searchPerformed: response.search_performed || false,
        confidenceScore: response.confidence_score || 0
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error: any) {
      toast.error('Failed to send message')
      console.error('Chat error:', error)

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">AI Chat</h1>
              <p className="text-zinc-400">
                Conversational AI for creative and technical assistance
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <Search className="h-4 w-4 text-zinc-400" />
                  <span className="text-sm font-medium text-zinc-300">Deep Search</span>
                  <button
                    onClick={() => setDeepSearchEnabled(!deepSearchEnabled)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      deepSearchEnabled ? 'bg-purple-600' : 'bg-zinc-700'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        deepSearchEnabled ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {deepSearchEnabled && (
            <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-3 text-purple-300 mb-2">
                <Search className="h-5 w-5" />
                <span className="font-medium">Deep Search Enabled</span>
                <Sparkles className="h-4 w-4" />
              </div>
              <p className="text-sm text-purple-200">
                AI responses will be enhanced with knowledge base search for more accurate and contextual answers.
              </p>
            </div>
          )}
        </div>

        {/* Chat Container */}
        <div className="bg-zinc-900/50 backdrop-blur border border-zinc-800 rounded-lg">
          <div className="border-b border-zinc-800 p-4">
            <h2 className="flex items-center gap-2 text-white text-lg font-semibold">
              <MessageCircle className="h-5 w-5" />
              AI Assistant
              {deepSearchEnabled && (
                <span className="text-xs bg-purple-600/20 text-purple-300 px-2 py-1 rounded-full border border-purple-500/30">
                  Deep Search Active
                </span>
              )}
            </h2>
          </div>

          <div className="p-0">
            {/* Messages */}
            <div className="h-[600px] overflow-y-auto p-6 space-y-6">
              {messages.map((message) => (
                <div key={message.id} className="space-y-4">
                  <div
                    className={`flex gap-4 ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-2xl p-4 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-purple-600 text-white'
                          : 'bg-zinc-800 text-zinc-100'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-3">
                        {message.role === 'user' ? (
                          <User className="h-4 w-4" />
                        ) : (
                          <Bot className="h-4 w-4" />
                        )}
                        <span className="text-xs opacity-70">
                          {message.timestamp.toLocaleTimeString()}
                        </span>
                        {message.role === 'assistant' && message.searchPerformed && (
                          <span className="text-xs bg-green-600/20 text-green-300 px-2 py-1 rounded-full">
                            Deep Search
                          </span>
                        )}
                      </div>
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                    </div>
                  </div>

                  {/* Search Results */}
                  {message.role === 'assistant' && message.searchResults && message.searchResults.length > 0 && (
                    <div className="ml-12 max-w-2xl">
                      <div className="space-y-2">
                        {message.searchResults.slice(0, 3).map((result, idx) => (
                          <div key={idx} className="p-3 bg-zinc-800/50 rounded border border-zinc-700 cursor-pointer hover:bg-zinc-700/50 transition-colors"
                               onClick={() => {
                                 navigator.clipboard.writeText(result.snippet)
                                 toast.success('Content copied to clipboard')
                               }}>
                            <div className="font-medium text-blue-300 text-sm">{result.title}</div>
                            <div className="text-xs text-zinc-400 mt-1">{result.url}</div>
                            <div className="text-sm text-zinc-300 mt-2">{result.snippet}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className="flex gap-4 justify-start">
                  <div className="bg-zinc-800 p-4 rounded-lg max-w-2xl">
                    <div className="flex items-center gap-3 mb-3">
                      <Bot className="h-4 w-4 text-zinc-400" />
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin text-purple-400" />
                        <span className="text-sm text-zinc-400">
                          {deepSearchEnabled ? 'Searching knowledge base...' : 'Thinking...'}
                        </span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="h-3 bg-zinc-700 rounded animate-pulse"></div>
                      <div className="h-3 bg-zinc-700 rounded animate-pulse w-3/4"></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-zinc-800 p-6">
              <div className="flex gap-3">
                <div className="flex-1">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={
                      deepSearchEnabled
                        ? "Ask me anything with deep search - I'll access our knowledge base..."
                        : "Ask me anything about creative projects, content, or technical topics..."
                    }
                    className="w-full px-4 py-3 bg-zinc-800 text-white rounded-lg border border-zinc-700 focus:border-purple-500 outline-none resize-none"
                    rows={3}
                    disabled={isLoading}
                  />
                  <div className="mt-2 text-xs text-zinc-500">
                    Press Enter to send • Shift+Enter for new line
                    {deepSearchEnabled && (
                      <span className="text-purple-400 ml-2">
                        • Deep search enabled (uses ~0.02 credits per 1k tokens)
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={sendMessage}
                  disabled={!input.trim() || isLoading}
                  className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-zinc-700 disabled:to-zinc-700 text-white rounded-lg transition flex items-center justify-center gap-2 self-end"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
