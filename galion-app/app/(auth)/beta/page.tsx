'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, CheckCircle, Star, Zap, Users, TrendingUp, MessageSquare, Gift, Crown, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface BetaStats {
  current_users: number
  max_users: number
  utilization_rate: number
  available_tiers: string[]
  special_features: string[]
}

export default function BetaPage() {
  const [stats, setStats] = useState<BetaStats | null>(null)
  const [invitationCode, setInvitationCode] = useState('')
  const [isValidating, setIsValidating] = useState(false)
  const [validationResult, setValidationResult] = useState<any>(null)
  const [isJoining, setIsJoining] = useState(false)
  const router = useRouter()

  useEffect(() => {
    loadBetaStats()
  }, [])

  const loadBetaStats = async () => {
    try {
      const response = await fetch('/api/v2/beta/status')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to load beta stats:', error)
    }
  }

  const validateInvitationCode = async () => {
    if (!invitationCode.trim()) return

    setIsValidating(true)
    try {
      const response = await fetch(`/api/v2/beta/invitations/${invitationCode}/validate`)
      const result = await response.json()

      if (response.ok) {
        setValidationResult(result)
      } else {
        setValidationResult({ valid: false, error: result.detail })
      }
    } catch (error) {
      setValidationResult({ valid: false, error: 'Failed to validate code' })
    } finally {
      setIsValidating(false)
    }
  }

  const joinBetaProgram = async () => {
    if (!validationResult?.valid) return

    setIsJoining(true)
    try {
      // First, register the user as beta tester
      const registerResponse = await fetch('/api/v2/beta/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          invitation_code: invitationCode,
        }),
      })

      if (registerResponse.ok) {
        // Success - redirect to dashboard
        router.push('/dashboard?beta_joined=true')
      } else {
        const error = await registerResponse.json()
        setValidationResult({ valid: false, error: error.detail })
      }
    } catch (error) {
      setValidationResult({ valid: false, error: 'Failed to join beta program' })
    } finally {
      setIsJoining(false)
    }
  }

  const utilizationRate = stats ? Math.min(stats.utilization_rate, 100) : 0
  const spotsRemaining = stats ? Math.max(0, stats.max_users - stats.current_users) : 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-black/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-semibold">Galion Beta</span>
            </Link>

            <div className="flex items-center space-x-4">
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
              </Link>
              <Link href="/register">
                <Button size="sm">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="relative">
        {/* Hero Section */}
        <section className="py-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <div className="mb-8">
              <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Join the Future
              </h1>
              <p className="text-2xl md:text-3xl text-white/70 mb-8">
                Be among the first 10,000 users to experience the revolution in voice-first AI
              </p>
              <div className="text-lg text-white/60 italic">
                "Your imagination is the end."
              </div>
            </div>

            {/* Beta Progress */}
            {stats && (
              <div className="mb-12">
                <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8 max-w-md mx-auto">
                  <div className="flex items-center justify-center space-x-4 mb-6">
                    <Users className="w-8 h-8 text-blue-400" />
                    <div>
                      <div className="text-3xl font-bold text-white">
                        {stats.current_users.toLocaleString()}
                      </div>
                      <div className="text-white/60">Beta Users</div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-white/60">Progress</span>
                      <span className="text-white">{utilizationRate.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-white/20 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-1000"
                        style={{ width: `${utilizationRate}%` }}
                      />
                    </div>
                    <div className="text-center text-sm text-white/60">
                      {spotsRemaining > 0 ? `${spotsRemaining} spots remaining` : 'Program at capacity'}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Beta Tiers */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
              <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Star className="w-6 h-6 text-yellow-400" />
                  <h3 className="text-xl font-semibold">Standard</h3>
                </div>
                <ul className="text-left space-y-2 text-white/70">
                  <li className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>Full platform access</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>Community support</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>Beta program updates</span>
                  </li>
                </ul>
              </div>

              <div className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 backdrop-blur-sm rounded-xl border border-blue-500/30 p-6 relative">
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </span>
                </div>
                <div className="flex items-center space-x-2 mb-4">
                  <Zap className="w-6 h-6 text-blue-400" />
                  <h3 className="text-xl font-semibold">Premium</h3>
                </div>
                <ul className="text-left space-y-2 text-white/70">
                  <li className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>All Standard features</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>Early feature access</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>Priority support</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>Direct feedback channel</span>
                  </li>
                </ul>
              </div>

              <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-sm rounded-xl border border-purple-500/30 p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Crown className="w-6 h-6 text-purple-400" />
                  <h3 className="text-xl font-semibold">VIP</h3>
                </div>
                <ul className="text-left space-y-2 text-white/70">
                  <li className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>All Premium features</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>Direct team communication</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>Product influence & voting</span>
                  </li>
                  <li className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span>Exclusive beta content</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Invitation Code Input */}
            <div className="max-w-md mx-auto">
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8">
                <h2 className="text-2xl font-bold mb-6">Enter Your Invitation</h2>

                <div className="space-y-4">
                  <div>
                    <input
                      type="text"
                      value={invitationCode}
                      onChange={(e) => setInvitationCode(e.target.value.toUpperCase())}
                      placeholder="Enter invitation code"
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      maxLength={8}
                    />
                  </div>

                  {!validationResult && (
                    <Button
                      onClick={validateInvitationCode}
                      disabled={!invitationCode.trim() || isValidating}
                      className="w-full"
                      leftIcon={isValidating ? undefined : <CheckCircle className="w-4 h-4" />}
                    >
                      {isValidating ? 'Validating...' : 'Validate Code'}
                    </Button>
                  )}

                  {validationResult && (
                    <div className="space-y-4">
                      {validationResult.valid ? (
                        <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-4">
                          <div className="flex items-center space-x-2 mb-2">
                            <CheckCircle className="w-5 h-5 text-green-400" />
                            <span className="font-medium text-green-400">Valid Invitation Code!</span>
                          </div>
                          <div className="text-sm text-white/70 space-y-1">
                            <div>Tier: <span className="capitalize font-medium">{validationResult.beta_tier}</span></div>
                            <div>Uses remaining: {validationResult.uses_remaining}</div>
                            <div>Expires: {new Date(validationResult.expires_at).toLocaleDateString()}</div>
                          </div>
                        </div>
                      ) : (
                        <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-4">
                          <div className="flex items-center space-x-2 mb-2">
                            <CheckCircle className="w-5 h-5 text-red-400" />
                            <span className="font-medium text-red-400">Invalid Code</span>
                          </div>
                          <div className="text-sm text-white/70">
                            {validationResult.error}
                          </div>
                        </div>
                      )}

                      {validationResult.valid && (
                        <Button
                          onClick={joinBetaProgram}
                          disabled={isJoining}
                          className="w-full"
                          leftIcon={<Sparkles className="w-4 h-4" />}
                        >
                          {isJoining ? 'Joining Beta...' : 'Join Beta Program'}
                        </Button>
                      )}

                      {validationResult && !validationResult.valid && (
                        <Button
                          onClick={() => setValidationResult(null)}
                          variant="outline"
                          className="w-full"
                        >
                          Try Another Code
                        </Button>
                      )}
                    </div>
                  )}
                </div>

                <div className="mt-6 text-center">
                  <p className="text-white/60 text-sm mb-2">Don't have an invitation code?</p>
                  <Link href="/beta/waitlist" className="text-blue-400 hover:text-blue-300 text-sm font-medium">
                    Join the waitlist →
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-black/20">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-6">Why Join the Beta?</h2>
              <p className="text-xl text-white/70 max-w-3xl mx-auto">
                Be part of the revolution in human-AI interaction. Your feedback will shape the future of technology.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <TrendingUp className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Shape the Future</h3>
                <p className="text-white/70">
                  Your feedback directly influences product development. VIP members get voting rights on new features.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Early Access</h3>
                <p className="text-white/70">
                  Get access to cutting-edge features months before general release. Experience the latest innovations first.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <MessageSquare className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Direct Communication</h3>
                <p className="text-white/70">
                  Premium and VIP users get direct access to the development team. Your questions are answered personally.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Gift className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Exclusive Perks</h3>
                <p className="text-white/70">
                  Beta-exclusive content, merchandise, and recognition in our launch announcements and documentation.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-red-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Users className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Community Building</h3>
                <p className="text-white/70">
                  Join a community of innovators and early adopters. Network with like-minded individuals shaping the future.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Star className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-4">Recognition</h3>
                <p className="text-white/70">
                  Active beta participants are recognized in our product launches, documentation, and community stories.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-white/10 py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-6xl mx-auto text-center">
            <div className="flex items-center justify-center space-x-6 mb-6">
              <Link href="/" className="text-white/60 hover:text-white transition-colors">
                Home
              </Link>
              <Link href="/about" className="text-white/60 hover:text-white transition-colors">
                About
              </Link>
              <Link href="/privacy" className="text-white/60 hover:text-white transition-colors">
                Privacy
              </Link>
              <Link href="/terms" className="text-white/60 hover:text-white transition-colors">
                Terms
              </Link>
            </div>
            <p className="text-white/40 text-sm">
              © 2025 Galion. "Your imagination is the end."
            </p>
          </div>
        </footer>
      </main>
    </div>
  )
}
