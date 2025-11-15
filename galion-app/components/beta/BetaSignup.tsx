'use client'

import { useState } from 'react'
import { Mail, CheckCircle, Clock, Users, ArrowRight } from 'lucide-react'
import { LoadingStates } from '@/shared/components/ui/LoadingStates'

interface BetaSignupProps {
  onSignup?: (email: string) => Promise<void>
  className?: string
}

export function BetaSignup({ onSignup, className = '' }: BetaSignupProps) {
  const [email, setEmail] = useState('')
  const [invitationCode, setInvitationCode] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [error, setError] = useState('')
  const [waitlistPosition, setWaitlistPosition] = useState<number | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return

    setIsSubmitting(true)
    setError('')

    try {
      await onSignup?.(email)

      // Simulate API response
      setTimeout(() => {
        const position = Math.floor(Math.random() * 1000) + 1
        setWaitlistPosition(position)
        setIsSuccess(true)
        setIsSubmitting(false)
      }, 1500)
    } catch (err: any) {
      setError(err.message || 'Failed to join waitlist')
      setIsSubmitting(false)
    }
  }

  const handleInvitationSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!invitationCode.trim()) return

    setIsSubmitting(true)
    setError('')

    try {
      // Simulate invitation code validation
      setTimeout(() => {
        setIsSuccess(true)
        setIsSubmitting(false)
      }, 1000)
    } catch (err: any) {
      setError('Invalid invitation code')
      setIsSubmitting(false)
    }
  }

  if (isSuccess && waitlistPosition) {
    return (
      <div className={`bg-surface rounded-lg p-6 text-center ${className}`}>
        <div className="flex justify-center mb-4">
          <CheckCircle className="w-12 h-12 text-green-500" />
        </div>
        <h3 className="text-lg font-semibold text-foreground mb-2">
          You're on the waitlist!
        </h3>
        <p className="text-foreground-muted mb-4">
          Thanks for your interest in Galion. We'll send you an invitation soon.
        </p>
        <div className="bg-primary/10 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-center space-x-2">
            <Users className="w-5 h-5 text-primary" />
            <span className="font-medium text-primary">
              Position #{waitlistPosition.toLocaleString()}
            </span>
          </div>
          <p className="text-sm text-foreground-muted mt-1">
            Estimated wait time: 2-4 weeks
          </p>
        </div>
        <p className="text-xs text-foreground-muted">
          Check your email for updates and exclusive beta access.
        </p>
      </div>
    )
  }

  return (
    <div className={`bg-surface rounded-lg p-6 ${className}`}>
      <div className="text-center mb-6">
        <h2 className="text-xl font-semibold text-foreground mb-2">
          Join the Galion Beta
        </h2>
        <p className="text-foreground-muted">
          Be among the first to experience the future of AI interaction
        </p>
      </div>

      {/* Invitation Code Section */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-3">
          <Mail className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium text-foreground">Have an invitation code?</span>
        </div>
        <form onSubmit={handleInvitationSubmit} className="space-y-3">
          <input
            type="text"
            value={invitationCode}
            onChange={(e) => setInvitationCode(e.target.value.toUpperCase())}
            placeholder="Enter invitation code"
            className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={isSubmitting}
            maxLength={8}
          />
          <button
            type="submit"
            disabled={!invitationCode.trim() || isSubmitting}
            className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          >
            {isSubmitting ? (
              <LoadingStates type="spinner" size="sm" />
            ) : (
              'Redeem Code'
            )}
          </button>
        </form>
      </div>

      {/* Divider */}
      <div className="relative mb-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-surface text-foreground-muted">or</span>
        </div>
      </div>

      {/* Email Signup Section */}
      <div>
        <div className="flex items-center space-x-2 mb-3">
          <Clock className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium text-foreground">Join the waitlist</span>
        </div>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email address"
            className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={isSubmitting}
            required
          />
          <button
            type="submit"
            disabled={!email.trim() || isSubmitting}
            className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          >
            {isSubmitting ? (
              <LoadingStates type="spinner" size="sm" />
            ) : (
              <>
                Join Waitlist
                <ArrowRight className="w-4 h-4 ml-2" />
              </>
            )}
          </button>
        </form>

        {error && (
          <p className="text-sm text-error mt-2">{error}</p>
        )}

        <p className="text-xs text-foreground-muted mt-3">
          By joining, you agree to receive updates about Galion. We respect your privacy and will never spam you.
        </p>
      </div>

      {/* Benefits */}
      <div className="mt-6 pt-6 border-t border-border">
        <h4 className="text-sm font-medium text-foreground mb-3">Beta benefits:</h4>
        <div className="space-y-2">
          <div className="flex items-center space-x-2 text-sm text-foreground-muted">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>Early access to all features</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-foreground-muted">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>Direct feedback to our team</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-foreground-muted">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>Exclusive beta community access</span>
          </div>
        </div>
      </div>
    </div>
  )
}