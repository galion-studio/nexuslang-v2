'use client'

import { useState, useEffect } from 'react'
import { Sparkles, Zap, Building, Crown, Check } from 'lucide-react'
import Link from 'next/link'

export default function SubscriptionPage() {
  const [currentTier, setCurrentTier] = useState('free_trial')
  const [credits, setCredits] = useState(100)
  const [used, setUsed] = useState(0)
  
  const tiers = [
    {
      id: 'creator',
      name: 'Creator',
      price: 20,
      icon: Sparkles,
      color: 'purple',
      features: [
        '200 image generations/month',
        '50 video generations',
        '500 text generations',
        'Commercial license',
        'No watermarks',
        'Priority queue'
      ]
    },
    {
      id: 'professional',
      name: 'Professional',
      price: 50,
      icon: Zap,
      color: 'blue',
      features: [
        '1,000 image generations',
        '200 video generations',
        'All premium models',
        'Team collaboration (3 seats)',
        'API access',
        'Priority support'
      ]
    },
    {
      id: 'business',
      name: 'Business',
      price: 200,
      icon: Building,
      color: 'green',
      features: [
        '10,000 image generations',
        '2,000 video generations',
        'White-label option',
        'Team (10 seats)',
        'Dedicated support',
        'Custom training'
      ]
    }
  ]
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-2">Subscription</h1>
        <p className="text-zinc-400 mb-8">Manage your plan and credits</p>
        
        {/* Current Plan */}
        <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-xl p-8 border border-purple-500/30 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-purple-400 mb-1">Current Plan</div>
              <div className="text-3xl font-bold text-white">Free Trial</div>
              <div className="text-zinc-400 mt-2">{credits} credits remaining</div>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-white mb-1">{used}/{credits}</div>
              <div className="text-sm text-zinc-400">Credits used</div>
              <div className="mt-3">
                <div className="w-48 h-2 bg-zinc-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                    style={{ width: `${(used / credits) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Upgrade Options */}
        <h2 className="text-2xl font-bold text-white mb-6">Upgrade Your Plan</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {tiers.map(tier => (
            <div
              key={tier.id}
              className="bg-zinc-900 rounded-xl border border-zinc-800 p-6 hover:border-purple-500/50 transition"
            >
              <div className={`w-12 h-12 bg-${tier.color}-600/20 rounded-lg flex items-center justify-center mb-4`}>
                <tier.icon className={`text-${tier.color}-400`} size={24} />
              </div>
              <h3 className="text-2xl font-bold text-white mb-1">{tier.name}</h3>
              <div className="text-3xl font-bold text-white mb-4">
                ${tier.price}<span className="text-lg text-zinc-400">/month</span>
              </div>
              <ul className="space-y-2 mb-6">
                {tier.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                    <Check size={16} className="text-green-400 flex-shrink-0 mt-0.5" />
                    {feature}
                  </li>
                ))}
              </ul>
              <Link
                href="/contact"
                className="block w-full py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg font-semibold text-center transition"
              >
                Coming Soon
              </Link>
            </div>
          ))}
        </div>
        
        {/* Note */}
        <div className="mt-8 bg-blue-900/20 border border-blue-500/30 rounded-lg p-6">
          <p className="text-blue-300 text-center">
            💡 <strong>Note:</strong> Paid subscriptions coming soon! Currently enjoying free tier with 100 credits.
          </p>
        </div>
      </div>
    </div>
  )
}

