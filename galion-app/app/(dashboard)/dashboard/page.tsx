'use client'

import { useEffect, useState } from 'react'
import { VoiceInterface } from '@/components/voice/VoiceInterface'
import { VoiceStatus } from '@/components/voice/VoiceStatus'
import { ChatInterface } from '@/components/chat/ChatInterface'
import { galionAPI } from '@/lib/api-client'
import { MessageCircle, Mic, BarChart3, Settings, User } from 'lucide-react'

interface User {
  id: string
  email: string
  name?: string
  credits: number
  subscriptionTier: string
}

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null)
  const [showChat, setShowChat] = useState(false)
  const [isVoiceActive, setIsVoiceActive] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUserData()
  }, [])

  const loadUserData = async () => {
    try {
      const userData = await galionAPI.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error('Failed to load user data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleVoiceStateChange = (listening: boolean, processing: boolean) => {
    setIsVoiceActive(listening)
    setIsProcessing(processing)
  }

  const handleTranscription = async (text: string, isFinal: boolean) => {
    if (isFinal && text.trim()) {
      // Process the voice command
      try {
        await galionAPI.sendVoiceCommand(text)
        // The voice interface will handle TTS response
      } catch (error) {
        console.error('Failed to process voice command:', error)
      }
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white/70">Loading Galion...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-black/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                  <Mic className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-semibold">Galion</span>
              </div>
              <div className="text-center">
                <p className="text-sm text-white/60 italic">"Your imagination is the end."</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Voice Status */}
              <VoiceStatus
                isActive={isVoiceActive}
                isProcessing={isProcessing}
                className="hidden sm:flex"
              />

              {/* User Info */}
              {user && (
                <div className="flex items-center space-x-3 text-sm">
                  <div className="text-right hidden sm:block">
                    <p className="font-medium">{user.name || user.email}</p>
                    <p className="text-white/60">{user.credits} credits</p>
                  </div>
                  <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                </div>
              )}

              {/* Navigation */}
              <nav className="flex items-center space-x-2">
                <button
                  onClick={() => setShowChat(!showChat)}
                  className={`p-2 rounded-lg transition-colors ${
                    showChat
                      ? 'bg-blue-500/20 text-blue-400'
                      : 'text-white/60 hover:text-white hover:bg-white/10'
                  }`}
                  title={showChat ? 'Hide Chat' : 'Show Chat'}
                >
                  <MessageCircle className="w-5 h-5" />
                </button>

                <button
                  className="p-2 text-white/60 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                  title="Analytics"
                >
                  <BarChart3 className="w-5 h-5" />
                </button>

                <button
                  className="p-2 text-white/60 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                  title="Settings"
                >
                  <Settings className="w-5 h-5" />
                </button>
              </nav>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Voice-First Interface */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Welcome to Galion
            </h1>
            <p className="text-xl text-white/70 mb-8">
              Your voice-powered AI assistant is ready to help
            </p>

            {/* Voice Interface */}
            <div className="max-w-2xl mx-auto">
              <VoiceInterface
                autoStart={true}
                onTranscription={handleTranscription}
                onStateChange={handleVoiceStateChange}
                className="bg-black/20 backdrop-blur-sm rounded-2xl border border-white/10 p-8"
              />
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-black/20 backdrop-blur-sm rounded-xl border border-white/10 p-6 hover:bg-black/30 transition-colors cursor-pointer group">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">View Analytics</h3>
              <p className="text-white/60">Check your usage statistics and performance metrics</p>
            </div>

            <div className="bg-black/20 backdrop-blur-sm rounded-xl border border-white/10 p-6 hover:bg-black/30 transition-colors cursor-pointer group">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Settings className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Customize Settings</h3>
              <p className="text-white/60">Adjust your voice preferences and AI behavior</p>
            </div>

            <div className="bg-black/20 backdrop-blur-sm rounded-xl border border-white/10 p-6 hover:bg-black/30 transition-colors cursor-pointer group">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <User className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Manage Account</h3>
              <p className="text-white/60">Update your profile and billing information</p>
            </div>
          </div>
        </div>

        {/* Chat Window Overlay */}
        {showChat && (
          <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="w-full max-w-4xl h-[80vh] bg-slate-900 rounded-xl border border-white/10 overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b border-white/10">
                <h3 className="text-lg font-semibold">Chat Assistant</h3>
                <button
                  onClick={() => setShowChat(false)}
                  className="p-2 text-white/60 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="flex-1 overflow-hidden">
                <ChatInterface />
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
