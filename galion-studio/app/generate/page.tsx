'use client'

/**
 * Galion Studio - AI Generation Dashboard
 * Main hub for all content creation
 */

import { useState } from 'react'
import Link from 'next/link'
import { Image as ImageIcon, Video, FileText, Mic, Sparkles } from 'lucide-react'

export default function GeneratePage() {
  const [credits, setCredits] = useState(100) // From API later
  
  const tools = [
    {
      icon: ImageIcon,
      title: 'Image Generation',
      description: 'Create stunning images with Stable Diffusion, DALL-E, Midjourney',
      href: '/generate/image',
      color: 'purple',
      cost: '5 credits'
    },
    {
      icon: Video,
      title: 'Video Generation',
      description: 'Generate videos from text with Runway, Pika, AnimateDiff',
      href: '/generate/video',
      color: 'pink',
      cost: '20 credits'
    },
    {
      icon: FileText,
      title: 'Text Generation',
      description: 'Write content with Claude, GPT-4, Gemini Pro',
      href: '/generate/text',
      color: 'blue',
      cost: '2 credits'
    },
    {
      icon: Mic,
      title: 'Voice Synthesis',
      description: 'Generate natural speech with emotions and voice cloning',
      href: '/generate/voice',
      color: 'green',
      cost: '3 credits'
    },
  ]
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">AI Generation Studio</h1>
          <p className="text-zinc-400">Create images, videos, text, and voice content with AI</p>
          
          {/* Credits Display */}
          <div className="mt-6 inline-flex items-center gap-3 px-6 py-3 bg-purple-600/20 rounded-lg border border-purple-500/30">
            <Sparkles className="text-purple-400" size={20} />
            <span className="text-white font-semibold">{credits} Credits Available</span>
          </div>
        </div>
        
        {/* Tools Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {tools.map((tool, index) => (
            <Link
              key={index}
              href={tool.href}
              className="bg-zinc-900 p-8 rounded-xl border border-zinc-800 hover:border-purple-500/50 transition group"
            >
              <div className={`w-16 h-16 bg-${tool.color}-600/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition`}>
                <tool.icon className={`text-${tool.color}-400`} size={32} />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{tool.title}</h3>
              <p className="text-zinc-400 text-sm mb-4">{tool.description}</p>
              <div className="text-xs text-zinc-500">{tool.cost}</div>
            </Link>
          ))}
        </div>
        
        {/* Recent Projects */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-white mb-6">Recent Projects</h2>
          <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-8 text-center">
            <p className="text-zinc-500">Your generated content will appear here</p>
          </div>
        </div>
      </div>
    </div>
  )
}

