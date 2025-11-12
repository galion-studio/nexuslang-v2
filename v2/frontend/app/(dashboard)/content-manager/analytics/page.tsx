/**
 * Analytics Dashboard
 * Cross-platform metrics and insights
 */

'use client';

import { useState, useEffect } from 'react';
import contentManagerAPI from '@/lib/api/content-manager-api';

interface Brand {
  id: string;
  name: string;
}

interface BrandAnalytics {
  period_days: number;
  total_posts: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  total_views: number;
  avg_engagement_rate: number;
}

export default function AnalyticsPage() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [timeframe, setTimeframe] = useState(30);
  const [analytics, setAnalytics] = useState<BrandAnalytics | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadBrands();
  }, []);

  useEffect(() => {
    if (selectedBrand) {
      loadAnalytics();
    }
  }, [selectedBrand, timeframe]);

  const loadBrands = async () => {
    try {
      const data = await contentManagerAPI.getBrands();
      setBrands(data);
      if (data.length > 0) {
        setSelectedBrand(data[0].id);
      }
    } catch (error) {
      console.error('Error loading brands:', error);
    }
  };

  const loadAnalytics = async () => {
    if (!selectedBrand) return;
    
    setLoading(true);
    try {
      const data = await contentManagerAPI.getBrandAnalytics(selectedBrand, timeframe);
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Analytics Dashboard
          </h1>
          <p className="text-gray-600">
            Track your social media performance across all platforms
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Brand
              </label>
              <select
                value={selectedBrand}
                onChange={(e) => setSelectedBrand(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {brands.map((brand) => (
                  <option key={brand.id} value={brand.id}>
                    {brand.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Timeframe
              </label>
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
              </select>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="text-gray-500">Loading analytics...</div>
          </div>
        ) : analytics ? (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Total Posts</span>
                  <span className="text-2xl">📝</span>
                </div>
                <div className="text-3xl font-bold text-gray-900">
                  {analytics.total_posts}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Last {timeframe} days
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Total Likes</span>
                  <span className="text-2xl">❤️</span>
                </div>
                <div className="text-3xl font-bold text-pink-600">
                  {analytics.total_likes.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Across all platforms
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Total Comments</span>
                  <span className="text-2xl">💬</span>
                </div>
                <div className="text-3xl font-bold text-blue-600">
                  {analytics.total_comments.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Engagement count
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Avg Engagement</span>
                  <span className="text-2xl">📊</span>
                </div>
                <div className="text-3xl font-bold text-purple-600">
                  {analytics.avg_engagement_rate.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Engagement rate
                </div>
              </div>
            </div>

            {/* Detailed Metrics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Engagement Breakdown */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Engagement Breakdown
                </h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Likes</span>
                      <span className="font-medium">{analytics.total_likes.toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-pink-500 h-2 rounded-full"
                        style={{
                          width: `${(analytics.total_likes / (analytics.total_likes + analytics.total_comments + analytics.total_shares)) * 100}%`
                        }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Comments</span>
                      <span className="font-medium">{analytics.total_comments.toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{
                          width: `${(analytics.total_comments / (analytics.total_likes + analytics.total_comments + analytics.total_shares)) * 100}%`
                        }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Shares</span>
                      <span className="font-medium">{analytics.total_shares.toLocaleString()}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{
                          width: `${(analytics.total_shares / (analytics.total_likes + analytics.total_comments + analytics.total_shares)) * 100}%`
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Views & Reach */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Reach & Impact
                </h3>
                <div className="space-y-6">
                  <div>
                    <div className="text-sm text-gray-600 mb-1">Total Views</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {analytics.total_views.toLocaleString()}
                    </div>
                    <div className="text-xs text-gray-500">
                      Content impressions
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 mb-1">Engagement Rate</div>
                    <div className="flex items-baseline gap-2">
                      <div className="text-2xl font-bold text-purple-600">
                        {analytics.avg_engagement_rate.toFixed(2)}%
                      </div>
                      <div className="text-sm text-gray-500">average</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Tips */}
            <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="font-semibold text-blue-900 mb-2">
                💡 Performance Insights
              </h3>
              <ul className="space-y-1 text-sm text-blue-800">
                {analytics.avg_engagement_rate > 3 ? (
                  <li>✅ Great engagement rate! Your content is resonating well.</li>
                ) : (
                  <li>📈 Try posting at different times to improve engagement.</li>
                )}
                {analytics.total_posts < 10 ? (
                  <li>📝 Post more consistently to build audience engagement.</li>
                ) : (
                  <li>✅ Good posting frequency! Keep it up.</li>
                )}
                <li>🎯 Focus on platforms with the highest engagement rates.</li>
              </ul>
            </div>
          </>
        ) : (
          <div className="text-center py-12 text-gray-500">
            Select a brand to view analytics
          </div>
        )}
      </div>
    </div>
  );
}

