'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Slider } from '../ui/slider'

interface PersonalityTrait {
  name: string
  value: number
  description: string
  category: string
}

interface PersonalityTemplate {
  name: string
  description: string
  traits: Record<string, number>
}

const defaultTraits: PersonalityTrait[] = [
  { name: 'curiosity', value: 0.5, description: 'Explores novel solutions and asks questions', category: 'cognitive' },
  { name: 'analytical', value: 0.5, description: 'Systematic thinking and logical reasoning', category: 'cognitive' },
  { name: 'creative', value: 0.5, description: 'Outside-the-box thinking and innovation', category: 'cognitive' },
  { name: 'empathetic', value: 0.5, description: 'Understands and considers user feelings', category: 'emotional' },
  { name: 'helpfulness', value: 0.5, description: 'Focuses on being maximally useful', category: 'social' },
  { name: 'transparency', value: 0.5, description: 'Honest about capabilities and limitations', category: 'social' },
  { name: 'adaptability', value: 0.5, description: 'Learns and adapts from feedback', category: 'behavioral' },
  { name: 'precision', value: 0.5, description: 'Attention to detail and accuracy', category: 'behavioral' },
  { name: 'patience', value: 0.5, description: 'Takes time to think through complex problems', category: 'behavioral' },
  { name: 'innovation', value: 0.5, description: 'Creates new approaches and solutions', category: 'cognitive' },
  { name: 'confidence', value: 0.5, description: 'Expresses certainty in responses', category: 'social' },
  { name: 'diplomacy', value: 0.5, description: 'Handles conflicts and disagreements gracefully', category: 'social' },
  { name: 'persistence', value: 0.5, description: 'Continues working on difficult problems', category: 'behavioral' },
  { name: 'openness', value: 0.5, description: 'Willing to consider new ideas and perspectives', category: 'cognitive' },
  { name: 'thoroughness', value: 0.5, description: 'Comprehensive and detailed approach', category: 'behavioral' }
]

const personalityTemplates: PersonalityTemplate[] = [
  {
    name: 'Creative Writer',
    description: 'Excellent for storytelling, content creation, and imaginative tasks',
    traits: {
      creativity: 0.95,
      empathy: 0.8,
      analytical: 0.3,
      curiosity: 0.9,
      transparency: 0.7,
      adaptability: 0.8,
      innovation: 0.9,
      openness: 0.9,
      patience: 0.6
    }
  },
  {
    name: 'Analytical Researcher',
    description: 'Perfect for data analysis, research, and systematic problem-solving',
    traits: {
      analytical: 0.95,
      precision: 0.9,
      curiosity: 0.8,
      thoroughness: 0.9,
      transparency: 0.8,
      persistence: 0.8,
      creativity: 0.2,
      adaptability: 0.6
    }
  },
  {
    name: 'Empathetic Teacher',
    description: 'Ideal for education, mentoring, and user-friendly explanations',
    traits: {
      empathy: 0.95,
      helpfulness: 0.9,
      patience: 0.8,
      transparency: 0.9,
      adaptability: 0.8,
      creativity: 0.6,
      analytical: 0.5,
      diplomacy: 0.8
    }
  },
  {
    name: 'Technical Expert',
    description: 'Specialized for coding, debugging, and technical problem-solving',
    traits: {
      analytical: 0.9,
      precision: 0.95,
      helpfulness: 0.8,
      persistence: 0.8,
      transparency: 0.7,
      curiosity: 0.7,
      thoroughness: 0.9,
      adaptability: 0.6
    }
  },
  {
    name: 'Balanced Assistant',
    description: 'Well-rounded personality suitable for general tasks',
    traits: {
      analytical: 0.6,
      creativity: 0.6,
      empathy: 0.7,
      helpfulness: 0.8,
      transparency: 0.8,
      adaptability: 0.7,
      precision: 0.6,
      curiosity: 0.7
    }
  }
]

interface PersonalityEditorProps {
  onPersonalityChange?: (traits: Record<string, number>) => void
  initialTraits?: Record<string, number>
}

