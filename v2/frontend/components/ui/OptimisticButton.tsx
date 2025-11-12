/**
 * Optimistic Button
 * Provides instant feedback for better perceived performance
 * Implements Musk principle: Accelerate cycle time with instant UI feedback
 */

'use client'

import { useState } from 'react'
import { Check } from 'lucide-react'

interface OptimisticButtonProps {
  onClick: () => Promise<void>
  children: React.ReactNode
  className?: string
  successMessage?: string
  disabled?: boolean
}

export default function OptimisticButton({
  onClick,
  children,
  className = '',
  successMessage = 'Done!',
  disabled = false
}: OptimisticButtonProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  
  const handleClick = async () => {
    if (isLoading || disabled) return
    
    setIsLoading(true)
    
    try {
      await onClick()
      
      // Show success state
      setShowSuccess(true)
      setTimeout(() => setShowSuccess(false), 2000)
    } catch (error) {
      console.error('Action failed:', error)
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <button
      onClick={handleClick}
      disabled={disabled || isLoading}
      className={`relative transition-all duration-200 ${className} ${
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      }`}
    >
      {/* Loading state */}
      {isLoading && (
        <span className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          <span>Processing...</span>
        </span>
      )}
      
      {/* Success state */}
      {showSuccess && !isLoading && (
        <span className="flex items-center gap-2">
          <Check size={16} />
          <span>{successMessage}</span>
        </span>
      )}
      
      {/* Default state */}
      {!isLoading && !showSuccess && children}
    </button>
  )
}

