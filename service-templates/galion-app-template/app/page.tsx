import { Mic, Zap, Shield, Globe } from 'lucide-react'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-indigo-600 rounded-full">
              <Mic className="h-12 w-12 text-white" />
            </div>
          </div>
          <h1 className="text-5xl font-bold text-gray-900">
            Galion App
          </h1>
          <p className="text-xl text-gray-600">
            Voice-First Application Platform
          </p>
        </div>

        {/* Status Card */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-gray-800">
              System Status
            </h2>
            <span className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 rounded-full font-medium">
              <span className="h-2 w-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
              Online
            </span>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="flex flex-col items-center p-4 bg-blue-50 rounded-lg">
              <Zap className="h-8 w-8 text-blue-600 mb-2" />
              <h3 className="font-semibold text-gray-800">Fast</h3>
              <p className="text-sm text-gray-600 text-center mt-1">
                Lightning-fast voice processing
              </p>
            </div>

            <div className="flex flex-col items-center p-4 bg-purple-50 rounded-lg">
              <Shield className="h-8 w-8 text-purple-600 mb-2" />
              <h3 className="font-semibold text-gray-800">Secure</h3>
              <p className="text-sm text-gray-600 text-center mt-1">
                Enterprise-grade security
              </p>
            </div>

            <div className="flex flex-col items-center p-4 bg-green-50 rounded-lg">
              <Globe className="h-8 w-8 text-green-600 mb-2" />
              <h3 className="font-semibold text-gray-800">Global</h3>
              <p className="text-sm text-gray-600 text-center mt-1">
                Available worldwide
              </p>
            </div>
          </div>
        </div>

        {/* Info */}
        <div className="text-center text-sm text-gray-500">
          <p>Service is running successfully</p>
          <p className="mt-2">Version 1.0.0 • Port 3000</p>
        </div>
      </div>
    </main>
  )
}

