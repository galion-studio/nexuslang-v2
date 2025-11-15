'use client'

import { useState, useEffect } from 'react'
import { Wifi, WifiOff, Mic, MicOff, Volume2, AlertCircle } from 'lucide-react'

interface VoiceStatusProps {
  isConnected?: boolean
  isListening?: boolean
  isProcessing?: boolean
  connectionQuality?: 'excellent' | 'good' | 'poor' | 'offline'
  lastActivity?: number
  error?: string | null
  className?: string
}

export function VoiceStatus({
  isConnected = false,
  isListening = false,
  isProcessing = false,
  connectionQuality = 'offline',
  lastActivity,
  error,
  className = ''
}: VoiceStatusProps) {
  const [timeSinceActivity, setTimeSinceActivity] = useState(0)

  useEffect(() => {
    if (!lastActivity) return

    const interval = setInterval(() => {
      setTimeSinceActivity(Date.now() - lastActivity)
    }, 1000)

    return () => clearInterval(interval)
  }, [lastActivity])

  const formatTime = (ms: number): string => {
    const seconds = Math.floor(ms / 1000)
    if (seconds < 60) return `${seconds}s ago`
    const minutes = Math.floor(seconds / 60)
    return `${minutes}m ago`
  }

  const getConnectionIcon = () => {
    if (!isConnected) return <WifiOff size={16} className="text-red-500" />

    switch (connectionQuality) {
      case 'excellent':
        return <Wifi size={16} className="text-green-500" />
      case 'good':
        return <Wifi size={16} className="text-yellow-500" />
      case 'poor':
        return <Wifi size={16} className="text-orange-500" />
      default:
        return <WifiOff size={16} className="text-red-500" />
    }
  }

  const getStatusColor = () => {
    if (error) return 'text-red-600 bg-red-50 border-red-200'
    if (isProcessing) return 'text-blue-600 bg-blue-50 border-blue-200'
    if (isListening) return 'text-green-600 bg-green-50 border-green-200'
    return 'text-gray-600 bg-gray-50 border-gray-200'
  }

  const getStatusText = () => {
    if (error) return 'Error'
    if (isProcessing) return 'Processing'
    if (isListening) return 'Listening'
    if (!isConnected) return 'Disconnected'
    return 'Ready'
  }

  const getStatusIcon = () => {
    if (error) return <AlertCircle size={16} />
    if (isProcessing) return <Volume2 size={16} />
    if (isListening) return <Mic size={16} />
    return <MicOff size={16} />
  }

  return (
    <div className={`inline-flex items-center space-x-3 px-3 py-2 rounded-lg border ${getStatusColor()} ${className}`}>
      {/* Status Icon */}
      <div className="flex items-center space-x-2">
        {getStatusIcon()}
        <span className="text-sm font-medium">{getStatusText()}</span>
      </div>

      {/* Connection Status */}
      <div className="flex items-center space-x-1">
        {getConnectionIcon()}
        <span className="text-xs">
          {connectionQuality === 'excellent' ? 'Excellent' :
           connectionQuality === 'good' ? 'Good' :
           connectionQuality === 'poor' ? 'Poor' : 'Offline'}
        </span>
      </div>

      {/* Activity Timestamp */}
      {lastActivity && (
        <div className="text-xs text-gray-500">
          {formatTime(timeSinceActivity)}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="ml-2 text-xs text-red-600 max-w-xs truncate" title={error}>
          {error}
        </div>
      )}
    </div>
  )
}

// Compact version for status bars
export function VoiceStatusCompact({
  isConnected = false,
  isListening = false,
  isProcessing = false,
  error = null,
  className = ''
}: Omit<VoiceStatusProps, 'connectionQuality' | 'lastActivity'>) {
  const getStatusIndicator = () => {
    if (error) return { color: 'bg-red-500', pulse: true }
    if (isProcessing) return { color: 'bg-blue-500', pulse: true }
    if (isListening) return { color: 'bg-green-500', pulse: true }
    if (isConnected) return { color: 'bg-gray-400', pulse: false }
    return { color: 'bg-red-400', pulse: false }
  }

  const { color, pulse } = getStatusIndicator()

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <div className={`w-2 h-2 rounded-full ${color} ${pulse ? 'animate-pulse' : ''}`} />
      <span className="text-xs text-gray-600">
        {error ? 'Error' :
         isProcessing ? 'Processing' :
         isListening ? 'Listening' :
         isConnected ? 'Connected' : 'Disconnected'}
      </span>
    </div>
  )
}