'use client'

/**
 * Admin Dashboard - Main Overview Page
 * Requires admin or super_admin role
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

interface SystemStats {
  total_users: number
  active_users: number
  beta_testers: number
  total_feedback: number
  critical_bugs: number
}

export default function AdminDashboard() {
  const router = useRouter()
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        router.push('/login')
        return
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/admin/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.status === 403) {
        setError('You do not have permission to access the admin dashboard')
        return
      }

      if (!response.ok) {
        throw new Error('Failed to fetch stats')
      }

      const data = await response.json()
      setStats(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md">
          <div className="text-red-600 text-center">
            <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h2 className="text-xl font-bold mb-2">Access Denied</h2>
            <p className="text-gray-600">{error}</p>
            <Link href="/" className="mt-4 inline-block text-blue-600 hover:underline">
              Return to Home
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600 mt-1">Project Nexus Administration</p>
            </div>
            <Link href="/" className="text-blue-600 hover:text-blue-800">
              ← Back to App
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <StatCard
            title="Total Users"
            value={stats?.total_users || 0}
            icon="👥"
            color="blue"
          />
          <StatCard
            title="Active Users (30d)"
            value={stats?.active_users || 0}
            icon="⚡"
            color="green"
          />
          <StatCard
            title="Beta Testers"
            value={stats?.beta_testers || 0}
            icon="🧪"
            color="purple"
          />
          <StatCard
            title="Total Feedback"
            value={stats?.total_feedback || 0}
            icon="💬"
            color="yellow"
          />
          <StatCard
            title="Critical Bugs"
            value={stats?.critical_bugs || 0}
            icon="🐛"
            color={stats && stats.critical_bugs > 0 ? "red" : "gray"}
          />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ActionCard
            title="User Management"
            description="View, edit, and manage user accounts"
            href="/admin/users"
            icon="👤"
          />
          <ActionCard
            title="Beta Testers"
            description="Manage beta tester invitations and cohorts"
            href="/admin/beta-testers"
            icon="🧪"
          />
          <ActionCard
            title="Feature Flags"
            description="Control feature rollout and availability"
            href="/admin/feature-flags"
            icon="🚩"
          />
          <ActionCard
            title="Feedback & Bugs"
            description="Review user feedback and bug reports"
            href="/admin/feedback"
            icon="📝"
          />
          <ActionCard
            title="Analytics"
            description="View system analytics and metrics"
            href="/admin/analytics"
            icon="📊"
          />
          <ActionCard
            title="System Health"
            description="Monitor system health and performance"
            href="/admin/system"
            icon="💚"
          />
        </div>
      </main>
    </div>
  )
}

// StatCard Component
function StatCard({ title, value, icon, color }: {
  title: string
  value: number
  icon: string
  color: string
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    yellow: 'bg-yellow-50 text-yellow-600 border-yellow-200',
    red: 'bg-red-50 text-red-600 border-red-200',
    gray: 'bg-gray-50 text-gray-600 border-gray-200'
  }

  return (
    <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${colorClasses[color as keyof typeof colorClasses]}`}>
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value.toLocaleString()}</p>
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  )
}

// ActionCard Component
function ActionCard({ title, description, href, icon }: {
  title: string
  description: string
  href: string
  icon: string
}) {
  return (
    <Link href={href}>
      <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 hover:border-blue-300">
        <div className="flex items-start space-x-4">
          <span className="text-4xl">{icon}</span>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
            <p className="text-sm text-gray-600">{description}</p>
          </div>
        </div>
      </div>
    </Link>
  )
}

