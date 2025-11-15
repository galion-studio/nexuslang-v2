'use client'

import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mic, MicOff, Volume2, VolumeX, Settings, Play, Pause, RotateCcw } from 'lucide-react'
import { EnhancedButton } from '@/components/ui/enhanced-button'
import { Card, CardContent } from '@/components/ui/card'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import toast from 'react-hot-toast'

interface VoiceAssistantProps {
  onVoiceCommand?: (command: string) => void
  onVoiceResponse?: (response: string) => void
  className?: string
}

interface VoiceSettings {
  voice: 'female' | 'male' | 'neutral'
  speed: number
  pitch: number
  volume: number
  autoSpeak: boolean
}

export const VoiceAssistant: React.FC<VoiceAssistantProps> = ({
  onVoiceCommand,
  onVoiceResponse,
  className
}) => {
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [currentTranscript, setCurrentTranscript] = useState('')
  const [lastResponse, setLastResponse] = useState('')
  const [settings, setSettings] = useState<VoiceSettings>({
    voice: 'female',
    speed: 1,
    pitch: 1,
    volume: 0.8,
    autoSpeak: true
  })
  const [showSettings, setShowSettings] = useState(false)
  const [conversationHistory, setConversationHistory] = useState<Array<{
    type: 'user' | 'ai'
    text: string
    timestamp: Date
  }>>([])

  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const synthRef = useRef<SpeechSynthesis | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)

  useEffect(() => {
    initializeVoiceFeatures()
    return () => {
      cleanupVoiceFeatures()
    }
  }, [])

  const initializeVoiceFeatures = () => {
    // Initialize speech recognition
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = 'en-US'

      recognitionRef.current.onstart = () => {
        setIsListening(true)
        toast.success('Listening... Speak your command')
      }

      recognitionRef.current.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('')

        setCurrentTranscript(transcript)

        if (event.results[0].isFinal) {
          handleVoiceCommand(transcript)
        }
      }

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        toast.error(`Voice recognition error: ${event.error}`)
      }

      recognitionRef.current.onend = () => {
        setIsListening(false)
        setCurrentTranscript('')
      }
    }

    // Initialize speech synthesis
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis
    }

    // Initialize audio context for visual feedback
    if (typeof window !== 'undefined' && 'AudioContext' in window) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
    }
  }

  const cleanupVoiceFeatures = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
    if (synthRef.current) {
      synthRef.current.cancel()
    }
    if (audioContextRef.current) {
      audioContextRef.current.close()
    }
  }

  const handleVoiceCommand = async (command: string) => {
    // Add to conversation history
    setConversationHistory(prev => [...prev, {
      type: 'user',
      text: command,
      timestamp: new Date()
    }])

    // Call parent handler
    onVoiceCommand?.(command)

    // Simulate AI processing and response
    setTimeout(() => {
      const response = generateAIResponse(command)
      setLastResponse(response)

      // Add AI response to history
      setConversationHistory(prev => [...prev, {
        type: 'ai',
        text: response,
        timestamp: new Date()
      }])

      onVoiceResponse?.(response)

      // Auto-speak if enabled
      if (settings.autoSpeak) {
        speakResponse(response)
      }
    }, 1000 + Math.random() * 2000) // Simulate processing time
  }

  const generateAIResponse = (command: string): string => {
    const responses = [
      "I understand you're asking about " + command + ". Let me help you with that.",
      "That's an interesting request. Here's what I can tell you about " + command,
      "Great question! Based on your command, I suggest the following approach.",
      "I see you want to know about " + command + ". Let me provide you with detailed information.",
      "Perfect! I'll help you with " + command + ". Here's what you need to know."
    ]

    return responses[Math.floor(Math.random() * responses.length)]
  }

  const speakResponse = (text: string) => {
    if (!synthRef.current) {
      toast.error('Speech synthesis not supported')
      return
    }

    setIsSpeaking(true)

    const utterance = new SpeechSynthesisUtterance(text)

    // Configure voice settings
    utterance.rate = settings.speed
    utterance.pitch = settings.pitch
    utterance.volume = settings.volume

    // Set voice
    const voices = synthRef.current.getVoices()
    const selectedVoice = voices.find(voice =>
      voice.name.toLowerCase().includes(settings.voice)
    ) || voices[0]

    if (selectedVoice) {
      utterance.voice = selectedVoice
    }

    utterance.onend = () => {
      setIsSpeaking(false)
    }

    utterance.onerror = () => {
      setIsSpeaking(false)
      toast.error('Speech synthesis failed')
    }

    synthRef.current.speak(utterance)
  }

  const toggleListening = () => {
    if (!recognitionRef.current) {
      toast.error('Speech recognition not supported in this browser')
      return
    }

    if (isListening) {
      recognitionRef.current.stop()
    } else {
      recognitionRef.current.start()
    }
  }

  const toggleSpeaking = () => {
    if (isSpeaking) {
      synthRef.current?.cancel()
      setIsSpeaking(false)
    } else if (lastResponse) {
      speakResponse(lastResponse)
    } else {
      toast.error('No response to speak')
    }
  }

  const playAudioFeedback = () => {
    if (audioContextRef.current) {
      const oscillator = audioContextRef.current.createOscillator()
      const gainNode = audioContextRef.current.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(audioContextRef.current.destination)

      oscillator.frequency.setValueAtTime(800, audioContextRef.current.currentTime)
      gainNode.gain.setValueAtTime(0.1, audioContextRef.current.currentTime)

      oscillator.start()
      oscillator.stop(audioContextRef.current.currentTime + 0.1)
    }
  }

  const clearHistory = () => {
    setConversationHistory([])
    setLastResponse('')
    setCurrentTranscript('')
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Main Voice Interface */}
      <Card className="relative overflow-hidden bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20 border-2">
        <CardContent className="p-8">
          {/* Animated Background */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-10 left-10 w-32 h-32 bg-blue-400 rounded-full blur-3xl animate-pulse" />
            <div className="absolute bottom-10 right-10 w-24 h-24 bg-cyan-400 rounded-full blur-2xl animate-pulse delay-1000" />
          </div>

          <div className="relative z-10">
            {/* Status Indicators */}
            <div className="flex items-center justify-center gap-4 mb-8">
              <AnimatePresence>
                {isListening && (
                  <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0, opacity: 0 }}
                    className="flex items-center gap-2"
                  >
                    <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                    <Badge variant="destructive" className="animate-pulse">
                      Listening...
                    </Badge>
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence>
                {isSpeaking && (
                  <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0, opacity: 0 }}
                    className="flex items-center gap-2"
                  >
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                    <Badge variant="secondary" className="animate-pulse">
                      Speaking...
                    </Badge>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Main Voice Button */}
            <div className="flex justify-center mb-8">
              <motion.div
                animate={isListening ? {
                  scale: [1, 1.1, 1],
                  boxShadow: [
                    '0 0 0 0 rgba(59, 130, 246, 0.7)',
                    '0 0 0 20px rgba(59, 130, 246, 0)',
                    '0 0 0 0 rgba(59, 130, 246, 0)'
                  ]
                } : {}}
                transition={{
                  duration: 1.5,
                  repeat: isListening ? Infinity : 0,
                  ease: 'easeInOut'
                }}
              >
                <EnhancedButton
                  size="xl"
                  variant={isListening ? "secondary" : "primary"}
                  glow={!isListening}
                  animated={false}
                  onClick={toggleListening}
                  className="w-24 h-24 rounded-full"
                  icon={isListening ? <MicOff className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
                />
              </motion.div>
            </div>

            {/* Transcript Display */}
            <AnimatePresence>
              {(currentTranscript || lastResponse) && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="text-center mb-6"
                >
                  {currentTranscript && (
                    <div className="mb-4">
                      <p className="text-sm text-muted-foreground mb-2">You said:</p>
                      <p className="text-lg font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/20 rounded-lg p-3">
                        "{currentTranscript}"
                      </p>
                    </div>
                  )}

                  {lastResponse && (
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">AI Response:</p>
                      <p className="text-lg font-medium text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-950/20 rounded-lg p-3">
                        "{lastResponse}"
                      </p>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Control Buttons */}
            <div className="flex justify-center gap-4 mb-6">
              <EnhancedButton
                variant="outline"
                size="md"
                onClick={toggleSpeaking}
                disabled={!lastResponse}
                icon={isSpeaking ? <Pause className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              >
                {isSpeaking ? 'Stop' : 'Speak Response'}
              </EnhancedButton>

              <EnhancedButton
                variant="outline"
                size="md"
                onClick={clearHistory}
                icon={<RotateCcw className="w-4 h-4" />}
              >
                Clear
              </EnhancedButton>

              <EnhancedButton
                variant="outline"
                size="md"
                onClick={() => setShowSettings(!showSettings)}
                icon={<Settings className="w-4 h-4" />}
              >
                Settings
              </EnhancedButton>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Voice Settings */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold mb-4">Voice Settings</h3>

                <div className="space-y-6">
                  {/* Voice Selection */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Voice</label>
                    <select
                      value={settings.voice}
                      onChange={(e) => setSettings(prev => ({ ...prev, voice: e.target.value as VoiceSettings['voice'] }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="female">Female</option>
                      <option value="male">Male</option>
                      <option value="neutral">Neutral</option>
                    </select>
                  </div>

                  {/* Speed Control */}
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Speed: {settings.speed.toFixed(1)}x
                    </label>
                    <Slider
                      value={[settings.speed]}
                      onValueChange={([value]) => setSettings(prev => ({ ...prev, speed: value }))}
                      min={0.5}
                      max={2}
                      step={0.1}
                      className="w-full"
                    />
                  </div>

                  {/* Pitch Control */}
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Pitch: {settings.pitch.toFixed(1)}
                    </label>
                    <Slider
                      value={[settings.pitch]}
                      onValueChange={([value]) => setSettings(prev => ({ ...prev, pitch: value }))}
                      min={0.5}
                      max={2}
                      step={0.1}
                      className="w-full"
                    />
                  </div>

                  {/* Volume Control */}
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Volume: {Math.round(settings.volume * 100)}%
                    </label>
                    <Slider
                      value={[settings.volume]}
                      onValueChange={([value]) => setSettings(prev => ({ ...prev, volume: value }))}
                      min={0}
                      max={1}
                      step={0.1}
                      className="w-full"
                    />
                  </div>

                  {/* Auto Speak Toggle */}
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium">Auto-speak responses</label>
                    <button
                      onClick={() => setSettings(prev => ({ ...prev, autoSpeak: !prev.autoSpeak }))}
                      className={cn(
                        "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                        settings.autoSpeak ? "bg-blue-600" : "bg-gray-200"
                      )}
                    >
                      <span
                        className={cn(
                          "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                          settings.autoSpeak ? "translate-x-6" : "translate-x-1"
                        )}
                      />
                    </button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Conversation History */}
      {conversationHistory.length > 0 && (
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">Conversation History</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {conversationHistory.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: message.type === 'user' ? -20 : 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={cn(
                    "flex gap-3 p-3 rounded-lg",
                    message.type === 'user'
                      ? "bg-blue-50 dark:bg-blue-950/20 ml-8"
                      : "bg-green-50 dark:bg-green-950/20 mr-8"
                  )}
                >
                  <div className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium",
                    message.type === 'user'
                      ? "bg-blue-100 text-blue-600"
                      : "bg-green-100 text-green-600"
                  )}>
                    {message.type === 'user' ? 'U' : 'AI'}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm">{message.text}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
