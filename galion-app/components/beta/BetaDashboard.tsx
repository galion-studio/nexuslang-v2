'use client'

import { useState, useEffect } from 'react'
import { Star, MessageSquare, Bug, Lightbulb, TrendingUp, Users, Gift, Crown, CheckCircle, Clock, Award, Target } from 'lucide-react'
import { Button, Card } from '../../shared/ui'

interface BetaProfile {
  user_id: string
  beta_tier: string
  special_access_features: string[]
  session_count: number
  total_voice_sessions: number
  feedback_submitted: number
  bugs_reported: int
  feature_requests: number
  satisfaction_score: number | null
  nps_score: number | null
  retention_days: number
  first_login: string
  last_activity: string
}

interface BetaStats {
  program_overview: {
    total_beta_users: number
    current_capacity: number
    max_capacity: number
    utilization_rate: number
    program_progress: number
  }
  user_engagement: {
    active_users_7d: number
    active_user_rate: number
    total_voice_sessions: number
    avg_sessions_per_user: number
    total_feedback_submitted: number
    feedback_rate: number
  }
}

export function BetaDashboard() {
  const [profile, setProfile] = useState<BetaProfile | null>(null)
  const [stats, setStats] = useState<BetaStats | null>(null)
  const [feedbackRating, setFeedbackRating] = useState<number>(0)
  const [feedbackComments, setFeedbackComments] = useState('')
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false)
  const [showFeedbackForm, setShowFeedbackForm] = useState(false)

  useEffect(() => {
    loadBetaData()
  }, [])

  const loadBetaData = async () => {
    try {
      const [profileResponse, statsResponse] = await Promise.all([
        fetch('/api/v2/beta/profile'),
        fetch('/api/v2/beta/status')
      ])

      if (profileResponse.ok) {
        const profileData = await profileResponse.json()
        setProfile(profileData)
      }

      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats({
          program_overview: {
            total_beta_users: statsData.current_users,
            current_capacity: statsData.current_users,
            max_capacity: statsData.max_users,
            utilization_rate: statsData.utilization_rate,
            program_progress: (statsData.current_users / 10000) * 100
          },
          user_engagement: {
            active_users_7d: Math.floor(statsData.current_users * 0.7), // Mock data
            active_user_rate: 75.5, // Mock data
            total_voice_sessions: 15420, // Mock data
            avg_sessions_per_user: 4.2, // Mock data
            total_feedback_submitted: 890, // Mock data
            feedback_rate: 45.2 // Mock data
          }
        })
      }
    } catch (error) {
      console.error('Failed to load beta data:', error)
    }
  }

  const submitFeedback = async (feedbackType: string) => {
    if (feedbackRating === 0 && !feedbackComments.trim()) return

    setIsSubmittingFeedback(true)
    try {
      await fetch('/api/v2/beta/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          feedback_type: feedbackType,
          rating: feedbackRating,
          comments: feedbackComments,
          metadata: {
            source: 'beta_dashboard',
            beta_tier: profile?.beta_tier,
          },
        }),
      })

      // Reset form
      setFeedbackRating(0)
      setFeedbackComments('')
      setShowFeedbackForm(false)

      // Refresh profile data
      loadBetaData()
    } catch (error) {
      console.error('Failed to submit feedback:', error)
    } finally {
      setIsSubmittingFeedback(false)
    }
  }

  const trackActivity = async (activityType: string) => {
    try {
      await fetch('/api/v2/beta/activity/track', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          activity_type: activityType,
          metadata: { source: 'beta_dashboard' }
        }),
      })
    } catch (error) {
      console.error('Failed to track activity:', error)
    }
  }

  if (!profile || !stats) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-gray-300 rounded w-1/3"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-24 bg-gray-300 rounded"></div>
          ))}
        </div>
      </div>
    )
  }

  const tierColors = {
    standard: 'bg-blue-100 text-blue-800 border-blue-200',
    premium: 'bg-purple-100 text-purple-800 border-purple-200',
    vip: 'bg-yellow-100 text-yellow-800 border-yellow-200'
  }

  const tierIcons = {
    standard: <Star className="w-4 h-4" />,
    premium: <Award className="w-4 h-4" />,
    vip: <Crown className="w-4 h-4" />
  }

  return (
    <div className="space-y-6">
      {/* Beta Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              {tierIcons[profile.beta_tier as keyof typeof tierIcons]}
              <span className="text-sm font-medium opacity-90">
                {profile.beta_tier.charAt(0).toUpperCase() + profile.beta_tier.slice(1)} Beta Member
              </span>
            </div>
            <h2 className="text-2xl font-bold">Welcome to Galion Beta!</h2>
            <p className="text-blue-100 mt-1">
              You're part of an exclusive group shaping the future of AI
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">
              #{String(profile.user_id).slice(-4).padStart(4, '0')}
            </div>
            <div className="text-sm opacity-80">Beta ID</div>
          </div>
        </div>
      </div>

      {/* Beta Progress & Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center space-x-2">
            <Users className="w-5 h-5 text-blue-500" />
            <span className="text-sm font-medium text-gray-600">Program Progress</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-gray-900">
              {stats.program_overview.program_progress.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500">
              {stats.program_overview.total_beta_users} of 10,000 users
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-2">
            <Target className="w-5 h-5 text-green-500" />
            <span className="text-sm font-medium text-gray-600">Your Sessions</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-gray-900">{profile.session_count}</div>
            <div className="text-xs text-gray-500">
              {profile.total_voice_sessions} voice interactions
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-2">
            <MessageSquare className="w-5 h-5 text-purple-500" />
            <span className="text-sm font-medium text-gray-600">Feedback Given</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-gray-900">{profile.feedback_submitted}</div>
            <div className="text-xs text-gray-500">
              {profile.bugs_reported} bugs, {profile.feature_requests} features
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-orange-500" />
            <span className="text-sm font-medium text-gray-600">Activity Score</span>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-gray-900">
              {profile.retention_days > 0 ? Math.min(100, profile.retention_days * 10) : 0}
            </div>
            <div className="text-xs text-gray-500">
              {profile.retention_days} days active
            </div>
          </div>
        </Card>
      </div>

      {/* Special Features */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Beta Benefits</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {profile.special_access_features.map((feature, index) => (
            <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              <span className="text-sm text-gray-700 capitalize">
                {feature.replace(/_/g, ' ')}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Program Stats */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Beta Program Stats</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 mb-1">
              {stats.user_engagement.active_user_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Weekly Active Users</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 mb-1">
              {stats.user_engagement.avg_sessions_per_user.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600">Avg Sessions/User</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600 mb-1">
              {stats.user_engagement.feedback_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Feedback Rate</div>
          </div>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Beta Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button
            variant="outline"
            className="p-4 h-auto flex-col space-y-2"
            onClick={() => setShowFeedbackForm(true)}
          >
            <MessageSquare className="w-6 h-6" />
            <span>Give Feedback</span>
          </Button>

          <Button
            variant="outline"
            className="p-4 h-auto flex-col space-y-2"
            onClick={() => trackActivity('bug_report_intent')}
          >
            <Bug className="w-6 h-6" />
            <span>Report Bug</span>
          </Button>

          <Button
            variant="outline"
            className="p-4 h-auto flex-col space-y-2"
            onClick={() => trackActivity('feature_request_intent')}
          >
            <Lightbulb className="w-6 h-6" />
            <span>Suggest Feature</span>
          </Button>
        </div>
      </Card>

      {/* Feedback Form Modal */}
      {showFeedbackForm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Share Your Feedback</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  How satisfied are you with Galion?
                </label>
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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Comments (Optional)
                </label>
                <textarea
                  value={feedbackComments}
                  onChange={(e) => setFeedbackComments(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Tell us what you think..."
                />
              </div>

              <div className="flex space-x-3">
                <Button
                  variant="outline"
                  onClick={() => setShowFeedbackForm(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => submitFeedback('general')}
                  disabled={isSubmittingFeedback || (feedbackRating === 0 && !feedbackComments.trim())}
                  className="flex-1"
                  leftIcon={isSubmittingFeedback ? undefined : <CheckCircle className="w-4 h-4" />}
                >
                  {isSubmittingFeedback ? 'Submitting...' : 'Submit'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Beta Milestones */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Beta Journey</h3>
        <div className="space-y-3">
          {[
            { milestone: 'Joined Beta Program', completed: true, date: profile.first_login },
            { milestone: 'First Voice Session', completed: profile.total_voice_sessions > 0, date: profile.last_activity },
            { milestone: 'Submitted Feedback', completed: profile.feedback_submitted > 0, date: null },
            { milestone: 'Reported First Bug', completed: profile.bugs_reported > 0, date: null },
            { milestone: 'Suggested Feature', completed: profile.feature_requests > 0, date: null },
            { milestone: '30-Day Active User', completed: profile.retention_days >= 30, date: null },
          ].map((milestone, index) => (
            <div key={index} className="flex items-center space-x-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                milestone.completed ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
              }`}>
                {milestone.completed ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <Clock className="w-4 h-4" />
                )}
              </div>
              <div className="flex-1">
                <div className={`text-sm font-medium ${milestone.completed ? 'text-gray-900' : 'text-gray-500'}`}>
                  {milestone.milestone}
                </div>
                {milestone.date && (
                  <div className="text-xs text-gray-500">
                    {new Date(milestone.date).toLocaleDateString()}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
