'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Search, ToggleLeft, ToggleRight } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { developerAPI } from '@/lib/api-client'
import { SearchResults, SearchResultItem } from '../../../../shared/components/SearchResults'
import toast from 'react-hot-toast'

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
      content: 'Hello! I\'m your AI assistant. I can help you with coding, debugging, architecture decisions, and technical questions. Enable deep search to access our knowledge base for more accurate answers.',
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
        response = await developerAPI.sendDeepSearchMessage(apiMessages, input.trim())
      } else {
        // Use regular chat API
        response = await developerAPI.sendChatMessage(apiMessages)
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
    <div className="h-screen flex flex-col">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">AI Chat</h1>
            <p className="text-muted-foreground">
              Conversational AI assistant for coding, debugging, and technical guidance
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Search className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Deep Search</span>
              <button
                onClick={() => setDeepSearchEnabled(!deepSearchEnabled)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  deepSearchEnabled ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
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
        {deepSearchEnabled && (
          <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="flex items-center gap-2 text-blue-900 dark:text-blue-100">
              <Search className="h-4 w-4" />
              <span className="text-sm font-medium">Deep Search Enabled</span>
            </div>
            <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">
              AI responses will be enhanced with knowledge base search for more accurate and contextual answers.
            </p>
          </div>
        )}
      </div>

      {/* Chat Container */}
      <Card className="flex-1 flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            AI Assistant
          </CardTitle>
        </CardHeader>

        <CardContent className="flex-1 flex flex-col p-0">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div key={message.id} className="space-y-3">
                <div
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-2xl p-4 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      {message.role === 'user' ? (
                        <User className="h-4 w-4" />
                      ) : (
                        <Bot className="h-4 w-4" />
                      )}
                      <span className="text-xs opacity-70">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                      {message.role === 'assistant' && message.searchPerformed && (
                        <span className="text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded-full">
                          Deep Search
                        </span>
                      )}
                    </div>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>

                {/* Search Results */}
                {message.role === 'assistant' && message.searchResults && message.searchResults.length > 0 && (
                  <div className="ml-12">
                    <SearchResults
                      results={message.searchResults}
                      maxDisplay={3}
                      onResultClick={(result) => {
                        // Handle result click - could open document or copy to clipboard
                        navigator.clipboard.writeText(result.content)
                        toast.success('Content copied to clipboard')
                      }}
                    />
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-3 justify-start">
                <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Bot className="h-4 w-4" />
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">Thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t p-4">
            <div className="flex gap-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  deepSearchEnabled
                    ? "Ask me anything with deep search - I'll access our knowledge base for more accurate answers..."
                    : "Ask me anything about coding, debugging, architecture, or technical topics..."
                }
                className="flex-1 p-3 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                rows={3}
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition flex items-center gap-2"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>

            <div className="mt-2 text-xs text-muted-foreground">
              Press Enter to send • Shift+Enter for new line
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
