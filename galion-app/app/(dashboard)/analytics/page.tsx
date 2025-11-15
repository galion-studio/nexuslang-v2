'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart3, TrendingUp, Clock, Mic, MessageSquare, Brain } from 'lucide-react'
import { galionAPI } from '@/lib/api-client'
import toast from 'react-hot-toast'

interface AnalyticsData {
  totalInteractions: number
  monthlyInteractions: number
  dailyInteractions: number
  averageSessionLength: number
  topCommands: Array<{ command: string, count: number }>
  hourlyUsage: Array<{ hour: number, count: number }>
  weeklyUsage: Array<{ day: string, count: number }>
  voiceQuality: {
    accuracy: number
    speed: number
    satisfaction: number
  }
}

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      // For now, generate mock data since we don't have real analytics endpoints
      const mockData: AnalyticsData = {
        totalInteractions: 1247,
        monthlyInteractions: 387,
        dailyInteractions: 23,
        averageSessionLength: 4.2,
        topCommands: [
          { command: "Show dashboard", count: 89 },
          { command: "Check credits", count: 67 },
          { command: "Research AI", count: 45 },
          { command: "Open profile", count: 38 },
          { command: "Help", count: 29 }
        ],
        hourlyUsage: [
          { hour: 9, count: 12 }, { hour: 10, count: 18 }, { hour: 11, count: 25 },
          { hour: 12, count: 22 }, { hour: 13, count: 28 }, { hour: 14, count: 35 },
          { hour: 15, count: 32 }, { hour: 16, count: 29 }, { hour: 17, count: 24 },
          { hour: 18, count: 15 }, { hour: 19, count: 8 }, { hour: 20, count: 5 }
        ],
        weeklyUsage: [
          { day: "Mon", count: 45 }, { day: "Tue", count: 52 }, { day: "Wed", count: 48 },
          { day: "Thu", count: 61 }, { day: "Fri", count: 39 }, { day: "Sat", count: 28 },
          { day: "Sun", count: 22 }
        ],
        voiceQuality: {
          accuracy: 94,
          speed: 87,
          satisfaction: 91
        }
      }

      setAnalytics(mockData)
    } catch (error) {
      console.error('Failed to load analytics:', error)
      toast.error('Failed to load analytics data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading analytics...</div>
  }

  return (
    <div className="space-y-8 max-w-6xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Voice Analytics</h1>
        <p className="text-muted-foreground">
          Insights into your voice interaction patterns and performance
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Interactions</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.totalInteractions.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              All-time voice interactions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">This Month</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.monthlyInteractions}</div>
            <p className="text-xs text-muted-foreground">
              Voice interactions this month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Session</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.averageSessionLength}min</div>
            <p className="text-xs text-muted-foreground">
              Average interaction length
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Voice Accuracy</CardTitle>
            <Mic className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.voiceQuality.accuracy}%</div>
            <p className="text-xs text-muted-foreground">
              Speech recognition accuracy
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Hourly Usage */}
        <Card>
          <CardHeader>
            <CardTitle>Hourly Usage Pattern</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end justify-between space-x-2">
              {analytics?.hourlyUsage.map((data, index) => (
                <div key={index} className="flex flex-col items-center">
                  <div
                    className="bg-blue-500 rounded-t w-8 transition-all hover:bg-blue-600"
                    style={{ height: `${(data.count / 40) * 200}px` }}
                  ></div>
                  <span className="text-xs mt-2 text-muted-foreground">
                    {data.hour > 12 ? `${data.hour - 12}P` : `${data.hour}A`}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Weekly Usage */}
        <Card>
          <CardHeader>
            <CardTitle>Weekly Usage Pattern</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end justify-center space-x-4">
              {analytics?.weeklyUsage.map((data, index) => (
                <div key={index} className="flex flex-col items-center">
                  <div
                    className="bg-green-500 rounded-t w-12 transition-all hover:bg-green-600"
                    style={{ height: `${(data.count / 70) * 200}px` }}
                  ></div>
                  <span className="text-xs mt-2 text-muted-foreground">{data.day}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Commands & Quality Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Commands */}
        <Card>
          <CardHeader>
            <CardTitle>Most Used Commands</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analytics?.topCommands.map((command, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                        {index + 1}
                      </span>
                    </div>
                    <span className="text-sm">"{command.command}"</span>
                  </div>
                  <span className="text-sm font-semibold text-muted-foreground">
                    {command.count}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Voice Quality Metrics */}
        <Card>
          <CardHeader>
            <CardTitle>Voice Quality Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Recognition Accuracy</span>
                  <span className="text-sm text-muted-foreground">
                    {analytics?.voiceQuality.accuracy}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${analytics?.voiceQuality.accuracy}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Response Speed</span>
                  <span className="text-sm text-muted-foreground">
                    {analytics?.voiceQuality.speed}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${analytics?.voiceQuality.speed}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">User Satisfaction</span>
                  <span className="text-sm text-muted-foreground">
                    {analytics?.voiceQuality.satisfaction}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-500 h-2 rounded-full"
                    style={{ width: `${analytics?.voiceQuality.satisfaction}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            AI Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
              <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                Peak Usage Time
              </h4>
              <p className="text-sm text-blue-800 dark:text-blue-200">
                Your most active hours are 2-4 PM. Consider scheduling important tasks during this time.
              </p>
            </div>

            <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
              <h4 className="font-semibold text-green-900 dark:text-green-100 mb-2">
                Command Efficiency
              </h4>
              <p className="text-sm text-green-800 dark:text-green-200">
                "Show dashboard" is your most used command. Consider creating a quick access button.
              </p>
            </div>

            <div className="p-4 bg-purple-50 dark:bg-purple-950/20 rounded-lg">
              <h4 className="font-semibold text-purple-900 dark:text-purple-100 mb-2">
                Voice Quality
              </h4>
              <p className="text-sm text-purple-800 dark:text-purple-200">
                Excellent recognition accuracy! Your voice commands are processed with 94% accuracy.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
