/**
 * Loading Components
 * Reusable loading states for better UX
 * Optimized for fast perceived performance
 */

export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-3'
  }
  
  return (
    <div className={`${sizeClasses[size]} border-purple-600 border-t-transparent 
                     rounded-full animate-spin`}
    />
  )
}

export function LoadingDots() {
  return (
    <div className="flex gap-1">
      <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
      <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
      <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
    </div>
  )
}

export function LoadingPage({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 
                    flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-zinc-400">{message}</p>
      </div>
    </div>
  )
}

export function LoadingSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`bg-zinc-800 animate-pulse rounded ${className}`} />
  )
}

// Skeleton for content cards
export function ContentSkeleton() {
  return (
    <div className="bg-zinc-900 p-6 rounded-lg border border-zinc-800">
      <LoadingSkeleton className="h-6 w-1/3 mb-4" />
      <LoadingSkeleton className="h-4 w-full mb-2" />
      <LoadingSkeleton className="h-4 w-2/3" />
    </div>
  )
}

// Skeleton for table rows
export function TableRowSkeleton() {
  return (
    <tr>
      <td className="px-4 py-3">
        <LoadingSkeleton className="h-4 w-full" />
      </td>
      <td className="px-4 py-3">
        <LoadingSkeleton className="h-4 w-full" />
      </td>
      <td className="px-4 py-3">
        <LoadingSkeleton className="h-4 w-full" />
      </td>
    </tr>
  )
}

