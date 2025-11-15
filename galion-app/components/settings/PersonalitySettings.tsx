'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Brain,
  Sparkles,
  Target,
  Heart,
  Zap,
  Shield,
  Palette,
  Users,
  Save,
  RotateCcw,
  Eye,
  MessageSquare,
  Lightbulb
} from 'lucide-react'
import toast from 'react-hot-toast'

interface PersonalityTraits {
  // Core Traits
  creativity: number
  analytical: number
  practicality: number
  friendliness: number

  // Advanced Traits
  curiosity: number
  confidence: number
  patience: number
  adaptability: number

  // Interaction Style
  directness: number
  humor: number
  empathy: number
  thoroughness: number

  // Domain Expertise
  technical: number
  creative_writing: number
  problem_solving: number
  teaching: number
}

interface PersonalityProfile {
  id: string
  name: string
  description: string
  icon: string
  traits: Partial<PersonalityTraits>
  category: 'professional' | 'creative' | 'educational' | 'casual' | 'custom'
}

const PRESET_PROFILES: PersonalityProfile[] = [
  {
    id: 'professional',
    name: 'Professional Assistant',
    description: 'Business-focused, efficient, and reliable',
    icon: '💼',
    category: 'professional',
    traits: {
      analytical: 0.9,
      practicality: 0.95,
      confidence: 0.9,
      directness: 0.8,
      thoroughness: 0.9,
      technical: 0.8,
      problem_solving: 0.9
    }
  },
  {
    id: 'creative',
    name: 'Creative Partner',
    description: 'Imaginative, artistic, and inspirational',
    icon: '🎨',
    category: 'creative',
    traits: {
      creativity: 0.95,
      curiosity: 0.9,
      empathy: 0.8,
      humor: 0.7,
      adaptability: 0.8,
      creative_writing: 0.9
    }
  },
  {
    id: 'educator',
    name: 'Patient Teacher',
    description: 'Helpful, explanatory, and encouraging',
    icon: '📚',
    category: 'educational',
    traits: {
      patience: 0.95,
      teaching: 0.9,
      empathy: 0.9,
      thoroughness: 0.8,
      friendliness: 0.85,
      directness: 0.6
    }
  },
  {
    id: 'casual',
    name: 'Friendly Companion',
    description: 'Conversational, fun, and approachable',
    icon: '😊',
    category: 'casual',
    traits: {
      friendliness: 0.95,
      humor: 0.8,
      empathy: 0.85,
      directness: 0.7,
      adaptability: 0.8,
      curiosity: 0.75
    }
  },
  {
    id: 'technical',
    name: 'Code Expert',
    description: 'Precise, technical, and detail-oriented',
    icon: '💻',
    category: 'professional',
    traits: {
      analytical: 0.95,
      technical: 0.95,
      thoroughness: 0.9,
      practicality: 0.85,
      problem_solving: 0.9,
      directness: 0.8
    }
  }
]

interface PersonalitySettingsProps {
  onPersonalityChange?: (traits: PersonalityTraits) => void
  className?: string
}

