/**
 * Personality Editor Component
 * Interactive UI for creating personality blocks in NexusLang v2
 */

'use client'

import { useState } from 'react'
import { Sparkles } from 'lucide-react'

interface PersonalityTrait {
  name: string
  value: number
  description: string
  emoji: string
}

interface PersonalityEditorProps {
  onInsert: (code: string) => void
  onClose: () => void
}

export default function PersonalityEditor({ onInsert, onClose }: PersonalityEditorProps) {
  const [traits, setTraits] = useState<PersonalityTrait[]>([
    {
      name: 'curiosity',
      value: 0.8,
      description: 'Explores novel solutions and approaches',
      emoji: '🔍'
    },
    {
      name: 'analytical',
      value: 0.9,
      description: 'Uses systematic and logical thinking',
      emoji: '📊'
    },
    {
      name: 'creative',
      value: 0.7,
      description: 'Generates innovative and outside-the-box ideas',
      emoji: '💡'
    },
    {
      name: 'empathetic',
      value: 0.85,
      description: 'Understands and responds to user needs',
      emoji: '❤️'
    },
    {
      name: 'precision',
      value: 0.95,
      description: 'Prioritizes accuracy over speed',
      emoji: '🎯'
    },
    {
      name: 'verbosity',
      value: 0.6,
      description: 'Level of detail in explanations',
      emoji: '💬'
    }
  ])

  const updateTrait = (index: number, value: number) => {
    const newTraits = [...traits]
    newTraits[index].value = value
    setTraits(newTraits)
  }

  const generateCode = () => {
    let code = 'personality {\n'
    traits.forEach(trait => {
      code += `    ${trait.name}: ${trait.value.toFixed(2)},\n`
    })
    code = code.slice(0, -2) + '\n'  // Remove last comma
    code += '}\n'
    return code
  }

  const handleInsert = () => {
    const code = generateCode()
    onInsert(code)
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-zinc-900 rounded-lg shadow-xl w-[600px] max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-zinc-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sparkles className="text-purple-400" size={24} />
              <div>
                <h2 className="text-xl font-bold text-white">Personality Editor</h2>
                <p className="text-sm text-zinc-400">Define how your AI thinks and behaves</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-zinc-400 hover:text-white transition"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Traits */}
        <div className="p-6 space-y-6">
          {traits.map((trait, index) => (
            <div key={trait.name} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{trait.emoji}</span>
                  <div>
                    <h3 className="text-white font-semibold capitalize">{trait.name}</h3>
                    <p className="text-xs text-zinc-400">{trait.description}</p>
                  </div>
                </div>
                <span className="text-lg font-mono text-purple-400">{trait.value.toFixed(2)}</span>
              </div>
              
              {/* Slider */}
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={trait.value}
                onChange={(e) => updateTrait(index, parseFloat(e.target.value))}
                className="w-full h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
              />
              
              {/* Labels */}
              <div className="flex justify-between text-xs text-zinc-500">
                <span>Low (0.0)</span>
                <span>Medium (0.5)</span>
                <span>High (1.0)</span>
              </div>
            </div>
          ))}
        </div>

        {/* Preview */}
        <div className="p-6 border-t border-zinc-800">
          <h3 className="text-sm font-semibold text-zinc-400 mb-2">Code Preview:</h3>
          <pre className="bg-zinc-950 p-4 rounded text-sm text-zinc-300 font-mono overflow-x-auto">
            {generateCode()}
          </pre>
        </div>

        {/* Actions */}
        <div className="p-6 border-t border-zinc-800 flex gap-3 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-zinc-400 hover:text-white transition"
          >
            Cancel
          </button>
          <button
            onClick={handleInsert}
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition font-semibold"
          >
            Insert Code
          </button>
        </div>
      </div>
    </div>
  )
}

