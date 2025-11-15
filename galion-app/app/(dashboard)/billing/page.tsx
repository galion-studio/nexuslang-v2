'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CreditCard, TrendingUp, Clock, Download, RefreshCw } from 'lucide-react'
import { galionAPI } from '@/lib/api-client'
import toast from 'react-hot-toast'

interface BillingData {
  credits: number
  subscription: {
    tier: string
    price: number
    nextBilling?: string
  }
  usage: {
    total: number
    monthly: number
    daily: number
  }
  transactions: Array<{
    id: string
    type: string
    amount: number
    description: string
    date: string
  }>
}

export default function BillingPage() {
  const [billingData, setBillingData] = useState<BillingData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadBillingData()
  }, [])

  const loadBillingData = async () => {
    try {
      const [credits, subscription, usage] = await Promise.all([
        galionAPI.getCredits(),
        galionAPI.getSubscriptions(),
        galionAPI.getVoiceUsage()
      ])

      setBillingData({
        credits: credits.balance || 0,
        subscription: {
          tier: subscription.tier || 'Free',
          price: subscription.price || 0,
          nextBilling: subscription.next_billing
        },
        usage: {
          total: usage.total || 0,
          monthly: usage.monthly || 0,
          daily: usage.daily || 0
        },
        transactions: usage.transactions || []
      })
    } catch (error) {
      console.error('Failed to load billing data:', error)
      toast.error('Failed to load billing information')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading billing data...</div>
  }

  return (
    <div className="space-y-8 max-w-6xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Billing & Usage</h1>
        <p className="text-muted-foreground">
          Manage your credits, subscription, and voice usage
        </p>
      </div>

      {/* Current Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Voice Credits</CardTitle>
            <CreditCard className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{billingData?.credits || 0}</div>
            <p className="text-xs text-muted-foreground">
              Available for voice interactions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Usage</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{billingData?.usage.monthly || 0}</div>
            <p className="text-xs text-muted-foreground">
              Voice interactions this month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Daily Usage</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{billingData?.usage.daily || 0}</div>
            <p className="text-xs text-muted-foreground">
              Voice interactions today
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Subscription</CardTitle>
            <RefreshCw className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{billingData?.subscription.tier}</div>
            <p className="text-xs text-muted-foreground">
              {billingData?.subscription.price === 0 ? 'Free tier' : `$${billingData?.subscription.price}/mo`}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Usage Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Voice Usage Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm">Total Interactions</span>
                <span className="font-semibold">{billingData?.usage.total || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">This Month</span>
                <span className="font-semibold">{billingData?.usage.monthly || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Today</span>
                <span className="font-semibold">{billingData?.usage.daily || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Credits Used</span>
                <span className="font-semibold text-orange-600">
                  {Math.round((billingData?.usage.monthly || 0) * 0.5)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cost Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  ${(billingData?.usage.monthly || 0) * 0.05}
                </div>
                <div className="text-sm text-muted-foreground">Estimated cost this month</div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Voice interactions (5¢ each)</span>
                  <span>${(billingData?.usage.monthly || 0) * 0.05}</span>
                </div>
                <div className="flex justify-between">
                  <span>Subscription</span>
                  <span>${billingData?.subscription.price || 0}</span>
                </div>
                <hr className="my-2" />
                <div className="flex justify-between font-semibold">
                  <span>Total</span>
                  <span>
                    ${(billingData?.usage.monthly || 0) * 0.05 + (billingData?.subscription.price || 0)}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Transaction History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Transaction History
            <button className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
              <Download className="h-4 w-4" />
              Export
            </button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {billingData?.transactions.length ? (
            <div className="space-y-4">
              {billingData.transactions.map((transaction) => (
                <div key={transaction.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      transaction.type === 'credit' ? 'bg-green-100 text-green-600' :
                      transaction.type === 'debit' ? 'bg-red-100 text-red-600' :
                      'bg-blue-100 text-blue-600'
                    }`}>
                      {transaction.type === 'credit' ? '+' :
                       transaction.type === 'debit' ? '-' : '='}
                    </div>
                    <div>
                      <p className="font-medium">{transaction.description}</p>
                      <p className="text-sm text-muted-foreground">{transaction.date}</p>
                    </div>
                  </div>
                  <div className={`font-semibold ${
                    transaction.type === 'credit' ? 'text-green-600' :
                    transaction.type === 'debit' ? 'text-red-600' :
                    'text-blue-600'
                  }`}>
                    {transaction.type === 'credit' ? '+' : transaction.type === 'debit' ? '-' : ''}
                    {transaction.amount} credits
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <CreditCard className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No transactions yet</p>
              <p className="text-sm">Start using voice commands to see your billing history</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upgrade Prompt */}
      {billingData?.subscription.tier === 'Free' && (
        <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 border-blue-200 dark:border-blue-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-2">Upgrade to Professional</h3>
                <p className="text-muted-foreground mb-4">
                  Get 2,000 voice interactions per month for just $29
                </p>
                <ul className="text-sm space-y-1 mb-4">
                  <li>• 2,000 voice interactions/month</li>
                  <li>• Advanced voice commands</li>
                  <li>• Priority processing</li>
                  <li>• Custom voice models</li>
                </ul>
              </div>
              <a
                href="/subscription"
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition"
              >
                Upgrade Now
              </a>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
