'use client'

import { useState, useEffect } from 'react'
import { VoiceButton } from '@/shared/components/ui/VoiceButton'
import { LoadingStates } from '@/shared/components/ui/LoadingStates'

interface VoiceActivationProps {
  onActivate: () => void
}

export function VoiceActivation({ onActivate }: VoiceActivationProps) {
  const [isHovered, setIsHovered] = useState(false)
  const [showGreeting, setShowGreeting] = useState(false)

  useEffect(() => {
    // Show greeting after a short delay
    const timer = setTimeout(() => {
      setShowGreeting(true)
    }, 500)

    return () => clearTimeout(timer)
  }, [])

  const handleActivate = () => {
    // Add a small delay for visual feedback
    setTimeout(() => {
      onActivate()
    }, 300)
  }

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background gradient effect */}
      <div className="absolute inset-0 bg-gradient-radial from-primary/10 via-transparent to-transparent opacity-50" />

      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden">
        {Array.from({ length: 20 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-primary/20 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 3}s`
            }}
          />
        ))}
      </div>

      <div className="relative z-10 flex flex-col items-center space-y-8 max-w-md mx-auto text-center">
        {/* Slogan */}
        <div
          className={`transition-all duration-1000 ${
            showGreeting ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
          }`}
        >
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-display font-bold italic text-primary mb-4 animate-fade-in">
            "Your imagination is the end."
          </h1>
          <p className="text-lg text-foreground-muted mb-8">
            Welcome to Galion, the voice-first AI platform
          </p>
        </div>

        {/* Voice Button */}
        <div
          className={`transition-all duration-1000 delay-300 ${
            showGreeting ? 'opacity-100 scale-100' : 'opacity-0 scale-95'
          }`}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <VoiceButton
            size="xl"
            platform="galion-app"
            onClick={handleActivate}
            className="mb-6"
          />

          {/* Button hint */}
          <div className={`transition-opacity duration-300 ${isHovered ? 'opacity-100' : 'opacity-70'}`}>
            <p className="text-foreground-muted text-sm">
              Click to start your voice journey
            </p>
          </div>
        </div>

        {/* Features preview */}
        <div
          className={`transition-all duration-1000 delay-500 ${
            showGreeting ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}
        >
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-12">
            <div className="text-center">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-2">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </div>
              <p className="text-sm text-foreground-muted">Voice-First</p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-2">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <p className="text-sm text-foreground-muted">Lightning Fast</p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-2">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <p className="text-sm text-foreground-muted">AI Powered</p>
            </div>
          </div>
        </div>

        {/* Skip onboarding link */}
        <div
          className={`transition-all duration-1000 delay-700 ${
            showGreeting ? 'opacity-100' : 'opacity-0'
          }`}
        >
          <button
            onClick={handleActivate}
            className="text-xs text-foreground-muted hover:text-foreground transition-colors underline underline-offset-2"
          >
            Skip introduction
          </button>
        </div>
      </div>

      {/* Accessibility: Skip link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary text-primary-foreground px-4 py-2 rounded-md z-50"
      >
        Skip to main content
      </a>
    </div>
  )
}