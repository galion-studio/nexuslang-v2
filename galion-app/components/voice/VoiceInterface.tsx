'use client'

import { useState, useEffect, useRef } from 'react'
import { Mic, MicOff, Volume2, VolumeX, Settings } from 'lucide-react'
import { VoiceButton } from '../../shared/components/ui/VoiceButton'
import { VoiceWaveform } from './VoiceWaveform'
import { voiceProcessor } from '../../lib/voice/voice-processor'
import { sttService } from '../../lib/voice/stt-service'
import { ttsService } from '../../lib/voice/tts-service'

interface VoiceInterfaceProps {
  className?: string
  onTranscription?: (text: string, isFinal: boolean) => void
  onStateChange?: (isListening: boolean, isProcessing: boolean) => void
  autoStart?: boolean
}

export function VoiceInterface({
  className = '',
  onTranscription,
  onStateChange,
  autoStart = false
}: VoiceInterfaceProps) {
  const [isListening, setIsListening] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [transcription, setTranscription] = useState('')
  const [audioLevel, setAudioLevel] = useState(0)
  const [isInitialized, setIsInitialized] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const initializationRef = useRef(false)

  useEffect(() => {
    if (initializationRef.current) return
    initializationRef.current = true

    initializeVoiceServices()
  }, [])

  useEffect(() => {
    onStateChange?.(isListening, isProcessing)
  }, [isListening, isProcessing, onStateChange])

  const initializeVoiceServices = async () => {
    try {
      setError(null)

      // Initialize voice processor
      await voiceProcessor.initialize()

      // Initialize STT service
      await sttService.initialize()

      // Initialize TTS service
      await ttsService.initialize()

      // Set up callbacks
      voiceProcessor.setCallbacks({
        onStateChange: (state) => {
          setIsListening(state.isListening)
          setIsProcessing(state.isProcessing)
        },
        onAudioLevel: setAudioLevel,
        onError: (error) => {
          console.error('Voice processor error:', error)
          setError(error.message)
        }
      })

      sttService.setCallbacks({
        onResult: (result) => {
          setTranscription(result.text)
          onTranscription?.(result.text, result.isFinal)

          // Auto-stop if we get final result and no speech detected
          if (result.isFinal && !voiceProcessor.isVoiceActivity()) {
            stopListening()
          }
        },
        onError: (error) => {
          console.error('STT error:', error)
          setError(`Speech recognition error: ${error.message}`)
        }
      })

      ttsService.setCallbacks({
        onStart: () => setIsProcessing(true),
        onEnd: () => setIsProcessing(false),
        onError: (error) => {
          console.error('TTS error:', error)
          setError(`Text-to-speech error: ${error.message}`)
        }
      })

      setIsInitialized(true)

      // Auto-start if requested
      if (autoStart) {
        setTimeout(() => startListening(), 1000)
      }

    } catch (error) {
      console.error('Failed to initialize voice services:', error)
      setError('Failed to initialize voice services. Please check your microphone permissions.')
    }
  }

  const startListening = async () => {
    if (!isInitialized) {
      setError('Voice services not initialized')
      return
    }

    try {
      setError(null)
      await voiceProcessor.startListening()
      await sttService.startListening()
    } catch (error) {
      console.error('Failed to start listening:', error)
      setError('Failed to start voice recognition. Please check your microphone.')
    }
  }

  const stopListening = async () => {
    try {
      await voiceProcessor.stopListening()
      await sttService.stopListening()
    } catch (error) {
      console.error('Failed to stop listening:', error)
    }
  }

  const toggleListening = async () => {
    if (isListening) {
      await stopListening()
    } else {
      await startListening()
    }
  }

  const clearTranscription = () => {
    setTranscription('')
  }

  const speakText = async (text: string) => {
    try {
      setIsProcessing(true)
      await ttsService.speak(text)
    } catch (error) {
      console.error('Failed to speak text:', error)
      setError('Failed to generate speech')
    }
  }

  if (!isInitialized) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing voice services...</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`flex flex-col items-center space-y-6 p-6 ${className}`}>
      {/* Header with slogan */}
      <div className="text-center mb-4">
        <h2 className="text-2xl font-semibold text-primary italic">
          "Your imagination is the end."
        </h2>
      </div>

      {/* Voice Button */}
      <div className="relative">
        <VoiceButton
          platform="galion-app"
          size="large"
          isListening={isListening}
          isProcessing={isProcessing}
          onClick={toggleListening}
          disabled={!isInitialized}
          className="w-24 h-24"
        />

        {/* Voice status indicator */}
        <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
          <div className={`w-3 h-3 rounded-full ${
            isListening ? 'bg-green-500 animate-pulse' :
            isProcessing ? 'bg-blue-500 animate-pulse' :
            'bg-gray-400'
          }`} />
        </div>
      </div>

      {/* Waveform Visualization */}
      <VoiceWaveform
        isActive={isListening}
        audioLevel={audioLevel}
        className="w-full max-w-md h-16"
      />

      {/* Status Text */}
      <div className="text-center min-h-[2rem]">
        <p className={`text-sm ${
          isListening ? 'text-green-600 font-medium' :
          isProcessing ? 'text-blue-600 font-medium' :
          error ? 'text-red-600' :
          'text-gray-500'
        }`}>
          {error ||
           (isListening ? 'Listening...' :
            isProcessing ? 'Processing...' :
            'Tap to speak')}
        </p>
      </div>

      {/* Transcription Display */}
      {transcription && (
        <div className="w-full max-w-lg bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <div className="flex items-start justify-between mb-2">
            <span className="text-xs text-gray-500 uppercase tracking-wide">Transcription</span>
            <button
              onClick={clearTranscription}
              className="text-xs text-gray-400 hover:text-gray-600"
            >
              Clear
            </button>
          </div>
          <p className="text-gray-800 leading-relaxed">{transcription}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex space-x-3">
        <button
          onClick={() => speakText("Hello! How can I help you today?")}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50"
          disabled={isListening || isProcessing}
        >
          <Volume2 size={16} />
          <span>Test Speech</span>
        </button>

        <button
          onClick={clearTranscription}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
        >
          <MicOff size={16} />
          <span>Clear</span>
        </button>
      </div>

      {/* Settings */}
      <div className="absolute top-4 right-4">
        <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
          <Settings size={20} />
        </button>
      </div>
    </div>
  )
}