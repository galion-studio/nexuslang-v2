'use client'

import * as React from 'react'
import { cn } from '../../../shared/utils/cn'
import { LoadingDots } from '../../../shared/components/ui/LoadingStates'

interface TranscriptionDisplayProps {
  transcript: string
  isActive?: boolean
  confidence?: number
  className?: string
}

/**
 * TranscriptionDisplay - Shows real-time speech-to-text transcription
 * Displays confidence levels and processing states
 */
export const TranscriptionDisplay: React.FC<TranscriptionDisplayProps> = ({
  transcript,
  isActive = false,
  confidence,
  className
}) => {
  const [displayText, setDisplayText] = React.useState('')
  const [isTyping, setIsTyping] = React.useState(false)

  // Animate text appearance
  React.useEffect(() => {
    if (!transcript) {
      setDisplayText('')
      setIsTyping(false)
      return
    }

    setIsTyping(true)

    // Simulate typing effect for real-time feel
    let currentText = ''
    const chars = transcript.split('')
    let index = 0

    const typeChar = () => {
      if (index < chars.length) {
        currentText += chars[index]
        setDisplayText(currentText)
        index++
        setTimeout(typeChar, 50) // Typing speed
      } else {
        setIsTyping(false)
      }
    }

    typeChar()
  }, [transcript])

  const getConfidenceColor = (conf: number) => {
    if (conf >= 0.9) return 'text-success'
    if (conf >= 0.7) return 'text-warning'
    return 'text-error'
  }

  const getConfidenceLabel = (conf: number) => {
    if (conf >= 0.9) return 'Excellent'
    if (conf >= 0.8) return 'Good'
    if (conf >= 0.7) return 'Fair'
    return 'Poor'
  }

  return (
    <div className={cn(
      "bg-surface border border-surface-hover rounded-xl p-6 transition-all duration-300",
      isActive && "border-primary shadow-lg",
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className={cn(
            "w-2 h-2 rounded-full",
            isActive ? "bg-accent animate-pulse" : "bg-text-muted"
          )} />
          <span className="text-sm font-medium text-text">
            {isActive ? 'Listening...' : 'Transcription'}
          </span>
        </div>

        {/* Confidence indicator */}
        {confidence !== undefined && (
          <div className="flex items-center gap-2">
            <span className={cn("text-xs", getConfidenceColor(confidence))}>
              {getConfidenceLabel(confidence)}
            </span>
            <div className="w-16 h-1 bg-surface-hover rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full transition-all duration-300",
                  confidence >= 0.9 ? "bg-success" :
                  confidence >= 0.7 ? "bg-warning" : "bg-error"
                )}
                style={{ width: `${confidence * 100}%` }}
              />
            </div>
            <span className="text-xs text-text-muted">
              {Math.round(confidence * 100)}%
            </span>
          </div>
        )}
      </div>

      {/* Transcription content */}
      <div className="min-h-[60px] flex items-center">
        {isActive && !transcript ? (
          <div className="flex items-center gap-3 text-text-muted">
            <LoadingDots size="sm" />
            <span className="text-sm">Waiting for speech...</span>
          </div>
        ) : transcript ? (
          <div className="w-full">
            <p className="text-text leading-relaxed">
              {displayText}
              {isTyping && <span className="animate-pulse">|</span>}
            </p>

            {/* Word count */}
            <div className="mt-2 text-xs text-text-muted">
              {displayText.split(' ').filter(word => word.length > 0).length} words
            </div>
          </div>
        ) : (
          <p className="text-text-muted italic">
            No transcription available
          </p>
        )}
      </div>

      {/* Processing indicator */}
      {isActive && transcript && (
        <div className="mt-4 flex items-center gap-2 text-xs text-text-muted">
          <div className="w-1 h-1 bg-accent rounded-full animate-ping" />
          <span>Processing speech...</span>
        </div>
      )}
    </div>
  )
}

export default TranscriptionDisplay
