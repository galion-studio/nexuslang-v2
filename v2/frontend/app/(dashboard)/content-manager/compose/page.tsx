/**
 * Content Compose Interface
 * Multi-platform post creation with scheduling
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import contentManagerAPI from '@/lib/api/content-manager-api';

interface Brand {
  id: string;
  name: string;
  slug: string;
  brand_color: string;
}

const PLATFORMS = [
  { id: 'reddit', name: 'Reddit', icon: '👽', maxLength: 40000 },
  { id: 'twitter', name: 'Twitter/X', icon: '𝕏', maxLength: 280 },
  { id: 'instagram', name: 'Instagram', icon: '📷', maxLength: 2200 },
  { id: 'facebook', name: 'Facebook', icon: '👤', maxLength: 63206 },
  { id: 'linkedin', name: 'LinkedIn', icon: '💼', maxLength: 3000 },
  { id: 'tiktok', name: 'TikTok', icon: '🎵', maxLength: 2200 },
  { id: 'youtube', name: 'YouTube', icon: '▶️', maxLength: 5000 },
];

export default function ComposePage() {
  const router = useRouter();
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [hashtagInput, setHashtagInput] = useState('');
  const [status, setStatus] = useState<'draft' | 'scheduled' | 'publish'>('draft');
  const [scheduledDate, setScheduledDate] = useState('');
  const [scheduledTime, setScheduledTime] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadBrands();
  }, []);

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

  const togglePlatform = (platformId: string) => {
    setSelectedPlatforms(prev =>
      prev.includes(platformId)
        ? prev.filter(p => p !== platformId)
        : [...prev, platformId]
    );
  };

  const addHashtag = () => {
    if (hashtagInput.trim()) {
      const tag = hashtagInput.trim().replace(/^#/, '');
      if (!hashtags.includes(tag)) {
        setHashtags([...hashtags, tag]);
      }
      setHashtagInput('');
    }
  };

  const removeHashtag = (tag: string) => {
    setHashtags(hashtags.filter(t => t !== tag));
  };

  const getMinMaxLength = () => {
    if (selectedPlatforms.length === 0) return { min: 0, max: 10000 };
    const lengths = selectedPlatforms.map(p => 
      PLATFORMS.find(platform => platform.id === p)?.maxLength || 10000
    );
    return { min: 0, max: Math.min(...lengths) };
  };

  const handleSave = async () => {
    if (!selectedBrand || !content) {
      alert('Please select a brand and enter content');
      return;
    }

    if (selectedPlatforms.length === 0) {
      alert('Please select at least one platform');
      return;
    }

    setSaving(true);
    try {
      const postData: any = {
        brand_id: selectedBrand,
        title: title || null,
        content: content,
        platforms: selectedPlatforms,
        hashtags: hashtags,
        status: status === 'publish' ? 'publishing' : status
      };

      if (status === 'scheduled' && scheduledDate && scheduledTime) {
        postData.scheduled_at = `${scheduledDate}T${scheduledTime}:00Z`;
      }

      const result = await contentManagerAPI.createPost(postData);

      // If publishing now, trigger publish
      if (status === 'publish') {
        await contentManagerAPI.publishPost(result.id);
        alert('Post published successfully!');
      } else {
        alert(`Post saved as ${status}!`);
      }

      router.push('/content-manager');
    } catch (error) {
      console.error('Error saving post:', error);
      alert('Error saving post. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const maxLength = getMinMaxLength().max;
  const remainingChars = maxLength - content.length;
  const isOverLimit = remainingChars < 0;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Create Post
            </h1>
            <p className="text-gray-600">
              Compose content for multiple platforms
            </p>
          </div>
          <button
            onClick={() => router.push('/content-manager')}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Brand Selection */}
            <div className="bg-white p-6 rounded-lg shadow">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Brand
              </label>
              <select
                value={selectedBrand}
                onChange={(e) => setSelectedBrand(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Brand</option>
                {brands.map((brand) => (
                  <option key={brand.id} value={brand.id}>
                    {brand.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Title */}
            <div className="bg-white p-6 rounded-lg shadow">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Title (Optional)
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter post title..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Content */}
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Content
                </label>
                <span className={`text-sm ${isOverLimit ? 'text-red-600' : 'text-gray-500'}`}>
                  {remainingChars} characters remaining
                </span>
              </div>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Write your post content..."
                rows={12}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 resize-none ${
                  isOverLimit ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              <div className="mt-2 text-xs text-gray-500">
                {selectedPlatforms.length > 0 && (
                  <div>Max length for selected platforms: {maxLength} characters</div>
                )}
              </div>
            </div>

            {/* Hashtags */}
            <div className="bg-white p-6 rounded-lg shadow">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hashtags
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={hashtagInput}
                  onChange={(e) => setHashtagInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addHashtag()}
                  placeholder="Add hashtag..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={addHashtag}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {hashtags.map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm flex items-center gap-2"
                  >
                    #{tag}
                    <button
                      onClick={() => removeHashtag(tag)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Platform Selection */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 mb-4">
                Select Platforms
              </h3>
              <div className="space-y-2">
                {PLATFORMS.map((platform) => (
                  <label
                    key={platform.id}
                    className="flex items-center gap-3 p-2 rounded hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedPlatforms.includes(platform.id)}
                      onChange={() => togglePlatform(platform.id)}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span className="text-xl">{platform.icon}</span>
                    <span className="text-sm text-gray-700">{platform.name}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Scheduling */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 mb-4">
                Publishing Options
              </h3>
              <div className="space-y-3">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="status"
                    checked={status === 'draft'}
                    onChange={() => setStatus('draft')}
                    className="w-4 h-4 text-blue-600"
                  />
                  <span className="text-sm text-gray-700">Save as Draft</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="status"
                    checked={status === 'scheduled'}
                    onChange={() => setStatus('scheduled')}
                    className="w-4 h-4 text-blue-600"
                  />
                  <span className="text-sm text-gray-700">Schedule for Later</span>
                </label>
                {status === 'scheduled' && (
                  <div className="ml-6 space-y-2">
                    <input
                      type="date"
                      value={scheduledDate}
                      onChange={(e) => setScheduledDate(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                    <input
                      type="time"
                      value={scheduledTime}
                      onChange={(e) => setScheduledTime(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
                    />
                  </div>
                )}
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="status"
                    checked={status === 'publish'}
                    onChange={() => setStatus('publish')}
                    className="w-4 h-4 text-blue-600"
                  />
                  <span className="text-sm text-gray-700">Publish Now</span>
                </label>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-3">
              <button
                onClick={handleSave}
                disabled={saving || isOverLimit}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {saving ? 'Saving...' : status === 'publish' ? 'Publish Now' : 'Save Post'}
              </button>
              <button
                onClick={() => router.push('/content-manager')}
                className="w-full px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

