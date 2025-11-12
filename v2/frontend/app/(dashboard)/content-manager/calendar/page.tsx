/**
 * Calendar View
 * Visual schedule of all content posts
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import contentManagerAPI from '@/lib/api/content-manager-api';

interface Brand {
  id: string;
  name: string;
  brand_color: string;
}

interface Post {
  id: string;
  title: string;
  status: string;
  scheduled_at: string | null;
  published_at: string | null;
  platforms: string[];
  brand_id: string;
}

export default function CalendarPage() {
  const router = useRouter();
  const [brands, setBrands] = useState<Brand[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedBrand, setSelectedBrand] = useState<string>('all');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadBrands();
  }, []);

  useEffect(() => {
    loadPosts();
  }, [selectedBrand, currentDate]);

  const loadBrands = async () => {
    try {
      const data = await contentManagerAPI.getBrands();
      setBrands(data);
    } catch (error) {
      console.error('Error loading brands:', error);
    }
  };

  const loadPosts = async () => {
    setLoading(true);
    try {
      const filters: any = { limit: 100 };
      if (selectedBrand !== 'all') {
        filters.brand_id = selectedBrand;
      }
      const data = await contentManagerAPI.getPosts(filters);
      setPosts(data);
    } catch (error) {
      console.error('Error loading posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    return { daysInMonth, startingDayOfWeek };
  };

  const getPostsForDate = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return posts.filter(post => {
      const postDate = post.scheduled_at || post.published_at;
      return postDate && postDate.startsWith(dateStr);
    });
  };

  const previousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  const today = () => {
    setCurrentDate(new Date());
  };

  const { daysInMonth, startingDayOfWeek } = getDaysInMonth(currentDate);
  const monthName = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  const getBrandColor = (brandId: string) => {
    return brands.find(b => b.id === brandId)?.brand_color || '#3B82F6';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'published': return '✅';
      case 'scheduled': return '⏰';
      case 'draft': return '📝';
      default: return '📄';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Content Calendar
          </h1>
          <p className="text-gray-600">
            Schedule and manage your content across all platforms
          </p>
        </div>

        {/* Controls */}
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            {/* Brand Filter */}
            <div className="flex items-center gap-4">
              <label className="text-sm font-medium text-gray-700">
                Filter by Brand:
              </label>
              <select
                value={selectedBrand}
                onChange={(e) => setSelectedBrand(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Brands</option>
                {brands.map((brand) => (
                  <option key={brand.id} value={brand.id}>
                    {brand.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Month Navigation */}
            <div className="flex items-center gap-4">
              <button
                onClick={previousMonth}
                className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                ← Previous
              </button>
              <button
                onClick={today}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Today
              </button>
              <button
                onClick={nextMonth}
                className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Next →
              </button>
            </div>
          </div>
        </div>

        {/* Calendar Grid */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {/* Month Header */}
          <div className="bg-gray-100 px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              {monthName}
            </h2>
          </div>

          {/* Calendar */}
          <div className="p-4">
            {/* Day Headers */}
            <div className="grid grid-cols-7 gap-2 mb-2">
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                <div
                  key={day}
                  className="text-center text-sm font-semibold text-gray-600 py-2"
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar Days */}
            <div className="grid grid-cols-7 gap-2">
              {/* Empty cells for days before month starts */}
              {Array.from({ length: startingDayOfWeek }).map((_, index) => (
                <div key={`empty-${index}`} className="h-24 border border-gray-200 rounded-lg bg-gray-50" />
              ))}

              {/* Days of the month */}
              {Array.from({ length: daysInMonth }).map((_, dayIndex) => {
                const day = dayIndex + 1;
                const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
                const postsForDay = getPostsForDate(date);
                const isToday = 
                  date.toDateString() === new Date().toDateString();

                return (
                  <div
                    key={day}
                    className={`h-24 border rounded-lg p-2 hover:bg-gray-50 cursor-pointer ${
                      isToday ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                    }`}
                    onClick={() => {
                      // Could open a modal to create post for this day
                    }}
                  >
                    <div className={`text-sm font-semibold mb-1 ${
                      isToday ? 'text-blue-600' : 'text-gray-700'
                    }`}>
                      {day}
                    </div>
                    <div className="space-y-1 overflow-y-auto max-h-16">
                      {postsForDay.slice(0, 3).map((post) => (
                        <div
                          key={post.id}
                          className="text-xs p-1 rounded cursor-pointer hover:opacity-80"
                          style={{ 
                            backgroundColor: getBrandColor(post.brand_id) + '20',
                            borderLeft: `3px solid ${getBrandColor(post.brand_id)}`
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            router.push(`/content-manager/posts/${post.id}`);
                          }}
                          title={post.title || 'Untitled'}
                        >
                          <div className="truncate flex items-center gap-1">
                            <span>{getStatusIcon(post.status)}</span>
                            <span>{post.title || 'Untitled'}</span>
                          </div>
                        </div>
                      ))}
                      {postsForDay.length > 3 && (
                        <div className="text-xs text-gray-500 text-center">
                          +{postsForDay.length - 3} more
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-6 bg-white p-4 rounded-lg shadow">
          <div className="flex flex-wrap items-center gap-4">
            <div className="text-sm font-medium text-gray-700">Legend:</div>
            <div className="flex items-center gap-2">
              <span>✅</span>
              <span className="text-sm text-gray-600">Published</span>
            </div>
            <div className="flex items-center gap-2">
              <span>⏰</span>
              <span className="text-sm text-gray-600">Scheduled</span>
            </div>
            <div className="flex items-center gap-2">
              <span>📝</span>
              <span className="text-sm text-gray-600">Draft</span>
            </div>
            <div className="ml-auto">
              <button
                onClick={() => router.push('/content-manager/compose')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
              >
                + New Post
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

