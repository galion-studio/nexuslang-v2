'use client'

/**
 * Galion Studio - Landing Page
 * AI Content Creation Platform
 */

import Link from 'next/link'
import { Sparkles, Image, Video, FileText, Mic, ArrowRight, Check } from 'lucide-react'

export default function StudioLanding() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-950 via-zinc-900 to-zinc-950">
      {/* Navigation */}
      <nav className="border-b border-zinc-800 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Galion Studio
          </div>
          <div className="flex gap-4">
            <Link href="/auth/login" className="text-zinc-400 hover:text-white transition">
              Login
            </Link>
            <Link
              href="/auth/register"
              className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-semibold transition"
            >
              Start Free
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-20">
          <div className="mb-6">
            <span className="px-4 py-2 bg-purple-600/20 text-purple-400 rounded-full text-sm font-semibold">
              ✨ AI-Powered Content Creation
            </span>
          </div>
          
          <h1 className="text-7xl font-bold text-white mb-6 leading-tight">
            Create Stunning Content
            <br />
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-orange-400 bg-clip-text text-transparent">
              With AI
            </span>
          </h1>
          
          <p className="text-2xl text-zinc-300 mb-4 font-medium">
            Images. Videos. Text. Voice. All in one platform.
          </p>
          
          <p className="text-lg text-zinc-500 mb-10 max-w-2xl mx-auto">
            Professional AI tools for creators, marketers, and businesses. 
            Generate content 10x faster with 30+ AI models.
          </p>
          
          <div className="flex gap-4 justify-center">
            <Link
              href="/auth/register"
              className="px-10 py-5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 
                         hover:to-pink-700 text-white rounded-lg font-bold text-xl transition 
                         flex items-center gap-3 shadow-lg shadow-purple-500/50"
            >
              <Sparkles size={24} />
              Start Creating Free
            </Link>
          </div>
          
          <p className="text-sm text-zinc-500 mt-4">
            Free tier • 100 credits • No credit card needed
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-4 gap-6 mb-20">
          <div className="bg-zinc-900/50 backdrop-blur p-8 rounded-xl border border-purple-500/20 hover:border-purple-500/40 transition">
            <div className="w-14 h-14 bg-purple-600/20 rounded-lg flex items-center justify-center mb-4">
              <Image className="text-purple-400" size={28} />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Image Generation</h3>
            <p className="text-zinc-400">
              Stable Diffusion, DALL-E 3, Midjourney. Create stunning visuals instantly.
            </p>
          </div>

          <div className="bg-zinc-900/50 backdrop-blur p-8 rounded-xl border border-pink-500/20 hover:border-pink-500/40 transition">
            <div className="w-14 h-14 bg-pink-600/20 rounded-lg flex items-center justify-center mb-4">
              <Video className="text-pink-400" size={28} />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Video Creation</h3>
            <p className="text-zinc-400">
              Runway, Pika, AnimateDiff. Generate videos from text in seconds.
            </p>
          </div>

          <div className="bg-zinc-900/50 backdrop-blur p-8 rounded-xl border border-blue-500/20 hover:border-blue-500/40 transition">
            <div className="w-14 h-14 bg-blue-600/20 rounded-lg flex items-center justify-center mb-4">
              <FileText className="text-blue-400" size={28} />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Content Writing</h3>
            <p className="text-zinc-400">
              Claude, GPT-4, Gemini. Write blog posts, social content, and more.
            </p>
          </div>

          <div className="bg-zinc-900/50 backdrop-blur p-8 rounded-xl border border-green-500/20 hover:border-green-500/40 transition">
            <div className="w-14 h-14 bg-green-600/20 rounded-lg flex items-center justify-center mb-4">
              <Mic className="text-green-400" size={28} />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Voice Synthesis</h3>
            <p className="text-zinc-400">
              AI voices with emotions. Text-to-speech and voice cloning.
            </p>
          </div>
        </div>

        {/* Pricing Preview */}
        <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-xl p-12 border border-purple-500/30">
          <h2 className="text-4xl font-bold text-white text-center mb-8">
            Start Free, Upgrade When Ready
          </h2>
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <div className="bg-zinc-900/70 p-6 rounded-lg">
              <div className="text-3xl font-bold text-white mb-2">Free</div>
              <div className="text-zinc-400 mb-4">100 credits/month</div>
              <ul className="space-y-2 text-sm text-zinc-400">
                <li className="flex items-center gap-2">
                  <Check size={16} className="text-green-400" />
                  20 images
                </li>
                <li className="flex items-center gap-2">
                  <Check size={16} className="text-green-400" />
                  10 videos
                </li>
                <li className="flex items-center gap-2">
                  <Check size={16} className="text-green-400" />
                  50 text generations
                </li>
              </ul>
            </div>

            <div className="bg-gradient-to-br from-purple-900 to-pink-900 p-6 rounded-lg border-2 border-purple-400">
              <div className="text-xs text-purple-300 font-bold mb-2">MOST POPULAR</div>
              <div className="text-3xl font-bold text-white mb-2">$20/mo</div>
              <div className="text-zinc-300 mb-4">Creator Tier</div>
              <ul className="space-y-2 text-sm text-zinc-300">
                <li className="flex items-center gap-2">
                  <Check size={16} className="text-green-400" />
                  200 images
                </li>
                <li className="flex items-center gap-2">
                  <Check size={16} className="text-green-400" />
                  50 videos
                </li>
                <li className="flex items-center gap-2">
                  <Check size={16} className="text-green-400" />
                  Commercial license
                </li>
              </ul>
            </div>

            <div className="bg-zinc-900/70 p-6 rounded-lg">
              <div className="text-3xl font-bold text-white mb-2">$50/mo</div>
              <div className="text-zinc-400 mb-4">Professional</div>
              <ul className="space-y-2 text-sm text-zinc-400">
                <li className="flex items-center gap-2">
                  <Check size={16} className="text-green-400" />
                  1,000 images
                </li>
                <li className="flex items-center gap-2">
                  <Check size={16} className="text-green-400" />
                  200 videos
                </li>
                <li className="flex items-center gap-2">
                  <Check size={16} className="text-green-400" />
                  Team features
                </li>
              </ul>
            </div>
          </div>
          <div className="text-center mt-8">
            <Link
              href="/pricing"
              className="text-purple-400 hover:text-purple-300 font-semibold inline-flex items-center gap-2"
            >
              See all plans <ArrowRight size={18} />
            </Link>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-20">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Create?
          </h2>
          <p className="text-xl text-zinc-400 mb-8">
            Join creators using AI to scale their content production
          </p>
          <Link
            href="/auth/register"
            className="inline-block px-10 py-4 bg-gradient-to-r from-purple-600 to-pink-600 
                       hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-bold text-lg transition"
          >
            Get Started Free
          </Link>
        </div>

        {/* Footer */}
        <div className="mt-20 pt-10 border-t border-zinc-800 text-center text-zinc-500 text-sm">
          <p>© 2025 Galion Studio. Powered by NexusLang v2. Built with AI for creators.</p>
        </div>
      </div>
    </div>
  )
}

