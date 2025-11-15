'use client'

import React from 'react'
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { trackError } from '@/lib/analytics'

interface Props {
  children: React.ReactNode
  fallback?: React.ComponentType<{ error: Error; resetError: () => void }>
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({
      error,
      errorInfo
    })

    // Log error to analytics
    trackError(error, {
      componentStack: errorInfo.componentStack,
      errorBoundary: true,
      platform: 'galion-app'
    })

    // In production, send to error reporting service
    console.error('Error Boundary caught an error:', error, errorInfo)
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback
        return <FallbackComponent error={this.state.error!} resetError={this.resetError} />
      }

      return <ErrorFallback error={this.state.error!} resetError={this.resetError} />
    }

    return this.props.children
  }
}

interface ErrorFallbackProps {
  error: Error
  resetError: () => void
}

export const ErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetError }) => {
  const handleReportError = () => {
    // In production, this would send error details to support
    console.log('Error reported:', error)
    alert('Error reported to our team. Thank you!')
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <View style={styles.iconContainer}>
          <AlertTriangle size={48} color="#ef4444" />
        </View>

        <Text style={styles.title}>Oops! Something went wrong</Text>
        <Text style={styles.description}>
          We encountered an unexpected error. Our team has been notified and is working to fix this issue.
        </Text>

        <ScrollView style={styles.errorDetails} showsVerticalScrollIndicator={false}>
          <Text style={styles.errorTitle}>Error Details:</Text>
          <Text style={styles.errorMessage}>{error.message}</Text>
          {__DEV__ && (
            <Text style={styles.errorStack}>{error.stack}</Text>
          )}
        </ScrollView>

        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.primaryButton} onPress={resetError}>
            <RefreshCw size={18} color="#ffffff" style={styles.buttonIcon} />
            <Text style={styles.primaryButtonText}>Try Again</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.secondaryButton} onPress={handleReportError}>
            <Text style={styles.secondaryButtonText}>Report Issue</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.homeButton} onPress={() => {
            // Navigate to home - in real app, use navigation
            console.log('Navigate to home')
          }}>
            <Home size={18} color="#6b7280" style={styles.buttonIcon} />
            <Text style={styles.homeButtonText}>Go Home</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  content: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 24,
    width: '100%',
    maxWidth: 400,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 8,
  },
  iconContainer: {
    marginBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    textAlign: 'center',
    marginBottom: 8,
  },
  description: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 20,
  },
  errorDetails: {
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    padding: 12,
    marginBottom: 20,
    maxHeight: 150,
    width: '100%',
  },
  errorTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  errorMessage: {
    fontSize: 14,
    color: '#ef4444',
    fontFamily: 'monospace',
    marginBottom: 8,
  },
  errorStack: {
    fontSize: 12,
    color: '#6b7280',
    fontFamily: 'monospace',
    lineHeight: 16,
  },
  buttonContainer: {
    width: '100%',
    gap: 12,
  },
  primaryButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
  },
  primaryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  secondaryButton: {
    backgroundColor: '#f3f4f6',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
    alignItems: 'center',
    width: '100%',
  },
  secondaryButtonText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '500',
  },
  homeButton: {
    backgroundColor: 'transparent',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
  },
  homeButtonText: {
    color: '#6b7280',
    fontSize: 16,
    fontWeight: '500',
  },
  buttonIcon: {
    marginRight: 8,
  },
})

// Web-specific Error Boundary
export const WebErrorBoundary: React.FC<Props> = ({ children, fallback }) => {
  return (
    <ErrorBoundary
      fallback={fallback || (({ error, resetError }) => (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertTriangle size={32} color="#ef4444" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Something went wrong
            </h2>
            <p className="text-gray-600 mb-4">
              We encountered an unexpected error. Please try refreshing the page.
            </p>
            <div className="space-y-2">
              <button
                onClick={resetError}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Try Again
              </button>
              <button
                onClick={() => window.location.href = '/'}
                className="w-full bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Go Home
              </button>
            </div>
          </div>
        </div>
      ))}
    >
      {children}
    </ErrorBoundary>
  )
}
