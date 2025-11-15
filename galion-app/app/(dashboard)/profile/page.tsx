'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PersonalitySettings } from '@/components/settings/PersonalitySettings'
import { AdvancedSettings } from '@/components/settings/AdvancedSettings'
import { User, Mail, Key, Shield, Save, Eye, EyeOff, Brain } from 'lucide-react'
import { galionAPI } from '@/lib/api-client'
import toast from 'react-hot-toast'

interface UserProfile {
  id: string
  email: string
  username: string
  full_name: string
  role: string
  created_at: string
  last_login?: string
  api_key?: string
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [showApiKey, setShowApiKey] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    full_name: '',
    email: ''
  })

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const userData = await galionAPI.getProfile()
      setProfile(userData)
      setFormData({
        username: userData.username || '',
        full_name: userData.full_name || '',
        email: userData.email || ''
      })
    } catch (error) {
      console.error('Failed to load profile:', error)
      toast.error('Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)

    try {
      // In a real implementation, you'd have an update profile endpoint
      // For now, we'll just show success
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call
      toast.success('Profile updated successfully')
    } catch (error) {
      toast.error('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const generateApiKey = async () => {
    try {
      // In a real implementation, this would call an API to generate a new key
      const newKey = 'gal_' + Math.random().toString(36).substring(2, 15)
      setProfile(prev => prev ? { ...prev, api_key: newKey } : null)
      toast.success('New API key generated')
    } catch (error) {
      toast.error('Failed to generate API key')
    }
  }

  if (loading) {
    return <div className="flex justify-center items-center h-64">Loading profile...</div>
  }

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Profile Settings</h1>
        <p className="text-muted-foreground">
          Manage your account information and API access
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Profile Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Personal Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSaveProfile} className="space-y-4">
              <div>
                <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Full Name
                </label>
                <input
                  id="full_name"
                  name="full_name"
                  type="text"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Username
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email Address
                </label>
                <div className="flex items-center">
                  <Mail className="h-4 w-4 text-gray-400 mr-2" />
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={saving}
                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-semibold transition flex items-center justify-center gap-2"
              >
                {saving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    Save Changes
                  </>
                )}
              </button>
            </form>
          </CardContent>
        </Card>

        {/* Account Details */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Account Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Account Type</span>
              <span className="font-semibold capitalize">{profile?.role || 'User'}</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Member Since</span>
              <span className="font-semibold">
                {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Last Login</span>
              <span className="font-semibold">
                {profile?.last_login ? new Date(profile.last_login).toLocaleDateString() : 'Today'}
              </span>
            </div>

            <div className="pt-4 border-t">
              <button className="w-full py-2 px-4 border border-red-300 text-red-600 hover:bg-red-50 dark:border-red-600 dark:text-red-400 dark:hover:bg-red-950/20 rounded-lg transition">
                Delete Account
              </button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* API Access */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            API Access
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              API Key
            </label>
            <div className="flex items-center gap-2">
              <div className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 font-mono text-sm">
                {showApiKey ? (profile?.api_key || 'No API key generated') : '••••••••••••••••••••••••••••••••'}
              </div>
              <button
                onClick={() => setShowApiKey(!showApiKey)}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={generateApiKey}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition"
            >
              Generate New Key
            </button>

            <button
              onClick={() => {
                navigator.clipboard.writeText(profile?.api_key || '')
                toast.success('API key copied to clipboard')
              }}
              disabled={!profile?.api_key}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg font-semibold transition disabled:opacity-50"
            >
              Copy Key
            </button>
          </div>

          <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
            <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
              🔒 API Key Security
            </h4>
            <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
              <li>• Keep your API key secure and never share it publicly</li>
              <li>• Regenerate your key if you suspect it has been compromised</li>
              <li>• Each key is tied to your account and usage limits</li>
              <li>• Monitor your API usage in the billing section</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Advanced Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Advanced Settings
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Customize your AI experience and account preferences
          </p>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="personality" className="space-y-6">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="personality">AI Personality</TabsTrigger>
              <TabsTrigger value="advanced">Advanced Settings</TabsTrigger>
            </TabsList>

            <TabsContent value="personality" className="space-y-6">
              <PersonalitySettings />
            </TabsContent>

            <TabsContent value="advanced" className="space-y-6">
              <AdvancedSettings />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Usage Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Voice Usage Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">1,247</div>
              <div className="text-sm text-muted-foreground">Total Interactions</div>
            </div>

            <div className="text-center p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
              <div className="text-2xl font-bold text-green-600">387</div>
              <div className="text-sm text-muted-foreground">This Month</div>
            </div>

            <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-950/20 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">23</div>
              <div className="text-sm text-muted-foreground">Today</div>
            </div>

            <div className="text-center p-4 bg-purple-50 dark:bg-purple-950/20 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">4.2min</div>
              <div className="text-sm text-muted-foreground">Avg Session</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
