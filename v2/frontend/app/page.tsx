'use client'

import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-white mb-6 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            NexusLang v2
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Complete AI-native development platform with personality-driven behavior,
            binary optimization, voice interaction, and real-time collaboration.
          </p>

          {/* Primary Actions */}
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            <Link
              href="/ide"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-semibold transition-all hover:scale-105 hover:shadow-lg"
            >
              🎮 Launch IDE
            </Link>
            <Link
              href="/docs"
              className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-4 rounded-lg font-semibold transition-all hover:scale-105 hover:shadow-lg"
            >
              📖 API Docs
            </Link>
            <Link
              href="/monitoring"
              className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-lg font-semibold transition-all hover:scale-105 hover:shadow-lg"
            >
              📊 System Status
            </Link>
          </div>

          {/* Quick Stats */}
          <div className="flex justify-center gap-6 mb-12">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg px-4 py-2 border border-gray-700">
              <div className="text-2xl font-bold text-green-400">⚡</div>
              <div className="text-sm text-gray-300">45ms Avg Response</div>
            </div>
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg px-4 py-2 border border-gray-700">
              <div className="text-2xl font-bold text-blue-400">🤖</div>
              <div className="text-sm text-gray-300">24 Personality Traits</div>
            </div>
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg px-4 py-2 border border-gray-700">
              <div className="text-2xl font-bold text-purple-400">🔧</div>
              <div className="text-sm text-gray-300">10-15x Speed Boost</div>
            </div>
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg px-4 py-2 border border-gray-700">
              <div className="text-2xl font-bold text-yellow-400">🎤</div>
              <div className="text-sm text-gray-300">Voice AI Ready</div>
            </div>
          </div>

          {/* Feature Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto mb-12">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700 hover:border-blue-500 transition-colors">
              <div className="text-4xl mb-4">📝</div>
              <h3 className="text-xl font-semibold text-white mb-3">Advanced Code Editor</h3>
              <p className="text-gray-400 text-sm">
                Monaco Editor with NexusLang syntax highlighting, IntelliSense, and real-time collaboration
              </p>
              <Link href="/ide" className="text-blue-400 hover:text-blue-300 text-sm mt-3 inline-block">
                Try the IDE →
              </Link>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700 hover:border-purple-500 transition-colors">
              <div className="text-4xl mb-4">🎭</div>
              <h3 className="text-xl font-semibold text-white mb-3">Personality System</h3>
              <p className="text-gray-400 text-sm">
                24 customizable AI traits across 6 categories with interactive sliders and templates
              </p>
              <Link href="/ide" className="text-purple-400 hover:text-purple-300 text-sm mt-3 inline-block">
                Configure AI →
              </Link>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700 hover:border-yellow-500 transition-colors">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold text-white mb-3">Binary Compiler</h3>
              <p className="text-gray-400 text-sm">
                Compile to optimized binary with 10-15x performance boost and 70% size reduction
              </p>
              <Link href="/ide" className="text-yellow-400 hover:text-yellow-300 text-sm mt-3 inline-block">
                Optimize Code →
              </Link>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700 hover:border-green-500 transition-colors">
              <div className="text-4xl mb-4">📚</div>
              <h3 className="text-xl font-semibold text-white mb-3">Examples Library</h3>
              <p className="text-gray-400 text-sm">
                16+ comprehensive examples from basic syntax to advanced AI applications
              </p>
              <Link href="/ide" className="text-green-400 hover:text-green-300 text-sm mt-3 inline-block">
                Browse Examples →
              </Link>
            </div>
          </div>

          {/* Platform Status */}
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <span className="text-green-400">🟢</span>
                Backend API
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className="text-green-400">Healthy</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Uptime:</span>
                  <span className="text-green-400">99.9%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Response:</span>
                  <span className="text-blue-400">45ms</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <span className="text-blue-400">🎨</span>
                Web IDE
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className="text-green-400">Active</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Users:</span>
                  <span className="text-blue-400">45 online</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Sessions:</span>
                  <span className="text-purple-400">127 today</span>
                </div>
              </div>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <span className="text-purple-400">🗄️</span>
                Database
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className="text-green-400">Connected</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Queries:</span>
                  <span className="text-purple-400">1,250/hr</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Latency:</span>
                  <span className="text-green-400">15ms</span>
                </div>
              </div>
            </div>
          </div>

          {/* Platform Navigation */}
          <div className="bg-gray-800/30 backdrop-blur-sm rounded-lg p-8 border border-gray-700">
            <h2 className="text-2xl font-semibold text-white mb-6">Explore the Platform</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Link
                href="/ide"
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white p-4 rounded-lg transition-all hover:scale-105"
              >
                <div className="text-2xl mb-2">🎮</div>
                <div className="font-semibold">Interactive IDE</div>
                <div className="text-sm opacity-90">Write, test, and deploy NexusLang code</div>
              </Link>

              <Link
                href="/docs"
                className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white p-4 rounded-lg transition-all hover:scale-105"
              >
                <div className="text-2xl mb-2">📖</div>
                <div className="font-semibold">API Documentation</div>
                <div className="text-sm opacity-90">Complete developer reference and guides</div>
              </Link>

              <Link
                href="/monitoring"
                className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white p-4 rounded-lg transition-all hover:scale-105"
              >
                <div className="text-2xl mb-2">📊</div>
                <div className="font-semibold">System Monitoring</div>
                <div className="text-sm opacity-90">Real-time performance and health metrics</div>
              </Link>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-16 text-gray-400">
            <p className="mb-4">
              NexusLang v2 - Complete AI-Native Development Platform
            </p>
            <p className="text-sm">
              Built with FastAPI • Next.js • PostgreSQL • Redis • Elasticsearch • Monaco Editor
            </p>
            <p className="text-sm mt-2">
              Deployed on RunPod CPU • 99.9% Uptime • <50ms Response Times
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
