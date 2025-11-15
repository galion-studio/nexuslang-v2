'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface EnhancedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  loading?: boolean
  icon?: React.ReactNode
  glow?: boolean
  animated?: boolean
}

export const EnhancedButton: React.FC<EnhancedButtonProps> = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  glow = false,
  animated = true,
  disabled,
  ...props
}) => {
  const baseClasses = 'relative inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'

  const variants = {
    primary: 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white shadow-lg hover:shadow-xl focus:ring-blue-500',
    secondary: 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg hover:shadow-xl focus:ring-purple-500',
    outline: 'border-2 border-blue-500 text-blue-600 hover:bg-blue-50 focus:ring-blue-500 dark:border-blue-400 dark:text-blue-400 dark:hover:bg-blue-950',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500 dark:text-gray-300 dark:hover:bg-gray-800',
    danger: 'bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white shadow-lg hover:shadow-xl focus:ring-red-500'
  }

  const sizes = {
    sm: 'px-3 py-1.5 text-sm rounded-md',
    md: 'px-4 py-2 text-base rounded-lg',
    lg: 'px-6 py-3 text-lg rounded-lg',
    xl: 'px-8 py-4 text-xl rounded-xl'
  }

  const buttonClasses = cn(
    baseClasses,
    variants[variant],
    sizes[size],
    glow && variant === 'primary' && 'shadow-blue-500/25 shadow-2xl',
    animated && 'transform hover:scale-105 active:scale-95',
    className
  )

  return (
    <motion.button
      className={buttonClasses}
      disabled={disabled || loading}
      whileHover={animated ? { scale: 1.02 } : undefined}
      whileTap={animated ? { scale: 0.98 } : undefined}
      initial={animated ? { opacity: 0, y: 20 } : undefined}
      animate={animated ? { opacity: 1, y: 0 } : undefined}
      transition={{ duration: 0.2 }}
      {...props}
    >
      {loading && (
        <motion.div
          className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
      )}

      {icon && !loading && (
        <span className="mr-2">{icon}</span>
      )}

      <span className="relative z-10">{children}</span>

      {glow && variant === 'primary' && (
        <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-600 opacity-0 blur-xl transition-opacity group-hover:opacity-30" />
      )}
    </motion.button>
  )
}
