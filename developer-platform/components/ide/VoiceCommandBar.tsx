'use client'

import { useState, useEffect } from 'react'
import { Mic, MicOff, Command, ChevronDown, X } from 'lucide-react'
// Shared components removed for simplified deployment

interface VoiceCommand {
  id: string
  command: string
  description: string
  example: string
}

const voiceCommands: VoiceCommand[] = [
  {
    id: 'create-function',
    command: 'create function',
    description: 'Create a new function',
    example: 'create function calculateTotal'
  },
  {
    id: 'add-comment',
    command: 'add comment',
    description: 'Add documentation comments',
    example: 'add comment to fibonacci function'
  },
  {
    id: 'generate-test',
    command: 'generate test',
    description: 'Generate unit tests',
    example: 'generate test for login function'
  },
  {
    id: 'optimize-code',
    command: 'optimize code',
    description: 'Optimize performance',
    example: 'optimize code for better performance'
  },
  {
    id: 'explain-code',
    command: 'explain code',
    description: 'Explain selected code',
    example: 'explain the algorithm'
  },
  {
    id: 'find-bug',
    command: 'find bug',
    description: 'Find potential bugs',
    example: 'find bugs in this code'
  },
  {
    id: 'refactor-code',
    command: 'refactor code',
    description: 'Refactor for better readability',
    example: 'refactor this function'
  },
  {
    id: 'add-type',
    command: 'add type',
    description: 'Add TypeScript types',
    example: 'add types to parameters'
  }
]

interface VoiceCommandBarProps {
  isActive: boolean
  onToggle: () => void
  onCommand?: (command: VoiceCommand) => void
  className?: string
}

export function VoiceCommandBar({ isActive, onToggle, onCommand, className = '' }: VoiceCommandBarProps) {
  const [isListening, setIsListening] = useState(false)
  const [transcription, setTranscription] = useState('')
  const [suggestions, setSuggestions] = useState<VoiceCommand[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedSuggestion, setSelectedSuggestion] = useState(0)

  useEffect(() => {
    if (isActive && isListening) {
      // Simulate voice recognition
      const mockTranscriptions = [
        'create function',
        'add comment',
        'generate test',
        'optimize code',
        'explain code'
      ]

      const interval = setInterval(() => {
        const randomTranscription = mockTranscriptions[Math.floor(Math.random() * mockTranscriptions.length)]
        setTranscription(randomTranscription)

        // Filter suggestions based on transcription
        const filtered = voiceCommands.filter(cmd =>
          cmd.command.toLowerCase().includes(randomTranscription.toLowerCase()) ||
          cmd.description.toLowerCase().includes(randomTranscription.toLowerCase())
        )
        setSuggestions(filtered.slice(0, 3))
        setShowSuggestions(true)
      }, 2000)

      return () => clearInterval(interval)
    } else {
      setTranscription('')
      setSuggestions([])
      setShowSuggestions(false)
    }
  }, [isActive, isListening])

  const handleVoiceToggle = () => {
    if (!isActive) {
      onToggle()
    } else {
      setIsListening(!isListening)
    }
  }

  const handleSuggestionClick = (command: VoiceCommand) => {
    onCommand?.(command)
    setTranscription('')
    setSuggestions([])
    setShowSuggestions(false)
    setIsListening(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions) return

    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedSuggestion(prev => Math.min(prev + 1, suggestions.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedSuggestion(prev => Math.max(prev - 1, 0))
    } else if (e.key === 'Enter') {
      e.preventDefault()
      if (suggestions[selectedSuggestion]) {
        handleSuggestionClick(suggestions[selectedSuggestion])
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false)
      setSelectedSuggestion(0)
    }
  }

  return (
    <div className={`bg-surface border-b border-border px-4 py-3 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 flex-1">
          {/* Voice Toggle */}
          <VoiceButton
            size="small"
            state={isListening ? 'listening' : 'idle'}
            platform="developer"
            onClick={handleVoiceToggle}
          />

          {/* Status and Transcription */}
          <div className="flex-1">
            {isActive ? (
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${isListening ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
                  <span className="text-sm font-medium text-foreground">
                    {isListening ? 'Listening...' : 'Voice commands ready'}
                  </span>
                </div>

                {transcription && (
                  <div className="flex items-center space-x-2 text-sm">
                    <span className="text-foreground-muted">Heard:</span>
                    <span className="bg-surface-hover px-2 py-1 rounded text-foreground font-medium">
                      "{transcription}"
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Command className="w-4 h-4 text-foreground-muted" />
                <span className="text-sm text-foreground-muted">
                  Voice commands disabled. Click the microphone to enable.
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Help/Commands Button */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowSuggestions(!showSuggestions)}
            className="flex items-center space-x-2 px-3 py-1.5 bg-surface-hover hover:bg-surface-active rounded-md transition-colors text-sm"
          >
            <span>Commands</span>
            <ChevronDown className={`w-4 h-4 transition-transform ${showSuggestions ? 'rotate-180' : ''}`} />
          </button>
        </div>
      </div>

      {/* Suggestions Dropdown */}
      {showSuggestions && (
        <div className="mt-3 bg-surface-hover rounded-lg border border-border p-3 max-h-64 overflow-y-auto">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-foreground">Voice Commands</h4>
            <button
              onClick={() => setShowSuggestions(false)}
              className="text-foreground-muted hover:text-foreground"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-2">
            {suggestions.map((command, index) => (
              <button
                key={command.id}
                onClick={() => handleSuggestionClick(command)}
                onKeyDown={handleKeyDown}
                className={`w-full text-left p-3 rounded-md transition-colors ${
                  index === selectedSuggestion
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-surface hover:bg-surface-active'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-medium text-sm">{command.command}</div>
                    <div className="text-xs text-foreground-muted mt-1">
                      {command.description}
                    </div>
                  </div>
                  <div className="text-xs text-foreground-muted ml-4">
                    Example: {command.example}
                  </div>
                </div>
              </button>
            ))}

            {suggestions.length === 0 && (
              <div className="text-center py-4">
                <p className="text-sm text-foreground-muted">
                  No matching commands found. Try saying "help" for available commands.
                </p>
              </div>
            )}
          </div>

          {/* All Commands */}
          <div className="mt-4 pt-3 border-t border-border">
            <h5 className="text-xs font-medium text-foreground-muted uppercase tracking-wide mb-2">
              All Available Commands
            </h5>
            <div className="grid grid-cols-2 gap-2">
              {voiceCommands.map((command) => (
                <button
                  key={command.id}
                  onClick={() => handleSuggestionClick(command)}
                  className="text-left px-2 py-1 text-xs bg-surface hover:bg-surface-active rounded transition-colors"
                >
                  {command.command}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Keyboard shortcuts hint */}
      <div className="mt-2 text-xs text-foreground-muted">
        Press ↑↓ to navigate suggestions, Enter to select, Esc to close
      </div>
    </div>
  )
}

export default VoiceCommandBar