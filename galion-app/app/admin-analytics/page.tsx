'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Users,
  Activity,
  DollarSign,
  Clock,
  Globe,
  Smartphone,
  Monitor,
  Tablet,
  Calendar,
  Download
} from 'lucide-react'
import { motion } from 'framer-motion'

interface AnalyticsData {
  overview: {
    totalUsers: number
    activeUsers: number
    totalRevenue: number
    avgSessionTime: number
  }
  userGrowth: {
    period: string
    newUsers: number
    totalUsers: number
    growthRate: number
  }[]
  revenueData: {
    period: string
    revenue: number
    transactions: number
    avgOrderValue: number
  }[]
  usageMetrics: {
    feature: string
    usage: number
    growth: number
    icon: string
  }[]
  deviceBreakdown: {
    device: string
    users: number
    percentage: number
  }[]
  geographicData: {
    country: string
    users: number
    revenue: number
  }[]
}

export default function AdminAnalytics() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d')

  useEffect(() => {
    loadAnalyticsData()
  }, [timeRange])

  const loadAnalyticsData = async () => {
    try {
      // Mock analytics data - in production, this would fetch from analytics service
      const mockData: AnalyticsData = {
        overview: {
          totalUsers: 12470,
          activeUsers: 3421,
          totalRevenue: 45280,
          avgSessionTime: 4.2
        },
        userGrowth: [
          { period: 'Jan', newUsers: 1200, totalUsers: 8200, growthRate: 15.2 },
          { period: 'Feb', newUsers: 1350, totalUsers: 9550, growthRate: 16.5 },
          { period: 'Mar', newUsers: 1420, totalUsers: 10970, growthRate: 15.1 },
          { period: 'Apr', newUsers: 1580, totalUsers: 12550, growthRate: 14.4 },
          { period: 'May', newUsers: 1720, totalUsers: 14270, growthRate: 13.7 },
          { period: 'Jun', newUsers: 1200, totalUsers: 12470, growthRate: 8.4 }
        ],
        revenueData: [
          { period: 'Jan', revenue: 3200, transactions: 145, avgOrderValue: 22.07 },
          { period: 'Feb', revenue: 3800, transactions: 172, avgOrderValue: 22.09 },
          { period: 'Mar', revenue: 4100, transactions: 189, avgOrderValue: 21.69 },
          { period: 'Apr', revenue: 4500, transactions: 203, avgOrderValue: 22.17 },
          { period: 'May', revenue: 4800, transactions: 218, avgOrderValue: 22.02 },
          { period: 'Jun', revenue: 5280, transactions: 245, avgOrderValue: 21.55 }
        ],
        usageMetrics: [
          { feature: 'Voice Assistant', usage: 45280, growth: 23.5, icon: '🎤' },
          { feature: 'Code Editor', usage: 28940, growth: 18.2, icon: '💻' },
          { feature: 'AI Chat', usage: 34560, growth: 31.7, icon: '💬' },
          { feature: 'Analytics', usage: 15670, growth: 12.3, icon: '📊' },
          { feature: 'API Calls', usage: 89450, growth: 45.8, icon: '🔌' }
        ],
        deviceBreakdown: [
          { device: 'Desktop', users: 8920, percentage: 71.5 },
          { device: 'Mobile', users: 2890, percentage: 23.2 },
          { device: 'Tablet', users: 660, percentage: 5.3 }
        ],
        geographicData: [
          { country: 'United States', users: 4230, revenue: 18940 },
          { country: 'United Kingdom', users: 1890, revenue: 8540 },
          { country: 'Germany', users: 1450, revenue: 6230 },
          { country: 'Canada', users: 1230, revenue: 4890 },
          { country: 'Australia', users: 890, revenue: 3120 }
        ]
      }

      setData(mockData)
    } catch (error) {
      console.error('Failed to load analytics data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <BarChart3 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
          <p className="text-muted-foreground">
            Comprehensive insights into platform usage and performance
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex gap-2">
            {(['7d', '30d', '90d', '1y'] as const).map((range) => (
              <Button
                key={range}
                variant={timeRange === range ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTimeRange(range)}
              >
                {range}
              </Button>
            ))}
          </div>
          <Button>
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(data.overview.totalUsers)}</div>
            <div className="flex items-center text-xs text-green-600 mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              +12.5% from last month
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(data.overview.activeUsers)}</div>
            <div className="flex items-center text-xs text-green-600 mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              +8.3% from last month
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(data.overview.totalRevenue)}</div>
            <div className="flex items-center text-xs text-green-600 mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              +15.2% from last month
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Session Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.overview.avgSessionTime}min</div>
            <div className="flex items-center text-xs text-green-600 mt-1">
              <TrendingUp className="h-3 w-3 mr-1" />
              +2.1% from last month
            </div>
          </CardContent>
        </Card>
      </div>

      {/* User Growth Chart */}
      <Card>
        <CardHeader>
          <CardTitle>User Growth</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-end justify-between space-x-2">
            {data.userGrowth.map((item, index) => (
              <div key={index} className="flex flex-col items-center">
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: `${(item.newUsers / 2000) * 200}px` }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="bg-gradient-to-t from-blue-500 to-blue-600 rounded-t w-8 mb-2"
                  style={{ height: `${(item.newUsers / 2000) * 200}px` }}
                />
                <span className="text-xs font-medium">{item.period}</span>
                <span className="text-xs text-muted-foreground">{formatNumber(item.newUsers)}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Feature Usage & Revenue */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Feature Usage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.usageMetrics.map((metric, index) => (
                <motion.div
                  key={metric.feature}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{metric.icon}</span>
                    <div>
                      <h4 className="font-medium">{metric.feature}</h4>
                      <p className="text-sm text-muted-foreground">
                        {formatNumber(metric.usage)} interactions
                      </p>
                    </div>
                  </div>
                  <Badge className="bg-green-100 text-green-800">
                    +{metric.growth}%
                  </Badge>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Revenue Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.revenueData.slice(-4).map((item, index) => (
                <motion.div
                  key={item.period}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <div>
                    <h4 className="font-medium">{item.period} 2024</h4>
                    <p className="text-sm text-muted-foreground">
                      {item.transactions} transactions
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{formatCurrency(item.revenue)}</div>
                    <div className="text-sm text-muted-foreground">
                      ${item.avgOrderValue.toFixed(2)} avg
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Device & Geographic Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Device Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.deviceBreakdown.map((device, index) => (
                <motion.div
                  key={device.device}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    {device.device === 'Desktop' ? (
                      <Monitor className="h-5 w-5 text-gray-600" />
                    ) : device.device === 'Mobile' ? (
                      <Smartphone className="h-5 w-5 text-blue-600" />
                    ) : (
                      <Tablet className="h-5 w-5 text-green-600" />
                    )}
                    <span className="font-medium">{device.device}</span>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{formatNumber(device.users)} users</div>
                    <div className="text-sm text-muted-foreground">
                      {device.percentage}%
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Countries</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.geographicData.map((country, index) => (
                <motion.div
                  key={country.country}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <Globe className="h-5 w-5 text-purple-600" />
                    <div>
                      <h4 className="font-medium">{country.country}</h4>
                      <p className="text-sm text-muted-foreground">
                        {formatNumber(country.users)} users
                      </p>
                    </div>
                  </div>
                  <div className="font-medium text-green-600">
                    {formatCurrency(country.revenue)}
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
