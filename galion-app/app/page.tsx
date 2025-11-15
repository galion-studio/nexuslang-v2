export default function VoiceLanding() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-blue-950 to-slate-950">
      {/* Navigation */}
      <nav className="border-b border-slate-800 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            Galion.app
          </div>
          <div className="flex gap-4">
            <a href="/auth/login" className="text-slate-400 hover:text-white transition">
              Login
            </a>
            <a
              href="/auth/register"
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white rounded-lg font-semibold transition"
            >
              Start Free
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <div className="max-w-4xl mx-auto px-6 py-20">
        <div className="text-center">
          <div className="mb-6">
            <span className="px-4 py-2 bg-blue-600/20 text-blue-400 rounded-full text-sm font-semibold">
              🎤 Voice-First AI Assistant
            </span>
          </div>

          <h1 className="text-5xl font-bold text-white mb-6 leading-tight">
            "Your imagination is the end."
          </h1>

          <h2 className="text-4xl font-bold text-white mb-6">
            Talk to Your AI Like a Human
          </h2>

          <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
            Experience the future of AI interaction. Voice commands, natural conversations,
            instant research, and intelligent assistance.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <a
              href="/auth/register"
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white rounded-xl font-semibold text-lg transition shadow-lg hover:shadow-xl"
            >
              Start Talking Free →
            </a>
            <button className="px-8 py-4 border border-slate-600 hover:border-slate-500 text-white rounded-xl font-semibold text-lg transition">
              Watch Demo
            </button>
          </div>

          {/* API Status */}
          <div className="bg-slate-900/50 backdrop-blur border border-slate-700 rounded-2xl p-6 max-w-2xl mx-auto">
            <h3 className="text-xl font-semibold text-white mb-4">API Connection Status</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
                <span className="text-slate-300">Backend: Connected</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
                <span className="text-slate-300">Voice AI: Active</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                <span className="text-slate-300">API: v1.0 Ready</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
                <span className="text-slate-300">Frontend: Connected</span>
              </div>
            </div>
            <div className="mt-4 p-3 bg-slate-800/50 rounded-lg">
              <p className="text-xs text-slate-400">
                <strong>API Endpoint:</strong> http://213.173.105.83:8000<br/>
                <strong>Status:</strong> <span className="text-green-400">Super Link Active</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
