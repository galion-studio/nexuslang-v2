'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  TrendingUp, TrendingDown, Eye, Heart, Share, MessageCircle,
  Zap, Users, Clock, Target, BarChart3, Activity
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface StatCardProps {
  title: string
  value: string | number
  change?: number
  changeLabel?: string
  icon: React.ReactNode
  color: string
  delay?: number
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  changeLabel,
  icon,
  color,
  delay = 0
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      <Card className="relative overflow-hidden group hover:shadow-lg transition-all duration-300">
        <div className={cn(
          "absolute top-0 left-0 w-1 h-full",
          color
        )} />
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          <div className={cn(
            "p-2 rounded-lg group-hover:scale-110 transition-transform duration-300",
            color.replace('bg-', 'bg-').replace('-500', '-100'),
            color.replace('bg-', 'text-')
          )}>
            {icon}
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold mb-1">{value}</div>
          {change !== undefined && (
            <div className="flex items-center text-xs">
              {change > 0 ? (
                <TrendingUp className="h-3 w-3 text-green-500 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 text-red-500 mr-1" />
              )}
              <span className={change > 0 ? 'text-green-600' : 'text-red-600'}>
                {Math.abs(change)}%
              </span>
              {changeLabel && (
                <span className="text-muted-foreground ml-1">{changeLabel}</span>
              )}
            </div>
          )}
        </CardContent>

        {/* Animated background effect */}
        <div className={cn(
          "absolute inset-0 opacity-0 group-hover:opacity-5 transition-opacity duration-300 rounded-lg",
          color
        )} />
      </Card>
    </motion.div>
  )
}

interface EnhancedStatsProps {
  stats: {
    credits: number
    voiceInteractions: number
    subscriptionTier: string
    monthlyUsage: number
    dailyUsage: number
    avgSessionTime: number
    topCommands: Array<{ command: string; count: number }>
    recentActivity: Array<{
      id: string
      type: string
      description: string
      timestamp: string
      creditsUsed: number
    }>
  }
}

export const EnhancedStats: React.FC<EnhancedStatsProps> = ({ stats }) => {
  const statCards = [
    {
      title: 'Voice Credits',
      value: stats.credits,
      change: 12,
      changeLabel: 'from last month',
      icon: <Zap className="h-4 w-4" />,
      color: 'bg-blue-500'
    },
    {
      title: 'Monthly Usage',
      value: stats.monthlyUsage,
      change: 8,
      changeLabel: 'from last month',
      icon: <Activity className="h-4 w-4" />,
      color: 'bg-green-500',
      delay: 0.1
    },
    {
      title: 'Today\'s Usage',
      value: stats.dailyUsage,
      change: -3,
      changeLabel: 'from yesterday',
      icon: <Clock className="h-4 w-4" />,
      color: 'bg-purple-500',
      delay: 0.2
    },
    {
      title: 'Avg Session',
      value: `${stats.avgSessionTime}min`,
      change: 15,
      changeLabel: 'longer sessions',
      icon: <Target className="h-4 w-4" />,
      color: 'bg-orange-500',
      delay: 0.3
    }
  ]

  return (
    <div className="space-y-6">
      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => (
          <StatCard key={index} {...card} />
        ))}
      </div>

      {/* Usage Overview with Enhanced Visualization */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Commands */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Most Used Commands
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.topCommands.map((command, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="flex items-center justify-between p-3 rounded-lg bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                        {index + 1}
                      </span>
                    </div>
                    <span className="text-sm font-medium">"{command.command}"</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-green-600">
                      {command.count} times
                    </span>
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Weekly Usage Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Weekly Usage Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-48 flex items-end justify-between space-x-2">
              {[45, 52, 48, 61, 39, 28, 22].map((count, index) => (
                <motion.div
                  key={index}
                  initial={{ height: 0 }}
                  animate={{ height: `${(count / 70) * 150}px` }}
                  transition={{
                    duration: 0.8,
                    delay: index * 0.1,
                    ease: 'easeOut'
                  }}
                  className="flex flex-col items-center group"
                >
                  <div
                    className="bg-gradient-to-t from-blue-500 to-blue-600 rounded-t w-8 transition-all duration-300 group-hover:from-blue-600 group-hover:to-blue-700 group-hover:scale-110 shadow-sm group-hover:shadow-lg"
                    style={{ height: `${(count / 70) * 150}px` }}
                  />
                  <span className="text-xs mt-2 text-muted-foreground group-hover:text-foreground transition-colors">
                    {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index]}
                  </span>
                  <span className="text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity absolute -top-6 bg-gray-900 text-white px-2 py-1 rounded">
                    {count}
                  </span>
                </motion.div>
              ))}
            </div>
            <div className="flex justify-between text-xs text-muted-foreground mt-4">
              <span>Weekly average: 42 interactions</span>
              <span className="text-green-600">↑ 12% vs last week</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Enhanced Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {stats.recentActivity.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-3">
                  <div className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center",
                    activity.type === 'voice_command' ? 'bg-blue-100 text-blue-600' :
                    activity.type === 'subscription' ? 'bg-green-100 text-green-600' :
                    'bg-gray-100 text-gray-600'
                  )}>
                    {activity.type === 'voice_command' ? <MessageCircle className="h-5 w-5" /> :
                     activity.type === 'subscription' ? <Users className="h-5 w-5" /> :
                     <Activity className="h-5 w-5" />}
                  </div>
                  <div>
                    <p className="font-medium">{activity.description}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(activity.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
                {activity.creditsUsed > 0 && (
                  <div className="text-right">
                    <p className="font-semibold text-orange-600">
                      -{activity.creditsUsed} credits
                    </p>
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Zap className="h-3 w-3" />
                      Voice interaction
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>

          <div className="mt-6 text-center">
            <button className="text-blue-600 hover:text-blue-700 font-semibold hover:underline transition-colors">
              View detailed analytics →
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions with Enhanced UI */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            title: 'Voice Assistant',
            description: 'Start a conversation',
            icon: <MessageCircle className="h-6 w-6" />,
            color: 'from-blue-500 to-cyan-500',
            href: '/voice'
          },
          {
            title: 'Analytics',
            description: 'View insights',
            icon: <BarChart3 className="h-6 w-6" />,
            color: 'from-green-500 to-emerald-500',
            href: '/analytics'
          },
          {
            title: 'Grokopedia',
            description: 'Search knowledge base',
            icon: <Eye className="h-6 w-6" />,
            color: 'from-purple-500 to-pink-500',
            href: '/grokopedia'
          },
          {
            title: 'Billing',
            description: 'Manage credits',
            icon: <Zap className="h-6 w-6" />,
            color: 'from-orange-500 to-red-500',
            href: '/billing'
          }
        ].map((action, index) => (
          <motion.a
            key={index}
            href={action.href}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="block"
          >
            <Card className="hover:shadow-lg transition-all duration-300 hover:scale-105 cursor-pointer group">
              <CardContent className="p-6 text-center">
                <div className={cn(
                  "w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-r flex items-center justify-center text-white shadow-lg group-hover:shadow-xl transition-all duration-300",
                  action.color
                )}>
                  {action.icon}
                </div>
                <h3 className="font-semibold mb-2 group-hover:text-blue-600 transition-colors">
                  {action.title}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {action.description}
                </p>
              </CardContent>
            </Card>
          </motion.a>
        ))}
      </div>
    </div>
  )
}
