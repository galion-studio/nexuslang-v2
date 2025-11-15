'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { CheckCircle, Mic, MessageSquare, Zap, ArrowRight, ArrowLeft } from 'lucide-react'
import { VoiceButton } from '@/shared/components/ui/VoiceButton'
import { LoadingStates } from '@/shared/components/ui/LoadingStates'
import { Tutorial } from '@/components/onboarding/Tutorial'

const onboardingSteps = [
  {
    id: 'welcome',
    title: 'Welcome to Galion',
    subtitle: '"Your imagination is the end."',
    content: 'You\'re about to experience the future of AI interaction. Galion is designed to understand you naturally through voice and text.',
    icon: MessageSquare,
    action: 'Get Started'
  },
  {
    id: 'voice-intro',
    title: 'Voice-First Experience',
    subtitle: 'Speak naturally, get instant responses',
    content: 'Galion understands context, remembers conversations, and responds with human-like intelligence. Just speak or type - whatever feels right.',
    icon: Mic,
    action: 'Try Voice'
  },
  {
    id: 'features',
    title: 'Powerful Features',
    subtitle: 'Everything you need, nothing you don\'t',
    content: 'From creative writing to complex problem-solving, Galion adapts to your needs. Voice commands, file uploads, code generation - all in one place.',
    icon: Zap,
    action: 'Explore Features'
  },
  {
    id: 'ready',
    title: 'You\'re All Set!',
    subtitle: 'Ready to start your journey',
    content: 'Galion learns from every interaction to better serve you. Your privacy and data security are our top priorities.',
    icon: CheckCircle,
    action: 'Start Using Galion'
  }
]

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(0)
  const [showTutorial, setShowTutorial] = useState(false)
  const [isCompleting, setIsCompleting] = useState(false)
  const router = useRouter()

  const currentStepData = onboardingSteps[currentStep]
  const IconComponent = currentStepData.icon

  useEffect(() => {
    // Check if user has already completed onboarding
    const completed = localStorage.getItem('galion-onboarding-completed')
    if (completed === 'true') {
      router.push('/voice')
      return
    }
  }, [router])

  const handleNext = () => {
    if (currentStep < onboardingSteps.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      completeOnboarding()
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleTryVoice = () => {
    setShowTutorial(true)
  }

  const completeOnboarding = async () => {
    setIsCompleting(true)

    // Simulate completion delay
    setTimeout(() => {
      localStorage.setItem('galion-onboarding-completed', 'true')
      router.push('/voice')
    }, 1500)
  }

  const handleAction = () => {
    if (currentStepData.id === 'voice-intro') {
      handleTryVoice()
    } else {
      handleNext()
    }
  }

  if (showTutorial) {
    return (
      <Tutorial
        onComplete={() => {
          setShowTutorial(false)
          handleNext()
        }}
        onSkip={() => {
          setShowTutorial(false)
          handleNext()
        }}
      />
    )
  }

  if (isCompleting) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <LoadingStates type="spinner" size="lg" />
          <h2 className="text-xl font-semibold text-foreground">
            Setting up your Galion experience...
          </h2>
          <p className="text-foreground-muted">
            This will only take a moment
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Progress Indicator */}
      <div className="fixed top-0 left-0 right-0 z-50">
        <div className="bg-surface border-b border-border">
          <div className="max-w-md mx-auto px-4 py-3">
            <div className="flex items-center space-x-2">
              {onboardingSteps.map((step, index) => (
                <div
                  key={step.id}
                  className={`flex-1 h-1 rounded-full transition-colors ${
                    index <= currentStep ? 'bg-primary' : 'bg-border'
                  }`}
                />
              ))}
            </div>
            <p className="text-xs text-foreground-muted text-center mt-2">
              Step {currentStep + 1} of {onboardingSteps.length}
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="pt-20 pb-8 px-4 min-h-screen flex items-center justify-center">
        <div className="max-w-md mx-auto text-center space-y-8">
          {/* Icon */}
          <div className="flex justify-center">
            <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center">
              <IconComponent className="w-10 h-10 text-primary" />
            </div>
          </div>

          {/* Content */}
          <div className="space-y-4">
            <h1 className="text-2xl font-bold text-foreground">
              {currentStepData.title}
            </h1>
            <h2 className="text-lg text-primary italic">
              {currentStepData.subtitle}
            </h2>
            <p className="text-foreground-muted leading-relaxed">
              {currentStepData.content}
            </p>
          </div>

          {/* Interactive Element */}
          {currentStepData.id === 'voice-intro' && (
            <div className="py-8">
              <div className="flex justify-center mb-4">
                <VoiceButton
                  size="large"
                  platform="galion-app"
                  onClick={() => setShowTutorial(true)}
                />
              </div>
              <p className="text-sm text-foreground-muted">
                Click the button above to try voice interaction
              </p>
            </div>
          )}

          {currentStepData.id === 'features' && (
            <div className="py-6">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="bg-surface-hover rounded-lg p-3">
                  <Mic className="w-5 h-5 text-primary mx-auto mb-2" />
                  <p className="text-foreground">Voice Commands</p>
                </div>
                <div className="bg-surface-hover rounded-lg p-3">
                  <Zap className="w-5 h-5 text-primary mx-auto mb-2" />
                  <p className="text-foreground">AI Responses</p>
                </div>
                <div className="bg-surface-hover rounded-lg p-3">
                  <MessageSquare className="w-5 h-5 text-primary mx-auto mb-2" />
                  <p className="text-foreground">Chat History</p>
                </div>
                <div className="bg-surface-hover rounded-lg p-3">
                  <CheckCircle className="w-5 h-5 text-primary mx-auto mb-2" />
                  <p className="text-foreground">Context Aware</p>
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between pt-4">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 0}
              className="flex items-center space-x-2 px-4 py-2 text-foreground-muted hover:text-foreground disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              onClick={handleAction}
              className="flex items-center space-x-2 px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary-hover transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
            >
              <span>{currentStepData.action}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Skip Option */}
      <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2">
        <button
          onClick={completeOnboarding}
          className="text-xs text-foreground-muted hover:text-foreground underline underline-offset-2 transition-colors"
        >
          Skip onboarding
        </button>
      </div>
    </div>
  )
}