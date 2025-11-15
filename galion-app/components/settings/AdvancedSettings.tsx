'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Settings,
  Palette,
  Eye,
  Shield,
  Bell,
  Volume2,
  Moon,
  Sun,
  Monitor,
  Accessibility,
  Globe,
  Lock,
  User,
  Save,
  RotateCcw,
  Download,
  Upload
} from 'lucide-react'
import toast from 'react-hot-toast'

interface AdvancedSettings {
  theme: {
    mode: 'light' | 'dark' | 'system'
    accentColor: string
    fontSize: number
    highContrast: boolean
  }
  accessibility: {
    reducedMotion: boolean
    screenReader: boolean
    keyboardNavigation: boolean
    focusIndicators: boolean
    textToSpeech: boolean
    speechRate: number
  }
  privacy: {
    dataCollection: boolean
    analytics: boolean
    crashReports: boolean
    personalization: boolean
    thirdPartySharing: boolean
  }
  notifications: {
    email: boolean
    push: boolean
    sound: boolean
    desktop: boolean
    quietHours: {
      enabled: boolean
      start: string
      end: string
    }
  }
  language: {
    interface: string
    voice: string
    timezone: string
    dateFormat: string
    numberFormat: string
  }
  performance: {
    preloadContent: boolean
    imageQuality: 'low' | 'medium' | 'high'
    cacheSize: number
    backgroundSync: boolean
  }
}

interface AdvancedSettingsProps {
  onSettingsChange?: (settings: AdvancedSettings) => void
  className?: string
}

const THEME_PRESETS = [
  { name: 'Default Blue', color: '#3b82f6', preview: 'bg-blue-500' },
  { name: 'Forest Green', color: '#10b981', preview: 'bg-green-500' },
  { name: 'Royal Purple', color: '#8b5cf6', preview: 'bg-purple-500' },
  { name: 'Sunset Orange', color: '#f97316', preview: 'bg-orange-500' },
  { name: 'Ocean Teal', color: '#14b8a6', preview: 'bg-teal-500' },
  { name: 'Rose Pink', color: '#ec4899', preview: 'bg-pink-500' }
]

