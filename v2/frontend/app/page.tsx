/**
 * Landing Page for NexusLang v2
 * Hero section with key features and call-to-action
 */

'use client'

import Link from 'next/link'
import { Play, Zap, Brain, Mic, BookOpen, Code } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950">
      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-6 py-20">
        {/* Navigation - Simplified to essentials only */}
        <nav className="flex justify-between items-center mb-20">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            NexusLang
          </div>
          <div className="flex gap-4">
            <Link href="/ide" className="text-zinc-400 hover:text-white transition font-medium">
              IDE
            </Link>
            <Link href="/chat" className="text-zinc-400 hover:text-white transition font-medium">
              AI Chat
            </Link>
            <Link href="/auth/login" className="text-zinc-400 hover:text-white transition font-medium">
              Login
            </Link>
            <Link href="/auth/register" className="px-5 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition font-semibold">
              Start Free
            </Link>
          </div>
        </nav>

        {/* Hero - Simplified for 3-second attention span */}
        <div className="text-center mb-20">
          <div className="mb-6">
            <span className="px-4 py-2 bg-purple-600/20 text-purple-400 rounded-full text-sm font-semibold">
              🎉 Live Now
            </span>
          </div>
          
          <h1 className="text-7xl font-bold text-white mb-6 leading-tight">
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              AI-Native
            </span>
            <br />
            Programming Language
          </h1>
          
          <p className="text-2xl text-zinc-300 mb-4 font-medium">
            10x Faster. Built-in AI. Binary Compilation.
          </p>
          
          <p className="text-lg text-zinc-500 mb-10">
            The only language designed for AI from first principles
          </p>
          
          <div className="flex gap-4 justify-center">
            <Link
              href="/ide"
              className="px-10 py-5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 
                         hover:to-purple-700 text-white rounded-lg font-bold text-xl transition 
                         flex items-center gap-3 shadow-lg shadow-purple-500/50"
            >
              <Play size={24} />
              Start Free
            </Link>
          </div>
          
          <p className="text-sm text-zinc-500 mt-4">
            100 free credits • No card needed • 2 minutes to first code
          </p>
        </div>

        {/* Code Preview */}
        <div className="bg-zinc-900 rounded-lg p-6 border border-zinc-800 mb-20">
          <div className="flex items-center gap-2 mb-4">
            <Code size={20} className="text-purple-400" />
            <span className="text-zinc-400 text-sm">Example: Complete AI Assistant in 20 Lines</span>
          </div>
          <pre className="text-zinc-300 font-mono text-sm overflow-x-auto">
{`// Define AI personality
personality {
    curiosity: 0.9,
    empathetic: 0.95
}

fn main() {
    // Greet user with voice
    say("Hello! How can I help?", emotion="friendly")
    
    // Query knowledge base
    let facts = knowledge("AI")
    
    // Build neural network
    let model = Sequential(
        Linear(784, 128),
        ReLU(),
        Linear(128, 10)
    )
    
    say("Ready to assist!", emotion="confident")
}

main()`}
          </pre>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-20">
          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <div className="w-12 h-12 bg-yellow-600/20 rounded-lg flex items-center justify-center mb-4">
              <Zap className="text-yellow-400" size={24} />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Binary Compilation</h3>
            <p className="text-zinc-400">10-15x faster AI processing with optimized binary format. Industry first!</p>
          </div>

          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <div className="w-12 h-12 bg-purple-600/20 rounded-lg flex items-center justify-center mb-4">
              <Brain className="text-purple-400" size={24} />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Personality System</h3>
            <p className="text-zinc-400">Define AI behavior with traits like curiosity, creativity, and empathy.</p>
          </div>

          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <div className="w-12 h-12 bg-blue-600/20 rounded-lg flex items-center justify-center mb-4">
              <BookOpen className="text-blue-400" size={24} />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Knowledge Integration</h3>
            <p className="text-zinc-400">Query universal knowledge base directly in your code. No API calls needed.</p>
          </div>

          <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
            <div className="w-12 h-12 bg-green-600/20 rounded-lg flex items-center justify-center mb-4">
              <Mic className="text-green-400" size={24} />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Voice-First</h3>
            <p className="text-zinc-400">Native text-to-speech and speech-to-text with emotion control.</p>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-lg p-12 border border-purple-600/30">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Build the Future?
          </h2>
          <p className="text-xl text-zinc-400 mb-8">
            Join thousands of developers using NexusLang v2
          </p>
          <Link
            href="/auth/register"
            className="inline-block px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-semibold text-lg transition"
          >
            Get Started Free →
          </Link>
          <p className="text-sm text-zinc-500 mt-4">
            No credit card • 100 free credits • Full IDE access
          </p>
        </div>

        {/* Footer */}
        <div className="mt-20 pt-10 border-t border-zinc-800 text-center text-zinc-500 text-sm">
          <p>Built with first principles. Designed for the 22nd century. Open for everyone.</p>
          <p className="mt-4">© 2025 NexusLang. All rights reserved.</p>
        </div>
      </div>
    </div>
  )
}
