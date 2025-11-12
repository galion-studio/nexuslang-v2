'use client'

/**
 * Pricing Page - Complete Tier Structure
 * Galion Studio (Subscriptions) + Developer Platform (Pay-per-use)
 */

import { useState } from 'react'
import Link from 'next/link'
import { Check, Zap, Code, Sparkles, Building, Crown } from 'lucide-react'

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly')
  const [activeProduct, setActiveProduct] = useState<'studio' | 'developer'>('studio')
  
  // Galion Studio Subscription Plans
  const studioPlans = [
    {
      name: 'Free Trial',
      price: { monthly: 0, annual: 0 },
      duration: '14 days',
      icon: Sparkles,
      color: 'blue',
      features: [
        '20 image generations',
        '10 video generations (5s)',
        '50 text generations (GPT-3.5)',
        '100 NexusLang code runs',
        'Basic models only',
        'Watermarked outputs',
        'Community support'
      ],
      limitations: [
        'No commercial use',
        'Standard queue',
        'No API access'
      ],
      cta: 'Start Free Trial',
      popular: false
    },
    {
      name: 'Creator',
      price: { monthly: 20, annual: 200 },
      savings: '15%',
      icon: Sparkles,
      color: 'purple',
      features: [
        '200 image generations/month',
        '50 video generations (30s)',
        '500 text generations (Claude Haiku, GPT-3.5)',
        '1,000 NexusLang runs',
        '100 voice generations (TTS)',
        'No watermarks',
        'Commercial license',
        'Priority queue',
        'Email support (48h)',
        'Basic API access (100/day)'
      ],
      overage: '$0.10 per extra generation',
      cta: 'Start Creating',
      popular: true
    },
    {
      name: 'Professional',
      price: { monthly: 50, annual: 500 },
      savings: '20%',
      icon: Zap,
      color: 'green',
      features: [
        '1,000 image generations/month',
        '200 video generations (2min, 4K)',
        '2,000 text generations (Claude Sonnet, GPT-4)',
        '10,000 NexusLang runs',
        '500 voice generations + cloning',
        'Unlimited AI upscaling',
        'Unlimited background removal',
        '50 3D model generations',
        'All premium models',
        'Priority support (24h)',
        'Full API access (1,000/day)',
        'Team collaboration (3 seats)',
        'Brand voice training',
        'Content scheduler',
        'Analytics dashboard'
      ],
      overage: '$0.08 per extra generation',
      cta: 'Go Professional',
      popular: false
    },
    {
      name: 'Business',
      price: { monthly: 200, annual: 2000 },
      savings: '20%',
      icon: Building,
      color: 'orange',
      features: [
        '10,000 image generations/month',
        '2,000 video generations (5min)',
        '20,000 text generations (all models)',
        'Unlimited NexusLang execution',
        '5,000 voice generations',
        'Everything unlimited',
        'Priority support (12h)',
        'Advanced API (10,000/day)',
        'Team seats (10 included)',
        'White-label option',
        'Custom model training',
        'Dedicated account manager',
        'SLA guarantee (99.9%)',
        'Multi-brand management',
        'Advanced analytics',
        'Custom integrations'
      ],
      overage: '$0.05 per extra generation',
      cta: 'Scale Business',
      popular: false
    },
    {
      name: 'Enterprise',
      price: { monthly: 2500, annual: 25000 },
      custom: true,
      icon: Crown,
      color: 'red',
      features: [
        'Unlimited everything',
        'Custom integrations',
        'On-premise deployment',
        'Dedicated infrastructure',
        '24/7 phone support',
        'Custom SLA',
        'Security audit included',
        'Training & onboarding',
        'Unlimited team seats',
        'Custom model development',
        'API limits customized',
        'Invoiced billing',
        'Legal review support',
        'Compliance assistance'
      ],
      cta: 'Contact Sales',
      popular: false
    }
  ]
  
  // Developer Platform Plans
  const developerPlans = [
    {
      name: 'Free Developer',
      price: { monthly: 0, annual: 0 },
      icon: Code,
      color: 'blue',
      features: [
        'Pay-per-use credits',
        '100 free credits (one-time)',
        'All APIs available',
        '100 requests/minute',
        '10,000 requests/day',
        'Community support',
        'Public documentation',
        'Code examples',
        'GitHub integration'
      ],
      cta: 'Start Building',
      popular: false
    },
    {
      name: 'Professional Dev',
      price: { monthly: 49, annual: 490 },
      credits: '$50 credits included',
      icon: Code,
      color: 'purple',
      features: [
        '$50/month credits included (6,000 credits)',
        '500 requests/minute',
        '50,000 requests/day',
        'Priority support (24h)',
        'Beta API access',
        'Advanced analytics',
        'Webhook callbacks',
        'Custom integration help',
        'Premium documentation'
      ],
      overage: 'Pay-per-use at standard rates',
      cta: 'Upgrade to Pro',
      popular: true
    },
    {
      name: 'Business API',
      price: { monthly: 199, annual: 1990 },
      credits: '$250 credits included',
      icon: Building,
      color: 'green',
      features: [
        '$250/month credits included (50,000 credits)',
        'Dedicated API keys',
        '2,000 requests/minute',
        '200,000 requests/day',
        'Priority support (12h)',
        'SLA guarantee (99.9%)',
        'Custom rate limits',
        'Multi-environment support',
        'Advanced monitoring',
        'Team access (5 devs)',
        'Staging environment'
      ],
      cta: 'Scale API',
      popular: false
    },
    {
      name: 'Enterprise API',
      price: { monthly: 2000, annual: 20000 },
      custom: true,
      icon: Crown,
      color: 'red',
      features: [
        'Custom credit allocation',
        'Unlimited API access',
        'Custom rate limits',
        'Dedicated support team',
        'Custom SLA',
        'On-premise option',
        'Custom model training',
        'White-label API',
        'Invoiced billing',
        'Legal compliance support'
      ],
      cta: 'Contact Enterprise',
      popular: false
    }
  ]
  
  const plans = activeProduct === 'studio' ? studioPlans : developerPlans
  
  // Calculate annual savings
  const getPrice = (plan: any) => {
    if (plan.custom) return 'Custom'
    const price = billingCycle === 'monthly' ? plan.price.monthly : plan.price.annual / 12
    return price === 0 ? 'Free' : `$${price}`
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950">
      {/* Header */}
      <div className="border-b border-zinc-800">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center">
            <h1 className="text-5xl font-bold text-white mb-4">
              Simple, Transparent Pricing
            </h1>
            <p className="text-xl text-zinc-400 mb-8">
              Choose the plan that fits your needs. Upgrade or downgrade anytime.
            </p>
            
            {/* Product Selector */}
            <div className="flex justify-center gap-4 mb-6">
              <button
                onClick={() => setActiveProduct('studio')}
                className={`px-8 py-3 rounded-lg font-semibold transition ${
                  activeProduct === 'studio'
                    ? 'bg-purple-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:text-white'
                }`}
              >
                <Sparkles className="inline mr-2" size={20} />
                Galion Studio
              </button>
              <button
                onClick={() => setActiveProduct('developer')}
                className={`px-8 py-3 rounded-lg font-semibold transition ${
                  activeProduct === 'developer'
                    ? 'bg-blue-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:text-white'
                }`}
              >
                <Code className="inline mr-2" size={20} />
                Developer Platform
              </button>
            </div>
            
            {/* Billing Cycle Toggle */}
            {activeProduct === 'studio' && (
              <div className="flex items-center justify-center gap-4">
                <span className={billingCycle === 'monthly' ? 'text-white' : 'text-zinc-500'}>
                  Monthly
                </span>
                <button
                  onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'annual' : 'monthly')}
                  className="relative w-14 h-7 bg-zinc-700 rounded-full transition"
                >
                  <div className={`absolute top-1 left-1 w-5 h-5 bg-white rounded-full transition-transform ${
                    billingCycle === 'annual' ? 'transform translate-x-7' : ''
                  }`} />
                </button>
                <span className={billingCycle === 'annual' ? 'text-white' : 'text-zinc-500'}>
                  Annual <span className="text-green-400 text-sm ml-1">(Save 15-20%)</span>
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Pricing Cards */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`relative bg-zinc-900 rounded-xl border-2 ${
                plan.popular 
                  ? 'border-purple-500 shadow-lg shadow-purple-500/20' 
                  : 'border-zinc-800'
              } p-6 flex flex-col`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="px-4 py-1 bg-purple-600 text-white text-sm font-bold rounded-full">
                    MOST POPULAR
                  </span>
                </div>
              )}
              
              {/* Icon */}
              <div className={`w-12 h-12 bg-${plan.color}-600/20 rounded-lg flex items-center justify-center mb-4`}>
                <plan.icon className={`text-${plan.color}-400`} size={24} />
              </div>
              
              {/* Name */}
              <h3 className="text-xl font-bold text-white mb-2">{plan.name}</h3>
              
              {/* Price */}
              <div className="mb-4">
                {plan.custom ? (
                  <div>
                    <span className="text-4xl font-bold text-white">Custom</span>
                    <p className="text-sm text-zinc-500 mt-1">Contact for pricing</p>
                  </div>
                ) : (
                  <div>
                    <span className="text-4xl font-bold text-white">{getPrice(plan)}</span>
                    {plan.price.monthly > 0 && (
                      <span className="text-zinc-400">/{billingCycle === 'monthly' ? 'mo' : 'mo'}</span>
                    )}
                    {plan.duration && (
                      <p className="text-sm text-zinc-500 mt-1">{plan.duration}</p>
                    )}
                    {plan.savings && billingCycle === 'annual' && (
                      <p className="text-sm text-green-400 mt-1">Save {plan.savings}</p>
                    )}
                    {plan.credits && (
                      <p className="text-sm text-purple-400 mt-1">{plan.credits}</p>
                    )}
                  </div>
                )}
              </div>
              
              {/* CTA Button */}
              <Link
                href={plan.custom ? "/contact" : "/auth/register"}
                className={`w-full py-3 rounded-lg font-semibold text-center transition mb-6 ${
                  plan.popular
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                    : 'bg-zinc-800 hover:bg-zinc-700 text-white'
                }`}
              >
                {plan.cta}
              </Link>
              
              {/* Features */}
              <div className="space-y-3 flex-1">
                {plan.features.map((feature, i) => (
                  <div key={i} className="flex items-start gap-2">
                    <Check size={18} className="text-green-400 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-zinc-300">{feature}</span>
                  </div>
                ))}
                
                {plan.limitations && (
                  <div className="pt-3 mt-3 border-t border-zinc-800">
                    {plan.limitations.map((limit, i) => (
                      <div key={i} className="flex items-start gap-2 mb-2">
                        <span className="text-zinc-600 text-sm">• {limit}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {plan.overage && (
                <div className="mt-4 pt-4 border-t border-zinc-800">
                  <p className="text-xs text-zinc-500">Overage: {plan.overage}</p>
                </div>
              )}
            </div>
          ))}
        </div>
        
        {/* Pay-Per-Use Pricing Table (Developer Platform) */}
        {activeProduct === 'developer' && (
          <div className="mt-16">
            <h2 className="text-3xl font-bold text-white text-center mb-4">
              Pay-Per-Use Credit Pricing
            </h2>
            <p className="text-zinc-400 text-center mb-8">
              Buy credits, use anytime. Credits never expire.
            </p>
            
            <div className="max-w-4xl mx-auto bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden">
              <table className="w-full">
                <thead className="bg-zinc-800">
                  <tr>
                    <th className="px-6 py-4 text-left text-white font-semibold">API Call</th>
                    <th className="px-6 py-4 text-right text-white font-semibold">Credits</th>
                    <th className="px-6 py-4 text-right text-white font-semibold">Approx. Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800">
                  <tr>
                    <td className="px-6 py-3 text-zinc-300">NexusLang Execution</td>
                    <td className="px-6 py-3 text-right text-zinc-400">1</td>
                    <td className="px-6 py-3 text-right text-green-400">$0.01</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-3 text-zinc-300">Image Generation (Stable Diffusion)</td>
                    <td className="px-6 py-3 text-right text-zinc-400">5</td>
                    <td className="px-6 py-3 text-right text-green-400">$0.05</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-3 text-zinc-300">Image Generation (DALL-E 3)</td>
                    <td className="px-6 py-3 text-right text-zinc-400">10</td>
                    <td className="px-6 py-3 text-right text-green-400">$0.10</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-3 text-zinc-300">Video Generation (5s)</td>
                    <td className="px-6 py-3 text-right text-zinc-400">20</td>
                    <td className="px-6 py-3 text-right text-green-400">$0.20</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-3 text-zinc-300">Video Generation (30s)</td>
                    <td className="px-6 py-3 text-right text-zinc-400">50</td>
                    <td className="px-6 py-3 text-right text-green-400">$0.50</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-3 text-zinc-300">Text Gen (Claude Sonnet, per 1K tokens)</td>
                    <td className="px-6 py-3 text-right text-zinc-400">2</td>
                    <td className="px-6 py-3 text-right text-green-400">$0.02</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-3 text-zinc-300">Text Gen (GPT-4, per 1K tokens)</td>
                    <td className="px-6 py-3 text-right text-zinc-400">3</td>
                    <td className="px-6 py-3 text-right text-green-400">$0.03</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-3 text-zinc-300">Voice Synthesis (TTS)</td>
                    <td className="px-6 py-3 text-right text-zinc-400">3</td>
                    <td className="px-6 py-3 text-right text-green-400">$0.03</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-3 text-zinc-300">Voice Transcription (STT)</td>
                    <td className="px-6 py-3 text-right text-zinc-400">2</td>
                    <td className="px-6 py-3 text-right text-green-400">$0.02</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            {/* Credit Packages */}
            <div className="mt-8 grid md:grid-cols-4 gap-4">
              <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800 text-center">
                <div className="text-3xl font-bold text-white mb-2">$10</div>
                <div className="text-zinc-400 mb-4">1,000 credits</div>
                <div className="text-sm text-zinc-500">$0.01 per credit</div>
              </div>
              <div className="bg-zinc-900 p-6 rounded-lg border border-purple-600/50 text-center">
                <div className="text-xs text-purple-400 font-bold mb-2">20% BONUS</div>
                <div className="text-3xl font-bold text-white mb-2">$50</div>
                <div className="text-zinc-400 mb-4">6,000 credits</div>
                <div className="text-sm text-green-400">$0.0083 per credit</div>
              </div>
              <div className="bg-zinc-900 p-6 rounded-lg border border-purple-600/50 text-center">
                <div className="text-xs text-purple-400 font-bold mb-2">50% BONUS</div>
                <div className="text-3xl font-bold text-white mb-2">$200</div>
                <div className="text-zinc-400 mb-4">30,000 credits</div>
                <div className="text-sm text-green-400">$0.0067 per credit</div>
              </div>
              <div className="bg-zinc-900 p-6 rounded-lg border border-purple-600 text-center">
                <div className="text-xs text-purple-400 font-bold mb-2">100% BONUS</div>
                <div className="text-3xl font-bold text-white mb-2">$1,000</div>
                <div className="text-zinc-400 mb-4">200,000 credits</div>
                <div className="text-sm text-green-400">$0.005 per credit</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* FAQ */}
      <div className="max-w-4xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          Frequently Asked Questions
        </h2>
        
        <div className="space-y-6">
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <h3 className="text-lg font-bold text-white mb-2">
              What's the difference between Galion Studio and Developer Platform?
            </h3>
            <p className="text-zinc-400">
              <strong className="text-white">Galion Studio</strong> is for creators who want to generate content (images, videos, text). 
              <strong className="text-white ml-1">Developer Platform</strong> is for developers who want API access to integrate AI into their apps.
            </p>
          </div>
          
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <h3 className="text-lg font-bold text-white mb-2">
              Do credits expire?
            </h3>
            <p className="text-zinc-400">
              No! Developer Platform credits never expire. Buy once, use anytime. 
              Studio subscriptions reset monthly.
            </p>
          </div>
          
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <h3 className="text-lg font-bold text-white mb-2">
              Can I upgrade or downgrade anytime?
            </h3>
            <p className="text-zinc-400">
              Yes! Change your plan anytime. Upgrades take effect immediately. 
              Downgrades apply at next billing cycle.
            </p>
          </div>
          
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <h3 className="text-lg font-bold text-white mb-2">
              What happens if I exceed my limits?
            </h3>
            <p className="text-zinc-400">
              Studio: Pay overage rates ($0.05-$0.10 per generation) or upgrade.
              Developer: Buy more credits at any time.
            </p>
          </div>
          
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <h3 className="text-lg font-bold text-white mb-2">
              Is there a free trial?
            </h3>
            <p className="text-zinc-400">
              Yes! Galion Studio offers 14-day free trial. Developer Platform gives 100 free credits.
            </p>
          </div>
          
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <h3 className="text-lg font-bold text-white mb-2">
              What payment methods do you accept?
            </h3>
            <p className="text-zinc-400">
              Credit cards, debit cards, PayPal via Shopify. Enterprise can use invoicing.
            </p>
          </div>
        </div>
      </div>
      
      {/* CTA Section */}
      <div className="border-t border-zinc-800">
        <div className="max-w-4xl mx-auto px-6 py-16 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-zinc-400 mb-8">
            Start with free tier. Upgrade when you need more.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/auth/register"
              className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 
                         hover:to-pink-700 text-white rounded-lg font-bold text-lg transition"
            >
              Start Free Trial
            </Link>
            <Link
              href="/contact"
              className="px-8 py-4 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg font-bold text-lg transition"
            >
              Contact Sales
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

