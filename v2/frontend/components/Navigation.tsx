'use client'

/**
 * Global Navigation Component
 * Simplified navigation with pricing and developer platform
 */

import Link from 'next/link'
import { useState, useEffect } from 'react'
import { Code, Zap, DollarSign, Menu, X } from 'lucide-react'

export default function Navigation() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  
  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token')
    setIsLoggedIn(!!token)
  }, [])
  
  const navItems = [
    { href: '/ide', label: 'IDE', icon: Code },
    { href: '/pricing', label: 'Pricing', icon: DollarSign },
    { href: '/developers', label: 'Developers', icon: Zap },
  ]
  
  return (
    <nav className="border-b border-zinc-800 bg-zinc-950/50 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            NexusLang
          </Link>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-zinc-400 hover:text-white transition font-medium flex items-center gap-2"
              >
                <item.icon size={18} />
                {item.label}
              </Link>
            ))}
            
            {isLoggedIn ? (
              <>
                <Link
                  href="/dashboard"
                  className="text-zinc-400 hover:text-white transition font-medium"
                >
                  Dashboard
                </Link>
                <button
                  onClick={() => {
                    localStorage.removeItem('access_token')
                    window.location.href = '/'
                  }}
                  className="px-5 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition font-semibold"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/auth/login"
                  className="text-zinc-400 hover:text-white transition font-medium"
                >
                  Login
                </Link>
                <Link
                  href="/auth/register"
                  className="px-5 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition font-semibold"
                >
                  Start Free
                </Link>
              </>
            )}
          </div>
          
          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden text-white"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
        
        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pb-4 space-y-3">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="block text-zinc-400 hover:text-white transition font-medium py-2"
                onClick={() => setIsMenuOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            {isLoggedIn ? (
              <>
                <Link
                  href="/dashboard"
                  className="block text-zinc-400 hover:text-white transition font-medium py-2"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Dashboard
                </Link>
                <button
                  onClick={() => {
                    localStorage.removeItem('access_token')
                    window.location.href = '/'
                    setIsMenuOpen(false)
                  }}
                  className="w-full px-5 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition font-semibold"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/auth/login"
                  className="block text-zinc-400 hover:text-white transition font-medium py-2"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Login
                </Link>
                <Link
                  href="/auth/register"
                  className="block px-5 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition font-semibold text-center"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Start Free
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}

