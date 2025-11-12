/**
 * Content Manager Dashboard
 * Main overview page for multi-brand social media management
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import contentManagerAPI from '@/lib/api/content-manager-api';

interface DashboardStats {
  totalPosts: number;
  scheduledPosts: number;
  publishedToday: number;
  totalEngagement: number;
}

interface Brand {
  id: string;
  name: string;
  slug: string;
  brand_color: string;
  is_active: boolean;
}

interface RecentPost {
  id: string;
  title: string;
  status: string;
  scheduled_at: string | null;
  published_at: string | null;
  platforms: string[];
}

export default function ContentManagerDashboard() {
  const router = useRouter();
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string | null>(null);
  const [recentPosts, setRecentPosts] = useState<RecentPost[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    totalPosts: 0,
    scheduledPosts: 0,
    publishedToday: 0,
    totalEngagement: 0
  });
  const [loading, setLoading] = useState(true);

  // Fetch brands on mount
  useEffect(() => {
    loadBrands();
  }, []);

  // Fetch data when brand changes
  useEffect(() => {
    if (selectedBrand) {
      loadDashboardData();
    }
  }, [selectedBrand]);

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

  const loadDashboardData = async () => {
    if (!selectedBrand) return;
    
    setLoading(true);
    try {
      // Load recent posts
      const posts = await contentManagerAPI.getPosts({
        brand_id: selectedBrand,
        limit: 10
      });
      setRecentPosts(posts);

      // Calculate stats
      const totalPosts = posts.length;
      const scheduledPosts = posts.filter((p: RecentPost) => p.status === 'scheduled').length;
      const today = new Date().toISOString().split('T')[0];
      const publishedToday = posts.filter(
        (p: RecentPost) => p.published_at && p.published_at.startsWith(today)
      ).length;

      // Get analytics
      try {
        const analytics = await contentManagerAPI.getBrandAnalytics(selectedBrand, 30);
        setStats({
          totalPosts,
          scheduledPosts,
          publishedToday,
          totalEngagement: analytics.total_likes + analytics.total_comments + analytics.total_shares
        });
      } catch {
        setStats({ totalPosts, scheduledPosts, publishedToday, totalEngagement: 0 });
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'bg-green-100 text-green-800';
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPlatformIcon = (platform: string) => {
    const icons: Record<string, string> = {
      twitter: '𝕏',
      reddit: '👽',
      instagram: '📷',
      facebook: '👤',
      linkedin: '💼',
      tiktok: '🎵',
      youtube: '▶️'
    };
    return icons[platform] || '📱';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Content Manager
          </h1>
          <p className="text-gray-600">
            Multi-brand social media management platform
          </p>
        </div>

        {/* Brand Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Brand
          </label>
          <select
            value={selectedBrand || ''}
            onChange={(e) => setSelectedBrand(e.target.value)}
            className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            {brands.map((brand) => (
              <option key={brand.id} value={brand.id}>
                {brand.name}
              </option>
            ))}
          </select>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <button
            onClick={() => router.push('/content-manager/compose')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-4 rounded-lg font-semibold transition-colors"
          >
            ✍️ Create Post
          </button>
          <button
            onClick={() => router.push('/content-manager/calendar')}
            className="bg-white hover:bg-gray-50 text-gray-900 px-6 py-4 rounded-lg font-semibold border border-gray-300 transition-colors"
          >
            📅 Calendar
          </button>
          <button
            onClick={() => router.push('/content-manager/analytics')}
            className="bg-white hover:bg-gray-50 text-gray-900 px-6 py-4 rounded-lg font-semibold border border-gray-300 transition-colors"
          >
            📊 Analytics
          </button>
          <button
            onClick={() => router.push('/content-manager/settings')}
            className="bg-white hover:bg-gray-50 text-gray-900 px-6 py-4 rounded-lg font-semibold border border-gray-300 transition-colors"
          >
            ⚙️ Settings
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600 mb-1">Total Posts</div>
            <div className="text-3xl font-bold text-gray-900">{stats.totalPosts}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600 mb-1">Scheduled</div>
            <div className="text-3xl font-bold text-blue-600">{stats.scheduledPosts}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600 mb-1">Published Today</div>
            <div className="text-3xl font-bold text-green-600">{stats.publishedToday}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-600 mb-1">Total Engagement</div>
            <div className="text-3xl font-bold text-purple-600">
              {stats.totalEngagement.toLocaleString()}
            </div>
          </div>
        </div>

        {/* Recent Posts */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Recent Posts</h2>
          </div>
          <div className="p-6">
            {loading ? (
              <div className="text-center py-8 text-gray-500">Loading...</div>
            ) : recentPosts.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No posts yet. Create your first post!
              </div>
            ) : (
              <div className="space-y-4">
                {recentPosts.map((post) => (
                  <div
                    key={post.id}
                    className="flex items-start justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                    onClick={() => router.push(`/content-manager/posts/${post.id}`)}
                  >
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 mb-1">
                        {post.title || 'Untitled Post'}
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(post.status)}`}>
                          {post.status}
                        </span>
                        <span>•</span>
                        <div className="flex gap-1">
                          {post.platforms.map((platform) => (
                            <span key={platform} title={platform}>
                              {getPlatformIcon(platform)}
                            </span>
                          ))}
                        </div>
                        {post.scheduled_at && (
                          <>
                            <span>•</span>
                            <span>
                              {new Date(post.scheduled_at).toLocaleDateString()}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        // Handle edit/view
                      }}
                      className="text-blue-600 hover:text-blue-700 px-3 py-1"
                    >
                      View →
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