const PersonalityEditor: React.FC<PersonalityEditorProps> = ({
  onPersonalityChange,
  initialTraits = {}
}) => {
  const [traits, setTraits] = useState<PersonalityTrait[]>(() =>
    defaultTraits.map(trait => ({
      ...trait,
      value: initialTraits[trait.name] ?? trait.value
    }))
  )

  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')

  const categories = ['all', ...Array.from(new Set(traits.map(t => t.category)))]

  useEffect(() => {
    const traitValues = traits.reduce((acc, trait) => {
      acc[trait.name] = trait.value
      return acc
    }, {} as Record<string, number>)

    if (onPersonalityChange) {
      onPersonalityChange(traitValues)
    }
  }, [traits, onPersonalityChange])

  const updateTrait = (traitName: string, value: number) => {
    setTraits(prevTraits =>
      prevTraits.map(trait =>
        trait.name === traitName ? { ...trait, value } : trait
      )
    )
  }

  const applyTemplate = (template: PersonalityTemplate) => {
    setSelectedTemplate(template.name)
    setTraits(prevTraits =>
      prevTraits.map(trait => ({
        ...trait,
        value: template.traits[trait.name] ?? trait.value
      }))
    )
  }

  const resetToDefaults = () => {
    setSelectedTemplate('')
    setTraits(defaultTraits)
  }

  const filteredTraits = selectedCategory === 'all'
    ? traits
    : traits.filter(trait => trait.category === selectedCategory)

  const getTraitLevel = (value: number): { level: string; color: string } => {
    if (value >= 0.8) return { level: 'Very High', color: 'text-green-400' }
    if (value >= 0.6) return { level: 'High', color: 'text-blue-400' }
    if (value >= 0.4) return { level: 'Medium', color: 'text-yellow-400' }
    if (value >= 0.2) return { level: 'Low', color: 'text-orange-400' }
    return { level: 'Very Low', color: 'text-red-400' }
  }

  return (
    <div className="space-y-6">
      {/* Personality Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🎭 Personality Templates
            {selectedTemplate && (
              <span className="text-sm text-blue-400 font-normal">
                (Active: {selectedTemplate})
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {personalityTemplates.map((template) => (
              <div
                key={template.name}
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  selectedTemplate === template.name
                    ? 'border-blue-500 bg-blue-900/20'
                    : 'border-gray-600 hover:border-gray-500'
                }`}
                onClick={() => applyTemplate(template)}
              >
                <h4 className="font-semibold text-white mb-2">{template.name}</h4>
                <p className="text-sm text-gray-400 mb-3">{template.description}</p>
                <div className="flex flex-wrap gap-1">
                  {Object.entries(template.traits)
                    .filter(([, value]) => value > 0.7)
                    .slice(0, 3)
                    .map(([trait, value]) => (
                      <span
                        key={trait}
                        className="text-xs bg-blue-600/50 text-blue-200 px-2 py-1 rounded"
                      >
                        {trait}: {(value * 100).toFixed(0)}%
                      </span>
                    ))}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 flex gap-2">
            <Button
              onClick={resetToDefaults}
              variant="outline"
              size="sm"
            >
              Reset to Defaults
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Category Filter */}
      <Card>
        <CardHeader>
          <CardTitle>🎯 Trait Categories</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <Button
                key={category}
                onClick={() => setSelectedCategory(category)}
                variant={selectedCategory === category ? "default" : "outline"}
                size="sm"
                className="capitalize"
              >
                {category}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Personality Traits */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            🧠 Personality Traits
            <span className="text-sm text-gray-400">
              {filteredTraits.length} traits
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {filteredTraits.map((trait) => {
              const traitLevel = getTraitLevel(trait.value)
              return (
                <div key={trait.name} className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-white capitalize">
                        {trait.name.replace('_', ' ')}
                      </h4>
                      <p className="text-sm text-gray-400">{trait.description}</p>
                    </div>
                    <div className="text-right">
                      <div className={`font-semibold ${traitLevel.color}`}>
                        {traitLevel.level}
                      </div>
                      <div className="text-sm text-gray-500">
                        {(trait.value * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>

                  <Slider
                    value={[trait.value]}
                    onValueChange={(value) => updateTrait(trait.name, value[0])}
                    max={1}
                    min={0}
                    step={0.1}
                    className="w-full"
                  />

                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Very Low</span>
                    <span>Balanced</span>
                    <span>Very High</span>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Personality Preview */}
      <Card>
        <CardHeader>
          <CardTitle>👀 Personality Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-900 p-4 rounded-lg font-mono text-sm">
            <div className="text-green-400">
              personality {'{'}
              {traits
                .filter(trait => trait.value > 0.3)
                .map(trait => (
                  <div key={trait.name} className="ml-4">
                    {trait.name}: {trait.value.toFixed(1)},
                  </div>
                ))}
              {'}'}
            </div>
          </div>
          <p className="text-sm text-gray-400 mt-2">
            This is how your personality configuration will appear in NexusLang code.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

export default PersonalityEditor