export const AdvancedSettings: React.FC<AdvancedSettingsProps> = ({
  onSettingsChange,
  className
}) => {
  const [settings, setSettings] = useState<AdvancedSettings>({
    theme: {
      mode: 'system',
      accentColor: '#3b82f6',
      fontSize: 16,
      highContrast: false
    },
    accessibility: {
      reducedMotion: false,
      screenReader: false,
      keyboardNavigation: true,
      focusIndicators: true,
      textToSpeech: false,
      speechRate: 1.0
    },
    privacy: {
      dataCollection: true,
      analytics: true,
      crashReports: true,
      personalization: true,
      thirdPartySharing: false
    },
    notifications: {
      email: true,
      push: true,
      sound: true,
      desktop: true,
      quietHours: {
        enabled: false,
        start: '22:00',
        end: '08:00'
      }
    },
    language: {
      interface: 'en',
      voice: 'en-US',
      timezone: 'America/New_York',
      dateFormat: 'MM/DD/YYYY',
      numberFormat: 'en-US'
    },
    performance: {
      preloadContent: true,
      imageQuality: 'high',
      cacheSize: 100,
      backgroundSync: true
    }
  })

  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  useEffect(() => {
    // Load saved settings
    loadSavedSettings()
  }, [])

  const loadSavedSettings = async () => {
    try {
      const saved = localStorage.getItem('galion-advanced-settings')
      if (saved) {
        const parsed = JSON.parse(saved)
        setSettings(parsed)
      }
    } catch (error) {
      console.error('Failed to load advanced settings:', error)
    }
  }

  const updateSetting = (category: keyof AdvancedSettings, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }))
    setHasUnsavedChanges(true)
  }

  const updateNestedSetting = (category: keyof AdvancedSettings, nestedKey: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [nestedKey]: {
          ...(prev[category] as any)[nestedKey],
          [key]: value
        }
      }
    }))
    setHasUnsavedChanges(true)
  }

  const saveSettings = async () => {
    try {
      localStorage.setItem('galion-advanced-settings', JSON.stringify(settings))
      onSettingsChange?.(settings)
      setHasUnsavedChanges(false)
      toast.success('Advanced settings saved!')
    } catch (error) {
      console.error('Failed to save settings:', error)
      toast.error('Failed to save settings')
    }
  }

  const resetToDefaults = () => {
    const defaultSettings: AdvancedSettings = {
      theme: {
        mode: 'system',
        accentColor: '#3b82f6',
        fontSize: 16,
        highContrast: false
      },
      accessibility: {
        reducedMotion: false,
        screenReader: false,
        keyboardNavigation: true,
        focusIndicators: true,
        textToSpeech: false,
        speechRate: 1.0
      },
      privacy: {
        dataCollection: true,
        analytics: true,
        crashReports: true,
        personalization: true,
        thirdPartySharing: false
      },
      notifications: {
        email: true,
        push: true,
        sound: true,
        desktop: true,
        quietHours: {
          enabled: false,
          start: '22:00',
          end: '08:00'
        }
      },
      language: {
        interface: 'en',
        voice: 'en-US',
        timezone: 'America/New_York',
        dateFormat: 'MM/DD/YYYY',
        numberFormat: 'en-US'
      },
      performance: {
        preloadContent: true,
        imageQuality: 'high',
        cacheSize: 100,
        backgroundSync: true
      }
    }

    setSettings(defaultSettings)
    setHasUnsavedChanges(true)
    toast.success('Settings reset to defaults')
  }

  const exportSettings = () => {
    const dataStr = JSON.stringify(settings, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)

    const exportFileDefaultName = 'galion-settings.json'

    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()

    toast.success('Settings exported!')
  }

  const importSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const importedSettings = JSON.parse(e.target?.result as string)
          setSettings(importedSettings)
          setHasUnsavedChanges(true)
          toast.success('Settings imported successfully!')
        } catch (error) {
          toast.error('Invalid settings file')
        }
      }
      reader.readAsText(file)
    }
  }

  return (
    <div className={className}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold">Advanced Settings</h3>
          <p className="text-sm text-muted-foreground">
            Customize your experience with detailed preferences
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={exportSettings}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <label>
            <Button variant="outline" size="sm" asChild>
              <span>
                <Upload className="h-4 w-4 mr-2" />
                Import
              </span>
            </Button>
            <input
              type="file"
              accept=".json"
              onChange={importSettings}
              className="hidden"
            />
          </label>
          <Button variant="outline" size="sm" onClick={resetToDefaults}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button size="sm" onClick={saveSettings} disabled={!hasUnsavedChanges}>
            <Save className="h-4 w-4 mr-2" />
            Save
          </Button>
        </div>
      </div>

      <Tabs defaultValue="theme" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="theme">Theme</TabsTrigger>
          <TabsTrigger value="accessibility">Accessibility</TabsTrigger>
          <TabsTrigger value="privacy">Privacy</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="language">Language</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        {/* Theme Settings */}
        <TabsContent value="theme" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Appearance
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label className="text-base font-medium mb-3 block">Theme Mode</Label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: 'light', label: 'Light', icon: Sun },
                    { value: 'dark', label: 'Dark', icon: Moon },
                    { value: 'system', label: 'System', icon: Monitor }
                  ].map(({ value, label, icon: Icon }) => (
                    <button
                      key={value}
                      onClick={() => updateSetting('theme', 'mode', value)}
                      className={`p-4 border rounded-lg text-center transition-all ${
                        settings.theme.mode === value
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <Icon className="h-6 w-6 mx-auto mb-2" />
                      <div className="text-sm font-medium">{label}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-base font-medium mb-3 block">Accent Color</Label>
                <div className="grid grid-cols-3 gap-3 mb-4">
                  {THEME_PRESETS.map((preset) => (
                    <button
                      key={preset.color}
                      onClick={() => updateSetting('theme', 'accentColor', preset.color)}
                      className={`p-3 border rounded-lg text-center transition-all ${
                        settings.theme.accentColor === preset.color
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-full mx-auto mb-2 ${preset.preview}`} />
                      <div className="text-sm font-medium">{preset.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-base font-medium mb-3 block">Font Size</Label>
                <div className="space-y-3">
                  <Slider
                    value={[settings.theme.fontSize]}
                    onValueChange={([value]) => updateSetting('theme', 'fontSize', value)}
                    min={12}
                    max={24}
                    step={1}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Small (12px)</span>
                    <span className="font-medium">{settings.theme.fontSize}px</span>
                    <span>Large (24px)</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>High Contrast Mode</Label>
                  <p className="text-sm text-muted-foreground">
                    Increase contrast for better visibility
                  </p>
                </div>
                <Switch
                  checked={settings.theme.highContrast}
                  onCheckedChange={(checked) => updateSetting('theme', 'highContrast', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Accessibility Settings */}
        <TabsContent value="accessibility" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Accessibility className="h-5 w-5" />
                Accessibility
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Reduced Motion</Label>
                    <p className="text-sm text-muted-foreground">
                      Minimize animations and transitions
                    </p>
                  </div>
                  <Switch
                    checked={settings.accessibility.reducedMotion}
                    onCheckedChange={(checked) => updateSetting('accessibility', 'reducedMotion', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Screen Reader Support</Label>
                    <p className="text-sm text-muted-foreground">
                      Optimize interface for screen readers
                    </p>
                  </div>
                  <Switch
                    checked={settings.accessibility.screenReader}
                    onCheckedChange={(checked) => updateSetting('accessibility', 'screenReader', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Keyboard Navigation</Label>
                    <p className="text-sm text-muted-foreground">
                      Enable full keyboard navigation
                    </p>
                  </div>
                  <Switch
                    checked={settings.accessibility.keyboardNavigation}
                    onCheckedChange={(checked) => updateSetting('accessibility', 'keyboardNavigation', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Focus Indicators</Label>
                    <p className="text-sm text-muted-foreground">
                      Show focus rings on interactive elements
                    </p>
                  </div>
                  <Switch
                    checked={settings.accessibility.focusIndicators}
                    onCheckedChange={(checked) => updateSetting('accessibility', 'focusIndicators', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Text-to-Speech</Label>
                    <p className="text-sm text-muted-foreground">
                      Enable voice output for interface elements
                    </p>
                  </div>
                  <Switch
                    checked={settings.accessibility.textToSpeech}
                    onCheckedChange={(checked) => updateSetting('accessibility', 'textToSpeech', checked)}
                  />
                </div>

                {settings.accessibility.textToSpeech && (
                  <div>
                    <Label className="text-base font-medium mb-3 block">Speech Rate</Label>
                    <div className="space-y-3">
                      <Slider
                        value={[settings.accessibility.speechRate]}
                        onValueChange={([value]) => updateSetting('accessibility', 'speechRate', value)}
                        min={0.5}
                        max={2.0}
                        step={0.1}
                        className="w-full"
                      />
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>Slow (0.5x)</span>
                        <span className="font-medium">{settings.accessibility.speechRate}x</span>
                        <span>Fast (2.0x)</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Privacy Settings */}
        <TabsContent value="privacy" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Privacy & Data
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Data Collection</Label>
                    <p className="text-sm text-muted-foreground">
                      Allow collection of usage data to improve the service
                    </p>
                  </div>
                  <Switch
                    checked={settings.privacy.dataCollection}
                    onCheckedChange={(checked) => updateSetting('privacy', 'dataCollection', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Analytics Tracking</Label>
                    <p className="text-sm text-muted-foreground">
                      Help us understand how you use the platform
                    </p>
                  </div>
                  <Switch
                    checked={settings.privacy.analytics}
                    onCheckedChange={(checked) => updateSetting('privacy', 'analytics', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Crash Reports</Label>
                    <p className="text-sm text-muted-foreground">
                      Send anonymous crash reports to help fix issues
                    </p>
                  </div>
                  <Switch
                    checked={settings.privacy.crashReports}
                    onCheckedChange={(checked) => updateSetting('privacy', 'crashReports', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Personalization</Label>
                    <p className="text-sm text-muted-foreground">
                      Customize content based on your preferences
                    </p>
                  </div>
                  <Switch
                    checked={settings.privacy.personalization}
                    onCheckedChange={(checked) => updateSetting('privacy', 'personalization', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Third-Party Sharing</Label>
                    <p className="text-sm text-muted-foreground">
                      Share anonymized data with partners
                    </p>
                  </div>
                  <Switch
                    checked={settings.privacy.thirdPartySharing}
                    onCheckedChange={(checked) => updateSetting('privacy', 'thirdPartySharing', checked)}
                  />
                </div>
              </div>

              <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                  Privacy Information
                </h4>
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  Your privacy is important to us. You can control what data we collect and how it's used.
                  Changes to privacy settings may take effect after your next session.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Settings */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notifications
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive updates and alerts via email
                    </p>
                  </div>
                  <Switch
                    checked={settings.notifications.email}
                    onCheckedChange={(checked) => updateSetting('notifications', 'email', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Push Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive push notifications in your browser
                    </p>
                  </div>
                  <Switch
                    checked={settings.notifications.push}
                    onCheckedChange={(checked) => updateSetting('notifications', 'push', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Sound Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Play sounds for notifications
                    </p>
                  </div>
                  <Switch
                    checked={settings.notifications.sound}
                    onCheckedChange={(checked) => updateSetting('notifications', 'sound', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Desktop Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Show notifications on your desktop
                    </p>
                  </div>
                  <Switch
                    checked={settings.notifications.desktop}
                    onCheckedChange={(checked) => updateSetting('notifications', 'desktop', checked)}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Quiet Hours</Label>
                      <p className="text-sm text-muted-foreground">
                        Disable notifications during specified hours
                      </p>
                    </div>
                    <Switch
                      checked={settings.notifications.quietHours.enabled}
                      onCheckedChange={(enabled) => updateNestedSetting('notifications', 'quietHours', 'enabled', enabled)}
                    />
                  </div>

                  {settings.notifications.quietHours.enabled && (
                    <div className="grid grid-cols-2 gap-3 ml-6">
                      <div>
                        <Label htmlFor="quiet-start">Start Time</Label>
                        <Input
                          id="quiet-start"
                          type="time"
                          value={settings.notifications.quietHours.start}
                          onChange={(e) => updateNestedSetting('notifications', 'quietHours', 'start', e.target.value)}
                        />
                      </div>
                      <div>
                        <Label htmlFor="quiet-end">End Time</Label>
                        <Input
                          id="quiet-end"
                          type="time"
                          value={settings.notifications.quietHours.end}
                          onChange={(e) => updateNestedSetting('notifications', 'quietHours', 'end', e.target.value)}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Language Settings */}
        <TabsContent value="language" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Language & Region
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="interface-lang">Interface Language</Label>
                  <Select
                    value={settings.language.interface}
                    onValueChange={(value) => updateSetting('language', 'interface', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Español</SelectItem>
                      <SelectItem value="fr">Français</SelectItem>
                      <SelectItem value="de">Deutsch</SelectItem>
                      <SelectItem value="it">Italiano</SelectItem>
                      <SelectItem value="pt">Português</SelectItem>
                      <SelectItem value="ru">Русский</SelectItem>
                      <SelectItem value="ja">日本語</SelectItem>
                      <SelectItem value="ko">한국어</SelectItem>
                      <SelectItem value="zh">中文</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="voice-lang">Voice Language</Label>
                  <Select
                    value={settings.language.voice}
                    onValueChange={(value) => updateSetting('language', 'voice', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en-US">English (US)</SelectItem>
                      <SelectItem value="en-GB">English (UK)</SelectItem>
                      <SelectItem value="es-ES">Español (Spain)</SelectItem>
                      <SelectItem value="fr-FR">Français (France)</SelectItem>
                      <SelectItem value="de-DE">Deutsch (Germany)</SelectItem>
                      <SelectItem value="it-IT">Italiano (Italy)</SelectItem>
                      <SelectItem value="pt-BR">Português (Brazil)</SelectItem>
                      <SelectItem value="ru-RU">Русский (Russia)</SelectItem>
                      <SelectItem value="ja-JP">日本語 (Japan)</SelectItem>
                      <SelectItem value="ko-KR">한국어 (Korea)</SelectItem>
                      <SelectItem value="zh-CN">中文 (China)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select
                    value={settings.language.timezone}
                    onValueChange={(value) => updateSetting('language', 'timezone', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="America/New_York">Eastern Time</SelectItem>
                      <SelectItem value="America/Chicago">Central Time</SelectItem>
                      <SelectItem value="America/Denver">Mountain Time</SelectItem>
                      <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                      <SelectItem value="Europe/London">London</SelectItem>
                      <SelectItem value="Europe/Paris">Paris</SelectItem>
                      <SelectItem value="Europe/Berlin">Berlin</SelectItem>
                      <SelectItem value="Asia/Tokyo">Tokyo</SelectItem>
                      <SelectItem value="Asia/Shanghai">Shanghai</SelectItem>
                      <SelectItem value="Australia/Sydney">Sydney</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="date-format">Date Format</Label>
                  <Select
                    value={settings.language.dateFormat}
                    onValueChange={(value) => updateSetting('language', 'dateFormat', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                      <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                      <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Settings */}
        <TabsContent value="performance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Performance
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Preload Content</Label>
                    <p className="text-sm text-muted-foreground">
                      Load content in advance for faster navigation
                    </p>
                  </div>
                  <Switch
                    checked={settings.performance.preloadContent}
                    onCheckedChange={(checked) => updateSetting('performance', 'preloadContent', checked)}
                  />
                </div>

                <div>
                  <Label className="text-base font-medium mb-3 block">Image Quality</Label>
                  <Select
                    value={settings.performance.imageQuality}
                    onValueChange={(value: 'low' | 'medium' | 'high') => updateSetting('performance', 'imageQuality', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low (Faster)</SelectItem>
                      <SelectItem value="medium">Medium (Balanced)</SelectItem>
                      <SelectItem value="high">High (Best Quality)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-base font-medium mb-3 block">Cache Size (MB)</Label>
                  <div className="space-y-3">
                    <Slider
                      value={[settings.performance.cacheSize]}
                      onValueChange={([value]) => updateSetting('performance', 'cacheSize', value)}
                      min={10}
                      max={500}
                      step={10}
                      className="w-full"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground">
                      <span>10 MB</span>
                      <span className="font-medium">{settings.performance.cacheSize} MB</span>
                      <span>500 MB</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Background Sync</Label>
                    <p className="text-sm text-muted-foreground">
                      Sync data in the background when offline
                    </p>
                  </div>
                  <Switch
                    checked={settings.performance.backgroundSync}
                    onCheckedChange={(checked) => updateSetting('performance', 'backgroundSync', checked)}
                  />
                </div>
              </div>

              <div className="p-4 bg-green-50 dark:bg-green-950/20 rounded-lg">
                <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">
                  Performance Tips
                </h4>
                <ul className="text-sm text-green-800 dark:text-green-200 space-y-1">
                  <li>• Lower image quality and cache size for slower connections</li>
                  <li>• Enable preload content for stable internet connections</li>
                  <li>• Background sync helps keep your data current</li>
                  <li>• Clear cache regularly to free up storage space</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
