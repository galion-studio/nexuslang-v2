/**
 * Error Message Component
 * Displays error messages with consistent styling
 */

import { AlertCircle, X } from 'lucide-react'

interface ErrorMessageProps {
  message: string
  onDismiss?: () => void
  className?: string
}

export default function ErrorMessage({ message, onDismiss, className = '' }: ErrorMessageProps) {
  return (
    <div className={`flex items-start gap-3 p-4 bg-red-900/20 border border-red-800 rounded-lg ${className}`}>
      <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
      <p className="flex-1 text-red-200 text-sm">{message}</p>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-400 hover:text-red-300 transition flex-shrink-0"
          aria-label="Dismiss"
        >
          <X size={18} />
        </button>
      )}
    </div>
  )
}

