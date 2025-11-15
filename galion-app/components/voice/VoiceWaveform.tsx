'use client'

import { useEffect, useRef, useState } from 'react'

interface VoiceWaveformProps {
  isActive?: boolean
  audioLevel?: number
  color?: string
  backgroundColor?: string
  className?: string
  width?: number
  height?: number
  barCount?: number
}

export function VoiceWaveform({
  isActive = false,
  audioLevel = 0,
  color = '#3b82f6',
  backgroundColor = 'transparent',
  className = '',
  width,
  height = 60,
  barCount = 32
}: VoiceWaveformProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()
  const [bars, setBars] = useState<number[]>(new Array(barCount).fill(0))

  // Generate animated bars when active
  useEffect(() => {
    if (!isActive) {
      setBars(new Array(barCount).fill(0))
      return
    }

    const animate = () => {
      const newBars = bars.map((bar, index) => {
        // Base height from audio level
        const baseHeight = audioLevel * height

        // Add some randomness for visual effect
        const randomFactor = Math.random() * 0.3 + 0.7
        const waveFactor = Math.sin(Date.now() * 0.01 + index * 0.5) * 0.2 + 0.8

        return Math.max(2, baseHeight * randomFactor * waveFactor)
      })

      setBars(newBars)
      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isActive, audioLevel, height, barCount])

  // Draw waveform on canvas
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const rect = canvas.getBoundingClientRect()
    const canvasWidth = width || rect.width || 300
    const canvasHeight = height

    canvas.width = canvasWidth
    canvas.height = canvasHeight

    // Clear canvas
    ctx.fillStyle = backgroundColor
    ctx.fillRect(0, 0, canvasWidth, canvasHeight)

    if (!isActive) {
      // Draw static waveform when not active
      ctx.strokeStyle = color + '40' // Semi-transparent
      ctx.lineWidth = 2
      ctx.beginPath()

      const centerY = canvasHeight / 2
      const amplitude = 8

      for (let x = 0; x < canvasWidth; x += 4) {
        const y = centerY + Math.sin(x * 0.02) * amplitude * (1 - Math.abs(x - canvasWidth / 2) / (canvasWidth / 2))
        if (x === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      }

      ctx.stroke()
      return
    }

    // Draw active waveform
    const barWidth = (canvasWidth - (barCount - 1) * 2) / barCount
    const barSpacing = 2

    bars.forEach((barHeight, index) => {
      const x = index * (barWidth + barSpacing)
      const barTop = (canvasHeight - barHeight) / 2

      // Create gradient for 3D effect
      const gradient = ctx.createLinearGradient(0, barTop, 0, barTop + barHeight)
      gradient.addColorStop(0, color)
      gradient.addColorStop(0.5, color + '80')
      gradient.addColorStop(1, color + '40')

      ctx.fillStyle = gradient

      // Round rectangle for modern look
      const radius = Math.min(barWidth / 4, 2)
      ctx.beginPath()
      ctx.roundRect(x, barTop, barWidth, barHeight, radius)
      ctx.fill()

      // Add glow effect when audio level is high
      if (audioLevel > 0.7) {
        ctx.shadowColor = color
        ctx.shadowBlur = 8
        ctx.fill()
        ctx.shadowBlur = 0
      }
    })

    // Add frequency spectrum effect
    if (audioLevel > 0.3) {
      ctx.strokeStyle = color + '60'
      ctx.lineWidth = 1
      ctx.beginPath()

      bars.forEach((barHeight, index) => {
        const x = index * (barWidth + barSpacing) + barWidth / 2
        const y = (canvasHeight - barHeight) / 2

        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })

      ctx.stroke()
    }

  }, [bars, isActive, color, backgroundColor, width, height, barCount, audioLevel])

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <canvas
        ref={canvasRef}
        className="rounded-lg"
        style={{
          width: width || '100%',
          height: height,
          backgroundColor: backgroundColor !== 'transparent' ? backgroundColor : undefined
        }}
      />
    </div>
  )
}