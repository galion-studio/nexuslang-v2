/**
 * Success Message Component
 * Displays success messages with consistent styling
 */

import { CheckCircle, X } from 'lucide-react'

interface SuccessMessageProps {
  message: string
  onDismiss?: () => void
  className?: string
}

export default function SuccessMessage({ message, onDismiss, className = '' }: SuccessMessageProps) {
  return (
    <div className={`flex items-start gap-3 p-4 bg-green-900/20 border border-green-800 rounded-lg ${className}`}>
      <CheckCircle className="text-green-400 flex-shrink-0 mt-0.5" size={20} />
      <p className="flex-1 text-green-200 text-sm">{message}</p>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-green-400 hover:text-green-300 transition flex-shrink-0"
          aria-label="Dismiss"
        >
          <X size={18} />
        </button>
      )}
    </div>
  )
}

