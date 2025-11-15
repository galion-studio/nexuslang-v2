import Link from 'next/link'
import { Mic, Home, CreditCard, User, LogOut, BarChart3, BookOpen, Code, Bot, Zap } from 'lucide-react'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-center h-16 px-4 border-b border-gray-200 dark:border-gray-700">
            <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Galion.app
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            <Link
              href="/dashboard"
              className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
            >
              <Home className="h-5 w-5 mr-3" />
              Dashboard
            </Link>

            <Link
              href="/voice"
              className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
            >
              <Mic className="h-5 w-5 mr-3" />
              Voice Assistant
            </Link>

            <Link
              href="/analytics"
              className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
            >
              <BarChart3 className="h-5 w-5 mr-3" />
              Analytics
            </Link>

            <Link
              href="/grokopedia"
              className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
            >
              <BookOpen className="h-5 w-5 mr-3" />
              Grokopedia
            </Link>

            <Link
              href="/billing"
              className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
            >
              <CreditCard className="h-5 w-5 mr-3" />
              Billing
            </Link>

            <Link
              href="/developers"
              className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
            >
              <Code className="h-5 w-5 mr-3" />
              API Docs
            </Link>

            <Link
              href="/ai-studio"
              className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
            >
              <Zap className="h-5 w-5 mr-3" />
              AI Studio
            </Link>

            <Link
              href="/agents"
              className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
            >
              <Bot className="h-5 w-5 mr-3" />
              Autonomous Agents
            </Link>

            <Link
              href="/profile"
              className="flex items-center px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
            >
              <User className="h-5 w-5 mr-3" />
              Profile
            </Link>
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <button className="flex items-center w-full px-4 py-3 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition">
              <LogOut className="h-5 w-5 mr-3" />
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64">
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
