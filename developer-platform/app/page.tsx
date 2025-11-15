'use client'

import Link from 'next/link'
import { Code, Zap, Brain, Play, Terminal, Cpu, ArrowRight, Sparkles, Github, BookOpen } from 'lucide-react'

export default function DeveloperLanding() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-blue-950 to-slate-950">
      {/* Navigation */}
      <nav className="border-b border-slate-800 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            developer.galion.app
          </div>
          <div className="flex gap-4">
            <Link href="/ide" className="text-slate-400 hover:text-white transition font-medium">
              Web IDE
            </Link>
            <Link href="/chat" className="text-slate-400 hover:text-white transition font-medium">
              AI Chat
            </Link>
            <Link href="/developers" className="text-slate-400 hover:text-white transition font-medium">
              API Docs
            </Link>
            <Link href="/auth/login" className="text-slate-400 hover:text-white transition">
              Login
            </Link>
            <Link
              href="/auth/register"
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white rounded-lg font-semibold transition"
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
            <span className="px-4 py-2 bg-blue-600/20 text-blue-400 rounded-full text-sm font-semibold">
              🚀 AI-Native Development Platform
            </span>
          </div>

          <div className="mb-8">
            <h2 className="text-3xl font-semibold text-blue-400 italic mb-6">
              "Your imagination is the end."
            </h2>
          </div>

          <h1 className="text-7xl font-bold text-white mb-6 leading-tight">
            Code the Future
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent">
              With AI
            </span>
          </h1>

          <p className="text-xl text-slate-400 mb-8 max-w-3xl mx-auto">
            The only development platform designed from first principles for AI-native programming.
            Web IDE, NexusLang execution, AI assistance, and enterprise-grade APIs.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/ide"
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white rounded-xl font-semibold text-lg transition shadow-lg hover:shadow-xl flex items-center gap-2"
            >
              <Code className="h-5 w-5" />
              Open IDE Free
              <ArrowRight className="h-5 w-5" />
            </Link>
            <button className="px-8 py-4 border border-slate-600 hover:border-slate-500 text-white rounded-xl font-semibold text-lg transition">
              Watch Demo
            </button>
          </div>
        </div>

        {/* Code Demo */}
        <div className="max-w-4xl mx-auto mb-20">
          <div className="bg-slate-900/50 backdrop-blur border border-slate-700 rounded-2xl p-8">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600/20 rounded-full mb-4">
                <Terminal className="h-8 w-8 text-blue-400" />
              </div>
              <h3 className="text-2xl font-semibold text-white mb-2">Try NexusLang - AI-Native Code</h3>
              <p className="text-slate-400">Execute code with built-in AI capabilities</p>
            </div>

            <div className="bg-slate-800 rounded-lg p-6 font-mono text-sm">
              <div className="text-blue-400 mb-2">// Define AI behavior</div>
              <div className="text-purple-400">personality {'{'}curiosity: 0.9, creativity: 0.8{'}'}</div>
              <br />
              <div className="text-blue-400 mb-2">// Create neural network</div>
              <div className="text-green-400">let model = Sequential(</div>
              <div className="text-green-400 ml-4">Linear(784, 128),</div>
              <div className="text-green-400 ml-4">ReLU(),</div>
              <div className="text-green-400 ml-4">Linear(128, 10)</div>
              <div className="text-green-400">)</div>
              <br />
              <div className="text-blue-400 mb-2">// Query knowledge instantly</div>
              <div className="text-yellow-400">let facts = knowledge("quantum computing")</div>
              <br />
              <div className="text-blue-400 mb-2">// Natural language output</div>
              <div className="text-cyan-400">say("Neural network ready!", emotion="confident")</div>
            </div>

            <div className="flex justify-center mt-6">
              <Link
                href="/ide"
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition flex items-center gap-2"
              >
                <Play className="h-4 w-4" />
                Run This Code
              </Link>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600/20 rounded-full mb-6">
              <Code className="h-8 w-8 text-blue-400" />
            </div>
            <h3 className="text-2xl font-semibold text-white mb-4">Web IDE</h3>
            <p className="text-slate-400">
              Professional code editor with syntax highlighting, auto-completion,
              and real-time collaboration powered by AI.
            </p>
          </div>

          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-cyan-600/20 rounded-full mb-6">
              <Brain className="h-8 w-8 text-cyan-400" />
            </div>
            <h3 className="text-2xl font-semibold text-white mb-4">AI Chat</h3>
            <p className="text-slate-400">
              Conversational AI assistant available everywhere. Get help with code,
              debugging, architecture, and problem-solving.
            </p>
          </div>

          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-teal-600/20 rounded-full mb-6">
              <Cpu className="h-8 w-8 text-teal-400" />
            </div>
            <h3 className="text-2xl font-semibold text-white mb-4">NexusLang</h3>
            <p className="text-slate-400">
              Revolutionary AI-native programming language with 10x faster compilation,
              built-in ML primitives, and knowledge integration.
            </p>
          </div>
        </div>

        {/* Developer Tools */}
        <div className="bg-slate-900/30 backdrop-blur border border-slate-700 rounded-2xl p-8 mb-20">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Complete Developer Ecosystem</h2>
            <p className="text-xl text-slate-400">Everything you need to build AI-powered applications</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <Terminal className="h-12 w-12 text-blue-400 mx-auto mb-4" />
              <h4 className="text-lg font-semibold text-white mb-2">Code Execution</h4>
              <p className="text-slate-400 text-sm">Run Python, JavaScript, Bash, and NexusLang in the cloud</p>
            </div>
            <div className="text-center">
              <BookOpen className="h-12 w-12 text-cyan-400 mx-auto mb-4" />
              <h4 className="text-lg font-semibold text-white mb-2">Grokopedia</h4>
              <p className="text-slate-400 text-sm">AI-powered knowledge base with instant answers</p>
            </div>
            <div className="text-center">
              <Github className="h-12 w-12 text-teal-400 mx-auto mb-4" />
              <h4 className="text-lg font-semibold text-white mb-2">API Platform</h4>
              <p className="text-slate-400 text-sm">Complete REST API with 50+ endpoints for integration</p>
            </div>
            <div className="text-center">
              <Sparkles className="h-12 w-12 text-purple-400 mx-auto mb-4" />
              <h4 className="text-lg font-semibold text-white mb-2">AI Models</h4>
              <p className="text-slate-400 text-sm">Access 30+ AI models via OpenRouter integration</p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <h2 className="text-4xl font-bold text-white mb-4">Ready to Code the Future?</h2>
          <p className="text-xl text-slate-400 mb-8">Join developers building the next generation of AI applications</p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/register"
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white rounded-xl font-semibold text-lg transition shadow-lg hover:shadow-xl"
            >
              Start Building Free
              <Code className="ml-2 h-5 w-5" />
            </Link>
            <Link
              href="/developers"
              className="inline-flex items-center px-8 py-4 border border-slate-600 hover:border-slate-500 text-white rounded-xl font-semibold text-lg transition"
            >
              View API Docs
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>

          <p className="text-sm text-slate-500 mt-4">
            100 free credits • No setup required • Full IDE access
          </p>
        </div>
      </div>
    </div>
  )
}
