"use client"

import { useState, useRef, useEffect } from 'react'
import { Mic, MicOff, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { galionAPI } from '@/lib/api-client'

interface VoiceButtonProps {
  onTranscript?: (transcript: string) => void
  onCommand?: (response: any) => void
  className?: string
  disabled?: boolean
}

export function VoiceButton({ onTranscript, onCommand, className, disabled }: VoiceButtonProps) {
  const [isListening, setIsListening] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [transcript, setTranscript] = useState('')
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  useEffect(() => {
    // Initialize speech recognition
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const recognition = new webkitSpeechRecognition()
      recognition.continuous = false
      recognition.interimResults = true
      recognition.lang = 'en-US'

      recognition.onstart = () => {
        setIsListening(true)
        setTranscript('')
      }

      recognition.onresult = (event) => {
        let finalTranscript = ''
        let interimTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i]
          if (result.isFinal) {
            finalTranscript += result[0].transcript
          } else {
            interimTranscript += result[0].transcript
          }
        }

        const currentTranscript = finalTranscript || interimTranscript
        setTranscript(currentTranscript)

        if (finalTranscript) {
          handleVoiceCommand(finalTranscript)
        }
      }

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        setIsProcessing(false)
      }

      recognition.onend = () => {
        setIsListening(false)
      }

      recognitionRef.current = recognition
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const handleVoiceCommand = async (command: string) => {
    setIsProcessing(true)

    try {
      // Call the voice API
      const response = await galionAPI.sendVoiceCommand(command)
      onCommand?.(response)
    } catch (error) {
      console.error('Voice command failed:', error)
      onCommand?.({ error: 'Failed to process voice command' })
    } finally {
      setIsProcessing(false)
      setTranscript('')
    }
  }

  const toggleListening = async () => {
    if (disabled) return

    if (isListening) {
      recognitionRef.current?.stop()
      setIsListening(false)
      return
    }

    try {
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      // Start speech recognition
      recognitionRef.current?.start()
    } catch (error) {
      console.error('Microphone access denied:', error)
      alert('Microphone access is required for voice commands')
    }
  }

  const getButtonState = () => {
    if (disabled) return 'disabled'
    if (isProcessing) return 'processing'
    if (isListening) return 'listening'
    return 'idle'
  }

  const buttonState = getButtonState()

  const getButtonStyles = () => {
    switch (buttonState) {
      case 'listening':
        return 'bg-red-600 hover:bg-red-700 animate-pulse'
      case 'processing':
        return 'bg-yellow-600 hover:bg-yellow-700'
      case 'disabled':
        return 'bg-gray-600 cursor-not-allowed'
      default:
        return 'bg-blue-600 hover:bg-blue-700'
    }
  }

  const getIcon = () => {
    switch (buttonState) {
      case 'listening':
        return <Mic className="h-8 w-8" />
      case 'processing':
        return <Loader2 className="h-8 w-8 animate-spin" />
      default:
        return <MicOff className="h-8 w-8" />
    }
  }

  return (
    <div className="flex flex-col items-center space-y-4">
      <button
        onClick={toggleListening}
        disabled={disabled || isProcessing}
        className={cn(
          "rounded-full p-6 text-white transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50",
          getButtonStyles(),
          className
        )}
      >
        {getIcon()}
      </button>

      <div className="text-center">
        <p className="text-sm font-medium">
          {buttonState === 'listening' && 'Listening...'}
          {buttonState === 'processing' && 'Processing...'}
          {buttonState === 'idle' && 'Click to speak'}
          {buttonState === 'disabled' && 'Voice unavailable'}
        </p>

        {transcript && (
          <p className="text-xs text-muted-foreground mt-1 max-w-xs truncate">
            "{transcript}"
          </p>
        )}
      </div>
    </div>
  )
}
