'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Settings,
  Save,
  RotateCcw,
  Shield,
  Database,
  Mail,
  CreditCard,
  Zap,
  Globe,
  Lock,
  Key,
  AlertTriangle,
  CheckCircle,
  RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'

interface SystemSettings {
  general: {
    siteName: string
    siteDescription: string
    contactEmail: string
    maintenanceMode: boolean
    registrationEnabled: boolean
  }
  security: {
    sessionTimeout: number
    passwordMinLength: number
    twoFactorRequired: boolean
    ipWhitelist: string[]
    rateLimitRequests: number
    rateLimitWindow: number
  }
  billing: {
    stripeEnabled: boolean
    paypalEnabled: boolean
    creditCardRequired: boolean
    freeCredits: number
    premiumPrice: number
    currency: string
  }
  api: {
    maxRequestsPerMinute: number
    maxRequestsPerHour: number
    apiKeyExpiration: number
    webhookRetries: number
  }
  notifications: {
    emailEnabled: boolean
    smtpHost: string
    smtpPort: number
    smtpUser: string
    smtpPassword: string
  }
}

export default function AdminSettings() {
  const [settings, setSettings] = useState<SystemSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      // Mock data - in production, this would fetch from your backend
      const mockSettings: SystemSettings = {
        general: {
          siteName: 'Galion.app',
          siteDescription: 'Advanced AI Voice Assistant Platform',
          contactEmail: 'support@galion.app',
          maintenanceMode: false,
          registrationEnabled: true
        },
        security: {
          sessionTimeout: 24,
          passwordMinLength: 8,
          twoFactorRequired: false,
          ipWhitelist: [],
          rateLimitRequests: 100,
          rateLimitWindow: 60
        },
        billing: {
          stripeEnabled: true,
          paypalEnabled: false,
          creditCardRequired: true,
          freeCredits: 100,
          premiumPrice: 29.99,
          currency: 'USD'
        },
        api: {
          maxRequestsPerMinute: 1000,
          maxRequestsPerHour: 10000,
          apiKeyExpiration: 365,
          webhookRetries: 3
        },
        notifications: {
          emailEnabled: true,
          smtpHost: 'smtp.gmail.com',
          smtpPort: 587,
          smtpUser: '',
          smtpPassword: ''
        }
      }

      setSettings(mockSettings)
    } catch (error) {
      console.error('Failed to load settings:', error)
      toast.error('Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  const updateSetting = (category: keyof SystemSettings, key: string, value: any) => {
    if (!settings) return

    setSettings({
      ...settings,
      [category]: {
        ...settings[category],
        [key]: value
      }
    })
    setHasChanges(true)
  }

  const saveSettings = async () => {
    if (!settings) return

    setSaving(true)
    try {
      // In production, this would save to your backend
      await new Promise(resolve => setTimeout(resolve, 1000)) // Mock delay
      setHasChanges(false)
      toast.success('Settings saved successfully!')
    } catch (error) {
      console.error('Failed to save settings:', error)
      toast.error('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  const resetSettings = () => {
    loadSettings()
    setHasChanges(false)
    toast.success('Settings reset to last saved state')
  }

  if (loading || !settings) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Settings className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-muted-foreground">Loading admin settings...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Admin Settings</h1>
          <p className="text-muted-foreground">
            Configure system-wide settings and preferences
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={resetSettings} disabled={!hasChanges}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button onClick={saveSettings} disabled={!hasChanges || saving}>
            {saving ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      <Tabs defaultValue="general" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="billing">Billing</TabsTrigger>
          <TabsTrigger value="api">API</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
        </TabsList>

        {/* General Settings */}
        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>General Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="siteName">Site Name</Label>
                  <Input
                    id="siteName"
                    value={settings.general.siteName}
                    onChange={(e) => updateSetting('general', 'siteName', e.target.value)}
                  />
                </div>

                <div>
                  <Label htmlFor="contactEmail">Contact Email</Label>
                  <Input
                    id="contactEmail"
                    type="email"
                    value={settings.general.contactEmail}
                    onChange={(e) => updateSetting('general', 'contactEmail', e.target.value)}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="siteDescription">Site Description</Label>
                <Textarea
                  id="siteDescription"
                  value={settings.general.siteDescription}
                  onChange={(e) => updateSetting('general', 'siteDescription', e.target.value)}
                  rows={3}
                />
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Maintenance Mode</Label>
                    <p className="text-sm text-muted-foreground">
                      Put the site in maintenance mode for updates
                    </p>
                  </div>
                  <Switch
                    checked={settings.general.maintenanceMode}
                    onCheckedChange={(checked) => updateSetting('general', 'maintenanceMode', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>User Registration</Label>
                    <p className="text-sm text-muted-foreground">
                      Allow new users to create accounts
                    </p>
                  </div>
                  <Switch
                    checked={settings.general.registrationEnabled}
                    onCheckedChange={(checked) => updateSetting('general', 'registrationEnabled', checked)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Settings */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Security Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="sessionTimeout">Session Timeout (hours)</Label>
                  <Input
                    id="sessionTimeout"
                    type="number"
                    value={settings.security.sessionTimeout}
                    onChange={(e) => updateSetting('security', 'sessionTimeout', parseInt(e.target.value))}
                  />
                </div>

                <div>
                  <Label htmlFor="passwordMinLength">Minimum Password Length</Label>
                  <Input
                    id="passwordMinLength"
                    type="number"
                    value={settings.security.passwordMinLength}
                    onChange={(e) => updateSetting('security', 'passwordMinLength', parseInt(e.target.value))}
                  />
                </div>

                <div>
                  <Label htmlFor="rateLimitRequests">Rate Limit Requests</Label>
                  <Input
                    id="rateLimitRequests"
                    type="number"
                    value={settings.security.rateLimitRequests}
                    onChange={(e) => updateSetting('security', 'rateLimitRequests', parseInt(e.target.value))}
                  />
                </div>

                <div>
                  <Label htmlFor="rateLimitWindow">Rate Limit Window (minutes)</Label>
                  <Input
                    id="rateLimitWindow"
                    type="number"
                    value={settings.security.rateLimitWindow}
                    onChange={(e) => updateSetting('security', 'rateLimitWindow', parseInt(e.target.value))}
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Two-Factor Authentication Required</Label>
                    <p className="text-sm text-muted-foreground">
                      Force all users to enable 2FA
                    </p>
                  </div>
                  <Switch
                    checked={settings.security.twoFactorRequired}
                    onCheckedChange={(checked) => updateSetting('security', 'twoFactorRequired', checked)}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="ipWhitelist">IP Whitelist (one per line)</Label>
                <Textarea
                  id="ipWhitelist"
                  placeholder="192.168.1.1&#10;10.0.0.1"
                  value={settings.security.ipWhitelist.join('\n')}
                  onChange={(e) => updateSetting('security', 'ipWhitelist', e.target.value.split('\n').filter(ip => ip.trim()))}
                  rows={4}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Billing Settings */}
        <TabsContent value="billing" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                Billing Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="freeCredits">Free Credits</Label>
                  <Input
                    id="freeCredits"
                    type="number"
                    value={settings.billing.freeCredits}
                    onChange={(e) => updateSetting('billing', 'freeCredits', parseInt(e.target.value))}
                  />
                </div>

                <div>
                  <Label htmlFor="premiumPrice">Premium Price</Label>
                  <Input
                    id="premiumPrice"
                    type="number"
                    step="0.01"
                    value={settings.billing.premiumPrice}
                    onChange={(e) => updateSetting('billing', 'premiumPrice', parseFloat(e.target.value))}
                  />
                </div>

                <div>
                  <Label htmlFor="currency">Currency</Label>
                  <select
                    id="currency"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    value={settings.billing.currency}
                    onChange={(e) => updateSetting('billing', 'currency', e.target.value)}
                  >
                    <option value="USD">USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                  </select>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Stripe Payment Gateway</Label>
                    <p className="text-sm text-muted-foreground">
                      Enable Stripe for credit card payments
                    </p>
                  </div>
                  <Switch
                    checked={settings.billing.stripeEnabled}
                    onCheckedChange={(checked) => updateSetting('billing', 'stripeEnabled', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>PayPal Payment Gateway</Label>
                    <p className="text-sm text-muted-foreground">
                      Enable PayPal for alternative payments
                    </p>
                  </div>
                  <Switch
                    checked={settings.billing.paypalEnabled}
                    onCheckedChange={(checked) => updateSetting('billing', 'paypalEnabled', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Credit Card Required</Label>
                    <p className="text-sm text-muted-foreground">
                      Require credit card for premium subscriptions
                    </p>
                  </div>
                  <Switch
                    checked={settings.billing.creditCardRequired}
                    onCheckedChange={(checked) => updateSetting('billing', 'creditCardRequired', checked)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Settings */}
        <TabsContent value="api" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                API Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="maxRequestsPerMinute">Max Requests/Minute</Label>
                  <Input
                    id="maxRequestsPerMinute"
                    type="number"
                    value={settings.api.maxRequestsPerMinute}
                    onChange={(e) => updateSetting('api', 'maxRequestsPerMinute', parseInt(e.target.value))}
                  />
                </div>

                <div>
                  <Label htmlFor="maxRequestsPerHour">Max Requests/Hour</Label>
                  <Input
                    id="maxRequestsPerHour"
                    type="number"
                    value={settings.api.maxRequestsPerHour}
                    onChange={(e) => updateSetting('api', 'maxRequestsPerHour', parseInt(e.target.value))}
                  />
                </div>

                <div>
                  <Label htmlFor="apiKeyExpiration">API Key Expiration (days)</Label>
                  <Input
                    id="apiKeyExpiration"
                    type="number"
                    value={settings.api.apiKeyExpiration}
                    onChange={(e) => updateSetting('api', 'apiKeyExpiration', parseInt(e.target.value))}
                  />
                </div>

                <div>
                  <Label htmlFor="webhookRetries">Webhook Retry Attempts</Label>
                  <Input
                    id="webhookRetries"
                    type="number"
                    value={settings.api.webhookRetries}
                    onChange={(e) => updateSetting('api', 'webhookRetries', parseInt(e.target.value))}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notification Settings */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Email Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Email Notifications Enabled</Label>
                  <p className="text-sm text-muted-foreground">
                    Send automated email notifications
                  </p>
                </div>
                <Switch
                  checked={settings.notifications.emailEnabled}
                  onCheckedChange={(checked) => updateSetting('notifications', 'emailEnabled', checked)}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="smtpHost">SMTP Host</Label>
                  <Input
                    id="smtpHost"
                    value={settings.notifications.smtpHost}
                    onChange={(e) => updateSetting('notifications', 'smtpHost', e.target.value)}
                    placeholder="smtp.gmail.com"
                  />
                </div>

                <div>
                  <Label htmlFor="smtpPort">SMTP Port</Label>
                  <Input
                    id="smtpPort"
                    type="number"
                    value={settings.notifications.smtpPort}
                    onChange={(e) => updateSetting('notifications', 'smtpPort', parseInt(e.target.value))}
                    placeholder="587"
                  />
                </div>

                <div>
                  <Label htmlFor="smtpUser">SMTP Username</Label>
                  <Input
                    id="smtpUser"
                    value={settings.notifications.smtpUser}
                    onChange={(e) => updateSetting('notifications', 'smtpUser', e.target.value)}
                    placeholder="your-email@gmail.com"
                  />
                </div>

                <div>
                  <Label htmlFor="smtpPassword">SMTP Password</Label>
                  <Input
                    id="smtpPassword"
                    type="password"
                    value={settings.notifications.smtpPassword}
                    onChange={(e) => updateSetting('notifications', 'smtpPassword', e.target.value)}
                    placeholder="App password or SMTP password"
                  />
                </div>
              </div>

              <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                  SMTP Configuration Notes
                </h4>
                <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                  <li>• For Gmail, use app passwords instead of your main password</li>
                  <li>• Port 587 is for TLS, 465 for SSL, 25 for non-encrypted</li>
                  <li>• Test your configuration before saving</li>
                  <li>• Consider using dedicated email services for production</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
