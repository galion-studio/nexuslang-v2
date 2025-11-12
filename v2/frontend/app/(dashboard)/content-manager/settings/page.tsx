/**
 * Settings & Account Management
 * Manage brands and connected social accounts
 */

'use client';

import { useState, useEffect } from 'react';
import contentManagerAPI from '@/lib/api/content-manager-api';

interface Brand {
  id: string;
  name: string;
  slug: string;
  brand_color: string;
  website_url: string | null;
  is_active: boolean;
}

interface SocialAccount {
  id: string;
  brand_id: string;
  platform: string;
  account_name: string;
  account_url: string | null;
  is_active: boolean;
  sync_status: string;
  last_synced: string | null;
}

const PLATFORMS = [
  { id: 'reddit', name: 'Reddit', icon: '👽', color: 'bg-orange-500' },
  { id: 'twitter', name: 'Twitter/X', icon: '𝕏', color: 'bg-blue-400' },
  { id: 'instagram', name: 'Instagram', icon: '📷', color: 'bg-pink-500' },
  { id: 'facebook', name: 'Facebook', icon: '👤', color: 'bg-blue-600' },
  { id: 'linkedin', name: 'LinkedIn', icon: '💼', color: 'bg-blue-700' },
  { id: 'tiktok', name: 'TikTok', icon: '🎵', color: 'bg-black' },
  { id: 'youtube', name: 'YouTube', icon: '▶️', color: 'bg-red-600' },
  { id: 'producthunt', name: 'ProductHunt', icon: '🚀', color: 'bg-orange-600' },
  { id: 'devto', name: 'Dev.to', icon: '💻', color: 'bg-gray-900' },
];

export default function SettingsPage() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [accounts, setAccounts] = useState<SocialAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const [showConnectModal, setShowConnectModal] = useState(false);
  const [connectPlatform, setConnectPlatform] = useState('');

  useEffect(() => {
    loadBrands();
  }, []);

  useEffect(() => {
    if (selectedBrand) {
      loadAccounts();
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

  const loadAccounts = async () => {
    if (!selectedBrand) return;
    
    setLoading(true);
    try {
      const data = await contentManagerAPI.getSocialAccounts(selectedBrand);
      setAccounts(data);
    } catch (error) {
      console.error('Error loading accounts:', error);
    } finally {
      setLoading(false);
    }
  };

  const openConnectModal = (platform: string) => {
    setConnectPlatform(platform);
    setShowConnectModal(true);
  };

  const getAccountForPlatform = (platformId: string) => {
    return accounts.find(acc => acc.platform === platformId);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Connected</span>;
      case 'error':
        return <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs">Error</span>;
      case 'expired':
        return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs">Expired</span>;
      default:
        return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs">Pending</span>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Settings
          </h1>
          <p className="text-gray-600">
            Manage your brands and connected social accounts
          </p>
        </div>

        {/* Brand Selector */}
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Brand
          </label>
          <select
            value={selectedBrand}
            onChange={(e) => setSelectedBrand(e.target.value)}
            className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            {brands.map((brand) => (
              <option key={brand.id} value={brand.id}>
                {brand.name}
              </option>
            ))}
          </select>
        </div>

        {/* Brand Details */}
        {selectedBrand && brands.find(b => b.id === selectedBrand) && (
          <div className="bg-white p-6 rounded-lg shadow mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Brand Details
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-600">Name</div>
                <div className="font-medium">{brands.find(b => b.id === selectedBrand)?.name}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Slug</div>
                <div className="font-medium">{brands.find(b => b.id === selectedBrand)?.slug}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Website</div>
                <div className="font-medium">
                  {brands.find(b => b.id === selectedBrand)?.website_url || 'Not set'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Status</div>
                <div className="font-medium">
                  {brands.find(b => b.id === selectedBrand)?.is_active ? (
                    <span className="text-green-600">Active</span>
                  ) : (
                    <span className="text-gray-600">Inactive</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Connected Accounts */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              Connected Accounts
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Connect your social media accounts to start posting
            </p>
          </div>
          <div className="p-6">
            {loading ? (
              <div className="text-center py-8 text-gray-500">Loading...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {PLATFORMS.map((platform) => {
                  const account = getAccountForPlatform(platform.id);
                  return (
                    <div
                      key={platform.id}
                      className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 ${platform.color} rounded-lg flex items-center justify-center text-white text-xl`}>
                          {platform.icon}
                        </div>
                        <div>
                          <div className="font-medium text-gray-900">
                            {platform.name}
                          </div>
                          {account ? (
                            <div className="text-sm text-gray-600">
                              {account.account_name}
                            </div>
                          ) : (
                            <div className="text-sm text-gray-400">
                              Not connected
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {account ? (
                          <>
                            {getStatusBadge(account.sync_status)}
                            <button
                              onClick={() => {/* Handle reconnect */}}
                              className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700"
                            >
                              Reconnect
                            </button>
                          </>
                        ) : (
                          <button
                            onClick={() => openConnectModal(platform.id)}
                            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                          >
                            Connect
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Connect Modal */}
        {showConnectModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Connect {PLATFORMS.find(p => p.id === connectPlatform)?.name}
              </h3>
              <p className="text-gray-600 mb-6">
                To connect your account, you'll need to authorize access through the platform's OAuth flow.
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-yellow-800">
                  <strong>Note:</strong> You'll need to set up a developer app for this platform and configure OAuth credentials.
                  See the documentation for detailed instructions.
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowConnectModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    // Implement OAuth flow
                    alert('OAuth flow would start here. See documentation for setup instructions.');
                    setShowConnectModal(false);
                  }}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Start OAuth
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Documentation Link */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2">
            📚 Need Help Connecting Accounts?
          </h3>
          <p className="text-sm text-blue-800 mb-3">
            Each platform requires OAuth setup. See the implementation guide for detailed instructions on connecting each platform.
          </p>
          <a
            href="/docs/platform-setup"
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            View Platform Setup Guide →
          </a>
        </div>
      </div>
    </div>
  );
}

