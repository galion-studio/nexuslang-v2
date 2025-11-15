'use client'

import { useState, useEffect } from 'react'
import { Check, Mic, Brain, Zap, Crown } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { galionAPI } from '@/lib/api-client'
import toast from 'react-hot-toast'

interface SubscriptionTier {
  id: string
  name: string
  price: number
  credits: number
  features: string[]
  popular?: boolean
}

const tiers: SubscriptionTier[] = [
  {
    id: 'free',
    name: 'Voice Explorer',
    price: 0,
    credits: 100,
    features: [
      '100 voice interactions/month',
      'Basic voice commands',
      'Text-to-speech',
      'Community support'
    ]
  },
  {
    id: 'voice_pro',
    name: 'Voice Professional',
    price: 29,
    credits: 2000,
    features: [
      '2,000 voice interactions/month',
      'Advanced voice commands',
      'Research assistant',
      'Priority support',
      'Custom voice models'
    ],
    popular: true
  },
  {
    id: 'voice_enterprise',
    name: 'Voice Enterprise',
    price: 99,
    credits: 10000,
    features: [
      '10,000 voice interactions/month',
      'All voice features',
      'API access',
      'White-label options',
      'Dedicated support',
      'Custom integrations'
    ]
  }
]

export default function SubscriptionPage() {
  const [currentSubscription, setCurrentSubscription] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSubscriptionData()
  }, [])

  const loadSubscriptionData = async () => {
    try {
      const [subscription, credits] = await Promise.all([
        galionAPI.getSubscriptions(),
        galionAPI.getCredits()
      ])
      setCurrentSubscription({ ...subscription, credits })
    } catch (error) {
      console.error('Failed to load subscription:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubscribe = async (tierId: string) => {
    try {
      await galionAPI.subscribe(tierId)
      toast.success('Subscription updated successfully!')
      await loadSubscriptionData()
    } catch (error) {
      toast.error('Failed to update subscription')
      console.error('Subscription error:', error)
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>
  }

  return (
    <div className="space-y-8 max-w-6xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Voice AI Subscriptions</h1>
        <p className="text-muted-foreground">
          Choose the perfect plan for your voice AI needs
        </p>
      </div>

      {/* Current Usage */}
      {currentSubscription && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mic className="h-5 w-5" />
              Current Plan
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Plan</p>
                <p className="text-2xl font-semibold">{currentSubscription.tier || 'Free'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Credits Remaining</p>
                <p className="text-2xl font-semibold text-green-600">{currentSubscription.credits || 0}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Voice Interactions</p>
                <p className="text-lg">{currentSubscription.usage || 0} this month</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pricing Tiers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {tiers.map((tier) => (
          <Card
            key={tier.id}
            className={`relative ${tier.popular ? 'ring-2 ring-blue-500' : ''}`}
          >
            {tier.popular && (
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                  Most Popular
                </span>
              </div>
            )}

            <CardHeader className="text-center">
              <div className="mx-auto mb-4">
                {tier.id === 'free' && <Mic className="h-12 w-12 text-gray-400" />}
                {tier.id === 'voice_pro' && <Brain className="h-12 w-12 text-blue-500" />}
                {tier.id === 'voice_enterprise' && <Crown className="h-12 w-12 text-purple-500" />}
              </div>
              <CardTitle className="text-2xl">{tier.name}</CardTitle>
              <div className="mt-4">
                <span className="text-4xl font-bold">${tier.price}</span>
                <span className="text-muted-foreground">/month</span>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                {tier.credits.toLocaleString()} voice interactions
              </p>
            </CardHeader>

            <CardContent>
              <ul className="space-y-3 mb-6">
                {tier.features.map((feature, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-green-500 flex-shrink-0" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleSubscribe(tier.id)}
                disabled={currentSubscription?.tier === tier.id}
                className={`w-full py-3 px-4 rounded-lg font-semibold transition ${
                  currentSubscription?.tier === tier.id
                    ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                    : tier.popular
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-gray-900 hover:bg-gray-800 text-white'
                }`}
              >
                {currentSubscription?.tier === tier.id ? 'Current Plan' : 'Subscribe'}
              </button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Features Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>All Plans Include</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <Mic className="h-5 w-5 text-blue-500" />
                Voice Features
              </h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Natural speech recognition</li>
                <li>• Human-like voice synthesis</li>
                <li>• Context-aware conversations</li>
                <li>• Multi-language support</li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                AI Capabilities
              </h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Research and analysis</li>
                <li>• Task automation</li>
                <li>• Knowledge base access</li>
                <li>• Intelligent routing</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
