'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { CheckCircle, ArrowRight, Mic, Code, Settings, MessageSquare, Star, Gift, Users, Zap, X } from 'lucide-react'
import { Button } from '../../shared/ui'

interface BetaProfile {
  beta_tier: string
  special_access_features: string[]
}

interface OnboardingStep {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  completed: boolean
  action?: () => void
}

export function BetaOnboarding({ onComplete }: { onComplete?: () => void }) {
  const [currentStep, setCurrentStep] = useState(0)
  const [profile, setProfile] = useState<BetaProfile | null>(null)
  const [feedbackRating, setFeedbackRating] = useState<number>(0)
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set())
  const router = useRouter()

  useEffect(() => {
    loadBetaProfile()
  }, [])

  const loadBetaProfile = async () => {
    try {
      const response = await fetch('/api/v2/beta/profile')
      if (response.ok) {
        const data = await response.json()
        setProfile(data)
      }
    } catch (error) {
      console.error('Failed to load beta profile:', error)
    }
  }

  const steps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: 'Welcome to Galion Beta!',
      description: 'Congratulations on joining our exclusive beta program. Let\'s get you set up for an amazing experience.',
      icon: <Gift className="w-6 h-6" />,
      completed: completedSteps.has('welcome'),
    },
    {
      id: 'voice_setup',
      title: 'Try Voice Commands',
      description: 'Experience our revolutionary voice-first interface. Click the microphone and say "Show my dashboard" or "Help me get started".',
      icon: <Mic className="w-6 h-6" />,
      completed: completedSteps.has('voice_setup'),
      action: () => router.push('/dashboard'),
    },
    {
      id: 'explore_features',
      title: 'Explore Key Features',
      description: 'Take a tour of our main features: Voice AI assistant, NexusLang code execution, and multi-platform integration.',
      icon: <Zap className="w-6 h-6" />,
      completed: completedSteps.has('explore_features'),
      action: () => router.push('/features'),
    },
    {
      id: 'feedback_initial',
      title: 'Share Your First Thoughts',
      description: 'Help us improve by sharing your initial impressions and expectations for the platform.',
      icon: <MessageSquare className="w-6 h-6" />,
      completed: completedSteps.has('feedback_initial'),
    },
    {
      id: 'customization',
      title: 'Customize Your Experience',
      description: 'Set up your preferences, voice settings, and personalize your AI assistant behavior.',
      icon: <Settings className="w-6 h-6" />,
      completed: completedSteps.has('customization'),
      action: () => router.push('/settings'),
    },
    {
      id: 'community',
      title: 'Join the Community',
      description: 'Connect with other beta users, share experiences, and contribute to our growing community.',
      icon: <Users className="w-6 h-6" />,
      completed: completedSteps.has('community'),
    },
  ]

  const submitInitialFeedback = async () => {
    if (feedbackRating === 0) return

    try {
      await fetch('/api/v2/beta/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          feedback_type: 'satisfaction',
          rating: feedbackRating,
          comments: `Initial beta onboarding feedback: ${feedbackRating}/5 stars`,
          metadata: {
            onboarding_step: 'initial_feedback',
            beta_tier: profile?.beta_tier,
          },
        }),
      })

      markStepCompleted('feedback_initial')
    } catch (error) {
      console.error('Failed to submit feedback:', error)
    }
  }

  const markStepCompleted = (stepId: string) => {
    setCompletedSteps(prev => new Set(prev).add(stepId))
  }

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      completeOnboarding()
    }
  }

  const completeOnboarding = () => {
    // Mark all remaining steps as completed
    const allStepIds = new Set(steps.map(step => step.id))
    setCompletedSteps(allStepIds)

    // Call completion callback
    onComplete?.()
  }

  const currentStepData = steps[currentStep]
  const allStepsCompleted = steps.every(step => completedSteps.has(step.id))

  if (!profile) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-300 rounded w-3/4 mx-auto"></div>
            <div className="h-4 bg-gray-300 rounded w-1/2 mx-auto"></div>
            <div className="h-32 bg-gray-300 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                <Star className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Welcome to Galion Beta!</h2>
                <p className="text-gray-600">
                  {profile.beta_tier.charAt(0).toUpperCase() + profile.beta_tier.slice(1)} Tier
                </p>
              </div>
            </div>
            <button
              onClick={onComplete}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Setup Progress</span>
            <span>{completedSteps.size} of {steps.length} completed</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(completedSteps.size / steps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Beta Tier Benefits */}
        <div className="px-6 pb-4">
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4">
            <div className="flex items-center space-x-2 mb-2">
              <Gift className="w-5 h-5 text-purple-600" />
              <span className="font-medium text-purple-900">
                {profile.beta_tier.charAt(0).toUpperCase() + profile.beta_tier.slice(1)} Benefits
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {profile.special_access_features.map((feature, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-purple-100 text-purple-700 text-xs rounded-full"
                >
                  {feature.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Current Step */}
        <div className="px-6 pb-6">
          <div className="bg-gray-50 rounded-xl p-6">
            <div className="flex items-start space-x-4">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                {currentStepData.icon}
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {currentStepData.title}
                </h3>
                <p className="text-gray-600 mb-4">
                  {currentStepData.description}
                </p>

                {/* Step-specific content */}
                {currentStepData.id === 'feedback_initial' && (
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-2">How excited are you about Galion?</p>
                      <div className="flex space-x-2">
                        {[1, 2, 3, 4, 5].map((rating) => (
                          <button
                            key={rating}
                            onClick={() => setFeedbackRating(rating)}
                            className={`w-10 h-10 rounded-lg border-2 transition-colors ${
                              feedbackRating >= rating
                                ? 'bg-yellow-400 border-yellow-400 text-white'
                                : 'border-gray-300 hover:border-yellow-300'
                            }`}
                          >
                            {rating}
                          </button>
                        ))}
                      </div>
                    </div>
                    {feedbackRating > 0 && (
                      <Button onClick={submitInitialFeedback}>
                        Submit Feedback
                      </Button>
                    )}
                  </div>
                )}

                {currentStepData.id !== 'feedback_initial' && (
                  <div className="flex space-x-3">
                    {currentStepData.action && (
                      <Button onClick={currentStepData.action}>
                        {currentStepData.title.includes('Explore') ? 'Start Tour' :
                         currentStepData.title.includes('Customize') ? 'Open Settings' :
                         currentStepData.title.includes('Voice') ? 'Try Voice Commands' :
                         'Get Started'}
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      onClick={() => markStepCompleted(currentStepData.id)}
                    >
                      Mark as Done
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Step Indicators */}
        <div className="px-6 pb-6">
          <div className="flex justify-center space-x-2">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={`w-3 h-3 rounded-full transition-colors ${
                  index < currentStep
                    ? 'bg-green-500'
                    : index === currentStep
                    ? 'bg-blue-500'
                    : 'bg-gray-300'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Step {currentStep + 1} of {steps.length}
          </div>

          <div className="flex space-x-3">
            {currentStep > 0 && (
              <Button
                variant="outline"
                onClick={() => setCurrentStep(currentStep - 1)}
              >
                Previous
              </Button>
            )}

            <Button
              onClick={nextStep}
              disabled={
                currentStepData.id === 'feedback_initial' && feedbackRating === 0
              }
              leftIcon={allStepsCompleted ? <CheckCircle className="w-4 h-4" /> : <ArrowRight className="w-4 h-4" />}
            >
              {allStepsCompleted ? 'Complete Setup' : 'Next Step'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
