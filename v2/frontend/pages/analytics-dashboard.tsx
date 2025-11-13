/**
 * Analytics Dashboard
 * 
 * View usage statistics, metrics, and insights.
 * Track API usage, credits, and performance.
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function AnalyticsDashboard() {
  const router = useRouter();
  const [analytics, setAnalytics] = useState<any>(null);
  const [featureUsage, setFeatureUsage] = useState<any>(null);
  const [systemStats, setSystemStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('week');

  // Fetch analytics data
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          router.push('/login');
          return;
        }

        // Fetch user analytics
        const analyticsRes = await fetch('/api/v2/analytics/user', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (analyticsRes.ok) {
          const data = await analyticsRes.json();
          setAnalytics(data);
        }

        // Fetch feature usage
        const featureRes = await fetch('/api/v2/analytics/feature-usage', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (featureRes.ok) {
          const data = await featureRes.json();
          setFeatureUsage(data);
        }

        // Fetch system stats
        const systemRes = await fetch('/api/v2/analytics/system');
        if (systemRes.ok) {
          const data = await systemRes.json();
          setSystemStats(data);
        }

      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Track your usage, monitor performance, and gain insights.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Total Requests</h3>
            <p className="mt-2 text-3xl font-bold text-gray-900">
              {analytics?.total_requests || 0}
            </p>
            <p className="mt-1 text-sm text-green-600">+12% from last week</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Credits Used</h3>
            <p className="mt-2 text-3xl font-bold text-gray-900">
              {analytics?.total_credits_used?.toFixed(2) || '0.00'}
            </p>
            <p className="mt-1 text-sm text-blue-600">$0.01 per credit</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Projects</h3>
            <p className="mt-2 text-3xl font-bold text-gray-900">
              {analytics?.projects_created || 0}
            </p>
            <p className="mt-1 text-sm text-gray-500">Active projects</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500">Success Rate</h3>
            <p className="mt-2 text-3xl font-bold text-gray-900">
              {systemStats?.requests?.success_rate || 99}%
            </p>
            <p className="mt-1 text-sm text-green-600">Excellent</p>
          </div>
        </div>

        {/* Feature Usage Chart */}
        {featureUsage && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Feature Usage</h2>
            <div className="space-y-4">
              {featureUsage.features.map((feature: any) => (
                <div key={feature.name}>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">
                      {feature.name}
                    </span>
                    <span className="text-sm text-gray-500">
                      {feature.count} ({feature.percentage.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${feature.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Activity Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Activity Breakdown</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-700">AI Chat</span>
                <span className="font-semibold">{analytics?.ai_chat_count || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Code Executions</span>
                <span className="font-semibold">{analytics?.code_executions || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Image Generations</span>
                <span className="font-semibold">{analytics?.image_generations || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Video Generations</span>
                <span className="font-semibold">{analytics?.video_generations || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Voice Syntheses</span>
                <span className="font-semibold">{analytics?.voice_syntheses || 0}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">System Performance</h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Avg Response Time</span>
                <span className="font-semibold">
                  {systemStats?.performance?.avg_response_time || 0} ms
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">P95 Response Time</span>
                <span className="font-semibold">
                  {systemStats?.performance?.p95_response_time || 0} ms
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Active Users</span>
                <span className="font-semibold">
                  {systemStats?.users?.active || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Uptime</span>
                <span className="font-semibold text-green-600">99.95%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Member Info */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 text-white">
          <h2 className="text-2xl font-bold mb-2">Your Account</h2>
          <p className="text-blue-100 mb-4">
            Member since {analytics?.member_since ? new Date(analytics.member_since).toLocaleDateString() : 'N/A'}
          </p>
          <p className="text-blue-100">
            Last active: {analytics?.last_active ? new Date(analytics.last_active).toLocaleString() : 'N/A'}
          </p>
        </div>
      </div>
    </div>
  );
}

