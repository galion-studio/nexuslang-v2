'use client'

import { useState } from 'react'
import { Brain, Heart, Zap, Shield, Users, Lightbulb } from 'lucide-react'

interface PersonalityTrait {
  id: string
  name: string
  description: string
  icon: any
  value: number
  minLabel: string
  maxLabel: string
}

const personalityTraits: PersonalityTrait[] = [
  {
    id: 'intelligence',
    name: 'Intelligence',
    description: 'Analytical thinking and problem-solving',
    icon: Brain,
    value: 85,
    minLabel: 'Basic',
    maxLabel: 'Expert'
  },
  {
    id: 'creativity',
    name: 'Creativity',
    description: 'Innovation and artistic expression',
    icon: Lightbulb,
    value: 75,
    minLabel: 'Practical',
    maxLabel: 'Visionary'
  },
  {
    id: 'empathy',
    name: 'Empathy',
    description: 'Understanding and emotional intelligence',
    icon: Heart,
    value: 90,
    minLabel: 'Logical',
    maxLabel: 'Empathetic'
  },
  {
    id: 'efficiency',
    name: 'Efficiency',
    description: 'Speed and resource optimization',
    icon: Zap,
    value: 80,
    minLabel: 'Thorough',
    maxLabel: 'Efficient'
  },
  {
    id: 'safety',
    name: 'Safety',
    description: 'Risk assessment and security focus',
    icon: Shield,
    value: 95,
    minLabel: 'Bold',
    maxLabel: 'Cautious'
  },
  {
    id: 'collaboration',
    name: 'Collaboration',
    description: 'Teamwork and communication skills',
    icon: Users,
    value: 85,
    minLabel: 'Independent',
    maxLabel: 'Collaborative'
  }
]

interface PersonalityEditorProps {
  className?: string
}

export function PersonalityEditor({ className = '' }: PersonalityEditorProps) {
  const [traits, setTraits] = useState<PersonalityTrait[]>(personalityTraits)
  const [selectedTemplate, setSelectedTemplate] = useState('balanced')

  const templates = {
    balanced: 'Balanced - All traits evenly distributed',
    creative: 'Creative - High creativity and empathy',
    technical: 'Technical - High intelligence and efficiency',
    supportive: 'Supportive - High empathy and collaboration',
    innovative: 'Innovative - High creativity and intelligence'
  }

  const applyTemplate = (template: string) => {
    setSelectedTemplate(template)
    // In a real implementation, this would load preset values
    console.log('Applying template:', template)
  }

  const updateTrait = (id: string, value: number) => {
    setTraits(prev =>
      prev.map(trait =>
        trait.id === id ? { ...trait, value } : trait
      )
    )
  }

  return (
    <div className={`p-6 space-y-6 ${className}`}>
      {/* Header */}
      <div className="text-center">
        <h2 className="text-xl font-semibold text-foreground mb-2">
          AI Personality Editor
        </h2>
        <p className="text-foreground-muted">
          Customize your AI assistant's personality and behavior
        </p>
      </div>

      {/* Template Selection */}
      <div className="bg-surface-hover rounded-lg p-4">
        <h3 className="text-sm font-medium text-foreground mb-3">Quick Templates</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {Object.entries(templates).map(([key, description]) => (
            <button
              key={key}
              onClick={() => applyTemplate(key)}
              className={`p-3 text-left rounded-md transition-colors ${
                selectedTemplate === key
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-surface hover:bg-surface-active'
              }`}
            >
              <div className="font-medium text-sm capitalize">{key}</div>
              <div className="text-xs opacity-80">{description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Personality Traits */}
      <div className="space-y-4">
        <h3 className="text-sm font-medium text-foreground">Personality Traits</h3>

        {traits.map((trait) => {
          const IconComponent = trait.icon
          return (
            <div key={trait.id} className="bg-surface-hover rounded-lg p-4">
              <div className="flex items-center space-x-3 mb-3">
                <IconComponent className="w-5 h-5 text-primary" />
                <div className="flex-1">
                  <div className="font-medium text-foreground">{trait.name}</div>
                  <div className="text-sm text-foreground-muted">{trait.description}</div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold text-primary">{trait.value}%</div>
                </div>
              </div>

              <div className="space-y-2">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={trait.value}
                  onChange={(e) => updateTrait(trait.id, parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                />
                <div className="flex justify-between text-xs text-foreground-muted">
                  <span>{trait.minLabel}</span>
                  <span>{trait.maxLabel}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Preview */}
      <div className="bg-surface-hover rounded-lg p-4">
        <h3 className="text-sm font-medium text-foreground mb-3">Personality Preview</h3>
        <div className="bg-surface rounded-lg p-4">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <Brain className="w-4 h-4 text-primary-foreground" />
            </div>
            <div>
              <div className="font-medium text-foreground">Galion AI</div>
              <div className="text-sm text-foreground-muted">
                {selectedTemplate.charAt(0).toUpperCase() + selectedTemplate.slice(1)} Personality
              </div>
            </div>
          </div>
          <p className="text-sm text-foreground">
            "I understand you're working on a NexusLang project. I can help you optimize the Fibonacci function
            for better performance while maintaining readability. Would you like me to show you some improvements?"
          </p>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary-hover transition-colors">
          Save Personality Settings
        </button>
      </div>
    </div>
  )
}

export default PersonalityEditor
