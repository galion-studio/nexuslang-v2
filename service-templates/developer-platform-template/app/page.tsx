import { Code2, Terminal, FileCode, Zap, Monitor, Globe } from 'lucide-react'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      <div className="max-w-4xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-emerald-600 rounded-full">
              <Code2 className="h-12 w-12 text-white" />
            </div>
          </div>
          <h1 className="text-5xl font-bold">
            Developer Platform
          </h1>
          <p className="text-xl text-gray-300">
            Web-Based Integrated Development Environment
          </p>
        </div>

        {/* Status Card */}
        <div className="bg-slate-800 rounded-lg shadow-2xl p-8 border border-slate-700">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold">
              IDE Status
            </h2>
            <span className="inline-flex items-center px-4 py-2 bg-emerald-900 text-emerald-300 rounded-full font-medium border border-emerald-700">
              <span className="h-2 w-2 bg-emerald-400 rounded-full mr-2 animate-pulse"></span>
              Ready
            </span>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="flex flex-col items-center p-4 bg-slate-700 rounded-lg border border-slate-600">
              <Terminal className="h-8 w-8 text-emerald-400 mb-2" />
              <h3 className="font-semibold">Terminal</h3>
              <p className="text-sm text-gray-400 text-center mt-1">
                Integrated terminal access
              </p>
            </div>

            <div className="flex flex-col items-center p-4 bg-slate-700 rounded-lg border border-slate-600">
              <FileCode className="h-8 w-8 text-blue-400 mb-2" />
              <h3 className="font-semibold">Code Editor</h3>
              <p className="text-sm text-gray-400 text-center mt-1">
                Monaco-based editor
              </p>
            </div>

            <div className="flex flex-col items-center p-4 bg-slate-700 rounded-lg border border-slate-600">
              <Zap className="h-8 w-8 text-yellow-400 mb-2" />
              <h3 className="font-semibold">Fast</h3>
              <p className="text-sm text-gray-400 text-center mt-1">
                Lightning-fast performance
              </p>
            </div>
          </div>

          {/* Additional Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            <div className="flex flex-col items-center p-4 bg-slate-700 rounded-lg border border-slate-600">
              <Monitor className="h-8 w-8 text-purple-400 mb-2" />
              <h3 className="font-semibold">Live Preview</h3>
              <p className="text-sm text-gray-400 text-center mt-1">
                Real-time code preview
              </p>
            </div>

            <div className="flex flex-col items-center p-4 bg-slate-700 rounded-lg border border-slate-600">
              <Globe className="h-8 w-8 text-cyan-400 mb-2" />
              <h3 className="font-semibold">Cloud-Based</h3>
              <p className="text-sm text-gray-400 text-center mt-1">
                Access from anywhere
              </p>
            </div>

            <div className="flex flex-col items-center p-4 bg-slate-700 rounded-lg border border-slate-600">
              <Code2 className="h-8 w-8 text-pink-400 mb-2" />
              <h3 className="font-semibold">Multi-Language</h3>
              <p className="text-sm text-gray-400 text-center mt-1">
                Support for all languages
              </p>
            </div>
          </div>
        </div>

        {/* Info */}
        <div className="text-center text-sm text-gray-400">
          <p>IDE service is running successfully</p>
          <p className="mt-2">Version 1.0.0 • Port 3003</p>
        </div>
      </div>
    </main>
  )
}

