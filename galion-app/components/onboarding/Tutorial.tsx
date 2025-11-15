'use client'

import { useState, useEffect } from 'react'
import { Mic, Volume2, MessageSquare, X, CheckCircle } from 'lucide-react'
import { VoiceButton } from '@/shared/components/ui/VoiceButton'
import { VoiceWaveform } from '@/components/voice/VoiceWaveform'
import { LoadingStates } from '@/shared/components/ui/LoadingStates'

interface TutorialProps {
  onComplete: () => void
  onSkip: () => void
}

const tutorialSteps = [
  {
    id: 'intro',
    title: 'Voice Interaction Tutorial',
    content: 'Let\'s learn how to use Galion with voice. Click the microphone button and say "Hello" or any greeting.',
    instruction: 'Try saying: "Hello Galion"',
    icon: Mic,
    action: 'Start Listening'
  },
  {
    id: 'listening',
    title: 'Listening for Your Voice',
    content: 'Great! Now speak clearly into your microphone. Galion will transcribe what you say in real-time.',
    instruction: 'The waveform shows your voice activity',
    icon: Volume2,
    action: 'Speak Now'
  },
  {
    id: 'response',
    title: 'AI Response',
    content: 'Perfect! Galion heard you and will respond. You can also type messages or continue speaking.',
    instruction: 'Galion responds with voice and text',
    icon: MessageSquare,
    action: 'Continue'
  },
  {
    id: 'complete',
    title: 'Tutorial Complete!',
    content: 'You\'ve successfully learned the basics of voice interaction with Galion. You can now use voice or text anytime.',
    instruction: 'Ready to explore Galion fully',
    icon: CheckCircle,
    action: 'Finish Tutorial'
  }
]

export function Tutorial({ onComplete, onSkip }: TutorialProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [isListening, setIsListening] = useState(false)
  const [hasHeardSpeech, setHasHeardSpeech] = useState(false)
  const [volume, setVolume] = useState(0)
  const [transcription, setTranscription] = useState('')

  const currentStepData = tutorialSteps[currentStep]
  const IconComponent = currentStepData.icon

  useEffect(() => {
    // Simulate voice interaction for tutorial
    if (currentStep === 1 && !isListening) {
      // Auto-start listening simulation
      setTimeout(() => {
        setIsListening(true)
        simulateVoiceInteraction()
      }, 1000)
    }
  }, [currentStep, isListening])

  const simulateVoiceInteraction = () => {
    // Simulate voice detection
    setTimeout(() => {
      setVolume(30)
      setTranscription('Hello...')
    }, 500)

    setTimeout(() => {
      setVolume(60)
      setTranscription('Hello Galion')
    }, 1000)

    setTimeout(() => {
      setVolume(20)
      setTranscription('Hello Galion!')
      setHasHeardSpeech(true)
    }, 1500)

    setTimeout(() => {
      setIsListening(false)
      setVolume(0)
      handleNext()
    }, 2000)
  }

  const handleNext = () => {
    if (currentStep < tutorialSteps.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      onComplete()
    }
  }

  const handleAction = () => {
    if (currentStep === 0) {
      setCurrentStep(1)
    } else if (currentStep === 2) {
      handleNext()
    } else if (currentStep === 3) {
      onComplete()
    }
  }

  return (
    <div className="fixed inset-0 bg-background/95 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-surface rounded-lg shadow-2xl max-w-md w-full p-6 relative">
        {/* Close button */}
        <button
          onClick={onSkip}
          className="absolute top-4 right-4 text-foreground-muted hover:text-foreground transition-colors"
          aria-label="Skip tutorial"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Progress indicator */}
        <div className="mb-6">
          <div className="flex items-center space-x-2 mb-2">
            {tutorialSteps.map((step, index) => (
              <div
                key={step.id}
                className={`flex-1 h-1 rounded-full transition-colors ${
                  index <= currentStep ? 'bg-primary' : 'bg-border'
                }`}
              />
            ))}
          </div>
          <p className="text-xs text-foreground-muted text-center">
            Tutorial Step {currentStep + 1} of {tutorialSteps.length}
          </p>
        </div>

        {/* Icon */}
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
            <IconComponent className={`w-8 h-8 text-primary ${
              currentStep === 1 && isListening ? 'animate-pulse' : ''
            }`} />
          </div>
        </div>

        {/* Content */}
        <div className="text-center space-y-4 mb-6">
          <h2 className="text-xl font-semibold text-foreground">
            {currentStepData.title}
          </h2>
          <p className="text-foreground-muted">
            {currentStepData.content}
          </p>

          {/* Voice interaction demo */}
          {currentStep === 1 && (
            <div className="space-y-4 py-4">
              <VoiceWaveform
                isActive={isListening}
                volume={volume}
                className="w-full h-12"
              />
              {transcription && (
                <div className="bg-surface-hover rounded-lg p-3">
                  <p className="text-sm text-foreground">
                    "{transcription}"
                  </p>
                </div>
              )}
              {isListening && !hasHeardSpeech && (
                <p className="text-xs text-primary animate-pulse">
                  Listening for your voice...
                </p>
              )}
            </div>
          )}

          {/* AI Response demo */}
          {currentStep === 2 && (
            <div className="space-y-4 py-4">
              <div className="bg-primary/10 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                    <MessageSquare className="w-3 h-3 text-primary-foreground" />
                  </div>
                  <span className="text-xs text-primary font-medium">Galion</span>
                </div>
                <p className="text-sm text-foreground">
                  "Hello! I'm Galion, your AI assistant. It's great to meet you!"
                </p>
              </div>
              <div className="flex justify-center">
                <VoiceButton
                  size="small"
                  state="speaking"
                  platform="galion-app"
                />
              </div>
            </div>
          )}

          {/* Completion checkmark */}
          {currentStep === 3 && (
            <div className="py-4">
              <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-2" />
            </div>
          )}

          <p className="text-sm text-primary font-medium">
            {currentStepData.instruction}
          </p>
        </div>

        {/* Action button */}
        <div className="flex justify-center">
          <button
            onClick={handleAction}
            disabled={currentStep === 1 && !hasHeardSpeech && isListening}
            className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          >
            {currentStep === 1 && isListening ? (
              <div className="flex items-center space-x-2">
                <LoadingStates type="spinner" size="sm" />
                <span>Listening...</span>
              </div>
            ) : (
              currentStepData.action
            )}
          </button>
        </div>

        {/* Skip option */}
        <div className="text-center mt-4">
          <button
            onClick={onSkip}
            className="text-xs text-foreground-muted hover:text-foreground underline underline-offset-2 transition-colors"
          >
            Skip tutorial
          </button>
        </div>
      </div>
    </div>
  )
}