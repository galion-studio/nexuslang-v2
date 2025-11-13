/**
 * Analytics Page for Galion Studio
 * 
 * View usage statistics and insights.
 */

import { useState, useEffect } from 'react';
import Head from 'next/head';

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [featureUsage, setFeatureUsage] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch user analytics
      const analyticsRes = await fetch('/api/v2/analytics/user', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (analyticsRes.ok) {
        setAnalytics(await analyticsRes.json());
      }

      // Fetch feature usage
      const featureRes = await fetch('/api/v2/analytics/feature-usage', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (featureRes.ok) {
        setFeatureUsage(await featureRes.json());
      }

    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

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
    <>
      <Head>
        <title>Analytics - Galion Studio</title>
      </Head>

      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">Analytics</h1>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Total Requests</h3>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {analytics?.total_requests || 0}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Credits Used</h3>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {analytics?.total_credits_used?.toFixed(2) || '0.00'}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Image Generations</h3>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {analytics?.image_generations || 0}
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Video Generations</h3>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {analytics?.video_generations || 0}
              </p>
            </div>
          </div>

          {/* Feature Usage */}
          {featureUsage && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Feature Usage</h2>
              <div className="space-y-4">
                {featureUsage.features.map((feature: any) => (
                  <div key={feature.name}>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium">{feature.name}</span>
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
        </div>
      </div>
    </>
  );
}