export const PersonalitySettings: React.FC<PersonalitySettingsProps> = ({
  onPersonalityChange,
  className
}) => {
  const [currentTraits, setCurrentTraits] = useState<PersonalityTraits>({
    creativity: 0.7,
    analytical: 0.7,
    practicality: 0.7,
    friendliness: 0.7,
    curiosity: 0.7,
    confidence: 0.7,
    patience: 0.7,
    adaptability: 0.7,
    directness: 0.7,
    humor: 0.7,
    empathy: 0.7,
    thoroughness: 0.7,
    technical: 0.7,
    creative_writing: 0.7,
    problem_solving: 0.7,
    teaching: 0.7
  })

  const [selectedPreset, setSelectedPreset] = useState<string | null>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  useEffect(() => {
    // Load saved personality settings
    loadPersonalitySettings()
  }, [])

  const loadPersonalitySettings = async () => {
    try {
      // In a real app, this would load from your backend
      const saved = localStorage.getItem('galion-personality')
      if (saved) {
        const parsed = JSON.parse(saved)
        setCurrentTraits(parsed)
      }
    } catch (error) {
      console.error('Failed to load personality settings:', error)
    }
  }

  const savePersonalitySettings = async () => {
    try {
      localStorage.setItem('galion-personality', JSON.stringify(currentTraits))
      onPersonalityChange?.(currentTraits)
      setHasUnsavedChanges(false)
      toast.success('Personality settings saved!')
    } catch (error) {
      console.error('Failed to save personality settings:', error)
      toast.error('Failed to save settings')
    }
  }

  const updateTrait = (trait: keyof PersonalityTraits, value: number) => {
    setCurrentTraits(prev => ({ ...prev, [trait]: value }))
    setSelectedPreset(null) // Clear preset selection when manually adjusting
    setHasUnsavedChanges(true)
  }

  const applyPreset = (preset: PersonalityProfile) => {
    const newTraits = { ...currentTraits, ...preset.traits }
    setCurrentTraits(newTraits)
    setSelectedPreset(preset.id)
    setHasUnsavedChanges(true)
    toast.success(`Applied ${preset.name} personality`)
  }

  const resetToDefaults = () => {
    const defaults = Object.keys(currentTraits).reduce((acc, key) => {
      acc[key as keyof PersonalityTraits] = 0.7
      return acc
    }, {} as PersonalityTraits)

    setCurrentTraits(defaults)
    setSelectedPreset(null)
    setHasUnsavedChanges(true)
    toast.success('Reset to default personality')
  }

  const getTraitDescription = (trait: keyof PersonalityTraits, value: number): string => {
    const descriptions = {
      creativity: value > 0.8 ? 'Highly creative and imaginative' :
                  value > 0.6 ? 'Moderately creative' :
                  'Practical and conventional',
      analytical: value > 0.8 ? 'Highly analytical and logical' :
                 value > 0.6 ? 'Balanced analytical approach' :
                 'Intuitive and holistic',
      practicality: value > 0.8 ? 'Highly practical and efficient' :
                   value > 0.6 ? 'Balanced practical approach' :
                   'Idealistic and theoretical',
      friendliness: value > 0.8 ? 'Very friendly and approachable' :
                   value > 0.6 ? 'Generally friendly' :
                   'More reserved and professional',
      curiosity: value > 0.8 ? 'Highly curious and exploratory' :
                value > 0.6 ? 'Moderately curious' :
                'Focused and task-oriented',
      confidence: value > 0.8 ? 'Very confident and assertive' :
                 value > 0.6 ? 'Generally confident' :
                 'More cautious and thoughtful',
      patience: value > 0.8 ? 'Very patient and thorough' :
               value > 0.6 ? 'Generally patient' :
               'More direct and efficient',
      adaptability: value > 0.8 ? 'Highly adaptable and flexible' :
                   value > 0.6 ? 'Moderately adaptable' :
                   'Prefer structure and routine',
      directness: value > 0.8 ? 'Very direct and straightforward' :
                 value > 0.6 ? 'Generally direct' :
                 'More diplomatic and nuanced',
      humor: value > 0.8 ? 'Very humorous and playful' :
             value > 0.6 ? 'Occasionally humorous' :
             'More serious and professional',
      empathy: value > 0.8 ? 'Highly empathetic and understanding' :
              value > 0.6 ? 'Generally empathetic' :
              'More logical and objective',
      thoroughness: value > 0.8 ? 'Very thorough and detailed' :
                   value > 0.6 ? 'Generally thorough' :
                   'More high-level and strategic',
      technical: value > 0.8 ? 'Highly technical and precise' :
                value > 0.6 ? 'Moderately technical' :
                'More user-friendly and accessible',
      creative_writing: value > 0.8 ? 'Excellent creative writing skills' :
                       value > 0.6 ? 'Good creative writing' :
                       'More functional writing style',
      problem_solving: value > 0.8 ? 'Expert problem solver' :
                      value > 0.6 ? 'Good problem solver' :
                      'More supportive role',
      teaching: value > 0.8 ? 'Excellent teacher and explainer' :
               value > 0.6 ? 'Good at teaching' :
               'More hands-off guidance'
    }

    return descriptions[trait] || 'Balanced approach'
  }

  const traitCategories = {
    core: [
      { key: 'creativity' as keyof PersonalityTraits, label: 'Creativity', icon: Sparkles },
      { key: 'analytical' as keyof PersonalityTraits, label: 'Analytical', icon: Brain },
      { key: 'practicality' as keyof PersonalityTraits, label: 'Practicality', icon: Target },
      { key: 'friendliness' as keyof PersonalityTraits, label: 'Friendliness', icon: Heart }
    ],
    advanced: [
      { key: 'curiosity' as keyof PersonalityTraits, label: 'Curiosity', icon: Lightbulb },
      { key: 'confidence' as keyof PersonalityTraits, label: 'Confidence', icon: Zap },
      { key: 'patience' as keyof PersonalityTraits, label: 'Patience', icon: Users },
      { key: 'adaptability' as keyof PersonalityTraits, label: 'Adaptability', icon: Shield }
    ],
    interaction: [
      { key: 'directness' as keyof PersonalityTraits, label: 'Directness', icon: MessageSquare },
      { key: 'humor' as keyof PersonalityTraits, label: 'Humor', icon: Palette },
      { key: 'empathy' as keyof PersonalityTraits, label: 'Empathy', icon: Heart },
      { key: 'thoroughness' as keyof PersonalityTraits, label: 'Thoroughness', icon: Eye }
    ],
    expertise: [
      { key: 'technical' as keyof PersonalityTraits, label: 'Technical', icon: Brain },
      { key: 'creative_writing' as keyof PersonalityTraits, label: 'Creative Writing', icon: Sparkles },
      { key: 'problem_solving' as keyof PersonalityTraits, label: 'Problem Solving', icon: Target },
      { key: 'teaching' as keyof PersonalityTraits, label: 'Teaching', icon: Users }
    ]
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">AI Personality Settings</h2>
          <p className="text-muted-foreground">
            Customize how the AI behaves and responds to you
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={resetToDefaults}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button
            onClick={savePersonalitySettings}
            disabled={!hasUnsavedChanges}
          >
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>

      {/* Preset Profiles */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Presets</CardTitle>
          <p className="text-sm text-muted-foreground">
            Choose from pre-configured personality profiles
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {PRESET_PROFILES.map((preset) => (
              <motion.div
                key={preset.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  className={cn(
                    'cursor-pointer transition-all hover:shadow-md',
                    selectedPreset === preset.id && 'ring-2 ring-blue-500'
                  )}
                  onClick={() => applyPreset(preset)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-2xl">{preset.icon}</span>
                      <div>
                        <h4 className="font-semibold">{preset.name}</h4>
                        <Badge variant="outline" className="text-xs">
                          {preset.category}
                        </Badge>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {preset.description}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Custom Personality Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Custom Personality</CardTitle>
          <p className="text-sm text-muted-foreground">
            Fine-tune individual personality traits
          </p>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="core" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="core">Core</TabsTrigger>
              <TabsTrigger value="advanced">Advanced</TabsTrigger>
              <TabsTrigger value="interaction">Interaction</TabsTrigger>
              <TabsTrigger value="expertise">Expertise</TabsTrigger>
            </TabsList>

            {Object.entries(traitCategories).map(([category, traits]) => (
              <TabsContent key={category} value={category} className="space-y-6">
                <div className="grid gap-6">
                  {traits.map((trait) => {
                    const Icon = trait.icon
                    return (
                      <motion.div
                        key={trait.key}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-3"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Icon className="h-5 w-5 text-blue-500" />
                            <div>
                              <h4 className="font-medium">{trait.label}</h4>
                              <p className="text-sm text-muted-foreground">
                                {getTraitDescription(trait.key, currentTraits[trait.key])}
                              </p>
                            </div>
                          </div>
                          <Badge variant="secondary">
                            {Math.round(currentTraits[trait.key] * 100)}%
                          </Badge>
                        </div>

                        <Slider
                          value={[currentTraits[trait.key]]}
                          onValueChange={([value]) => updateTrait(trait.key, value)}
                          min={0.1}
                          max={1.0}
                          step={0.1}
                          className="w-full"
                        />

                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Low</span>
                          <span>Balanced</span>
                          <span>High</span>
                        </div>
                      </motion.div>
                    )
                  })}
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      {/* Personality Preview */}
      <Card>
        <CardHeader>
          <CardTitle>Personality Preview</CardTitle>
          <p className="text-sm text-muted-foreground">
            See how your current personality settings would respond
          </p>
        </CardHeader>
        <CardContent>
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 rounded-lg p-6">
            <div className="space-y-4">
              <div className="flex gap-3">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-bold">AI</span>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium mb-1">Sample Response Based on Your Personality:</p>
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                    <p className="text-sm">
                      {currentTraits.creativity > 0.8
                        ? "What an intriguing question! Let's explore this creatively. I see multiple fascinating angles we could approach this from..."
                        : currentTraits.analytical > 0.8
                        ? "Let me break this down systematically. Based on the data and logical analysis, here's my step-by-step reasoning..."
                        : currentTraits.friendliness > 0.8
                        ? "I'd love to help you with that! Let's work through this together. What are your thoughts on the best approach?"
                        : "Here's a clear and direct answer to your question..."
                      }
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Save Reminder */}
      <AnimatePresence>
        {hasUnsavedChanges && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="fixed bottom-6 right-6 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2"
          >
            <Save className="h-4 w-4" />
            <span className="text-sm">Don't forget to save your changes!</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
