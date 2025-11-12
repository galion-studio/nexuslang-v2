'use client'

import { useState, useEffect } from 'react'
import { CreditCard, Zap, TrendingUp, Check } from 'lucide-react'

export default function BillingPage() {
  const [currentTier, setCurrentTier] = useState('free')
  const [credits, setCredits] = useState(100)
  const [usedCredits, setUsedCredits] = useState(0)

  useEffect(() => {
    // Fetch current subscription and credits
    fetchBillingInfo()
  }, [])

  const fetchBillingInfo = async () => {
    try {
      const response = await fetch('/api/v2/billing/subscriptions')
      const data = await response.json()
      setCurrentTier(data.tier)
      setCredits(data.credits)
    } catch (error) {
      console.error('Failed to fetch billing info:', error)
    }
  }

  const handleSubscribe = async (tier: string) => {
    try {
      const response = await fetch('/api/v2/billing/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tier })
      })
      const data = await response.json()
      
      // Redirect to Shopify checkout
      if (data.checkout_url) {
        window.location.href = data.checkout_url
      }
    } catch (error) {
      console.error('Subscription failed:', error)
    }
  }

  const handleBuyCredits = async (amount: number) => {
    try {
      const response = await fetch('/api/v2/billing/buy-credits', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount })
      })
      const data = await response.json()
      
      // Redirect to Shopify checkout
      if (data.checkout_url) {
        window.location.href = data.checkout_url
      }
    } catch (error) {
      console.error('Purchase failed:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-zinc-900 to-black">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Billing & Subscriptions
          </h1>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12">
        {/* Current Plan & Credits */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Current Plan</h2>
              <CreditCard className="text-blue-400" size={24} />
            </div>
            <p className="text-3xl font-bold mb-2 capitalize">{currentTier}</p>
            <p className="text-zinc-400">
              {currentTier === 'free' && 'Upgrade for more features'}
              {currentTier === 'pro' && 'Professional features enabled'}
              {currentTier === 'enterprise' && 'Full platform access'}
            </p>
          </div>

          <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Available Credits</h2>
              <Zap className="text-yellow-400" size={24} />
            </div>
            <p className="text-3xl font-bold mb-2">{credits.toLocaleString()}</p>
            <div className="w-full bg-zinc-800 rounded-full h-2 mb-2">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                style={{ width: `${(credits / (credits + usedCredits)) * 100}%` }}
              />
            </div>
            <p className="text-sm text-zinc-400">
              {usedCredits.toLocaleString()} used this month
            </p>
          </div>
        </div>

        {/* Subscription Plans */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Subscription Plans</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {PLANS.map((plan) => (
              <div
                key={plan.tier}
                className={`p-6 rounded-lg border-2 transition ${
                  currentTier === plan.tier
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-zinc-800 bg-zinc-900 hover:border-zinc-700'
                }`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold">{plan.name}</h3>
                  {currentTier === plan.tier && (
                    <span className="text-xs px-2 py-1 bg-blue-500 rounded">Current</span>
                  )}
                </div>
                
                <div className="mb-6">
                  <span className="text-4xl font-bold">${plan.price}</span>
                  <span className="text-zinc-400">/month</span>
                </div>

                <div className="space-y-3 mb-6">
                  {plan.features.map((feature, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <Check size={18} className="text-green-400 mt-0.5" />
                      <span className="text-sm">{feature}</span>
                    </div>
                  ))}
                </div>

                {currentTier !== plan.tier && (
                  <button
                    onClick={() => handleSubscribe(plan.tier)}
                    className={`w-full py-3 rounded-lg transition ${
                      plan.tier === 'free'
                        ? 'bg-zinc-800 hover:bg-zinc-700'
                        : 'bg-blue-600 hover:bg-blue-700'
                    }`}
                  >
                    {plan.tier === 'free' ? 'Downgrade' : 'Upgrade'}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Buy Additional Credits */}
        <div>
          <h2 className="text-2xl font-bold mb-6">Buy Additional Credits</h2>
          <div className="grid md:grid-cols-4 gap-4">
            {CREDIT_PACKS.map((pack) => (
              <div
                key={pack.amount}
                className="p-6 bg-zinc-900 border border-zinc-800 rounded-lg hover:border-zinc-700 transition"
              >
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="text-yellow-400" size={20} />
                  <span className="text-2xl font-bold">{pack.amount.toLocaleString()}</span>
                </div>
                <p className="text-zinc-400 text-sm mb-4">{pack.label}</p>
                <p className="text-xl font-bold mb-4">${pack.price}</p>
                <button
                  onClick={() => handleBuyCredits(pack.amount)}
                  className="w-full py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition"
                >
                  Buy Now
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Usage History */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6">Usage History</h2>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-zinc-800">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Date</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Service</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Credits</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold">Balance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {MOCK_USAGE.map((item, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 text-sm">{item.date}</td>
                    <td className="px-6 py-4 text-sm">{item.service}</td>
                    <td className={`px-6 py-4 text-sm ${item.credits > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {item.credits > 0 ? '+' : ''}{item.credits}
                    </td>
                    <td className="px-6 py-4 text-sm">{item.balance}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

const PLANS = [
  {
    tier: 'free',
    name: 'Free',
    price: 0,
    features: [
      '100 AI credits/month',
      'Basic Grokopedia access',
      'Limited IDE features',
      'Community support'
    ]
  },
  {
    tier: 'pro',
    name: 'Pro',
    price: 19,
    features: [
      '10,000 AI credits/month',
      'Full IDE access',
      'Priority support',
      'Custom voice cloning',
      'Advanced analytics',
      'Private projects'
    ]
  },
  {
    tier: 'enterprise',
    name: 'Enterprise',
    price: 199,
    features: [
      'Unlimited credits',
      'Private deployment',
      'SLA guarantees',
      'Dedicated support',
      'Custom integrations',
      'Team collaboration',
      'Advanced security'
    ]
  }
]

const CREDIT_PACKS = [
  { amount: 1000, price: 10, label: 'Starter' },
  { amount: 5000, price: 45, label: 'Popular' },
  { amount: 10000, price: 80, label: 'Value' },
  { amount: 25000, price: 175, label: 'Power User' }
]

const MOCK_USAGE = [
  { date: '2025-11-11', service: 'NexusLang Execution', credits: -50, balance: 100 },
  { date: '2025-11-10', service: 'Grokopedia Search', credits: -20, balance: 150 },
  { date: '2025-11-09', service: 'Voice Synthesis', credits: -30, balance: 170 },
  { date: '2025-11-08', service: 'Monthly Refill', credits: +100, balance: 200 },
]

