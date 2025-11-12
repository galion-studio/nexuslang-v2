/**
 * Voice Player Component
 * Synthesizes and plays text-to-speech audio
 */

'use client'

import { useState } from 'react'
import { Play, Volume2, VolumeX, Settings } from 'lucide-react'

interface VoicePlayerProps {
  text: string
  onPlay?: () => void
  onError?: (error: string) => void
  autoPlay?: boolean
}

export default function VoicePlayer({ text, onPlay, onError, autoPlay = false }: VoicePlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isSynthesizing, setIsSynthesizing] = useState(false)
  const [voiceId, setVoiceId] = useState('default')
  const [emotion, setEmotion] = useState('neutral')
  const [speed, setSpeed] = useState(1.0)
  const [showSettings, setShowSettings] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  
  const emotions = ['neutral', 'happy', 'excited', 'sad', 'calm', 'thoughtful', 'friendly', 'professional']
  
  const synthesizeAndPlay = async () => {
    if (!text.trim()) {
      if (onError) {
        onError('No text to synthesize')
      }
      return
    }
    
    setIsSynthesizing(true)
    
    try {
      // Send TTS request
      const response = await fetch('/api/v2/voice/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          voice_id: voiceId,
          emotion,
          speed,
          language: 'en'
        }),
      })
      
      if (!response.ok) {
        throw new Error('Speech synthesis failed')
      }
      
      const data = await response.json()
      
      // Decode base64 audio
      if (data.audio_base64) {
        const audioData = atob(data.audio_base64)
        const arrayBuffer = new ArrayBuffer(audioData.length)
        const view = new Uint8Array(arrayBuffer)
        
        for (let i = 0; i < audioData.length; i++) {
          view[i] = audioData.charCodeAt(i)
        }
        
        const blob = new Blob([arrayBuffer], { type: 'audio/wav' })
        const url = URL.createObjectURL(blob)
        setAudioUrl(url)
        
        // Play audio
        const audio = new Audio(url)
        
        audio.onplay = () => {
          setIsPlaying(true)
          if (onPlay) {
            onPlay()
          }
        }
        
        audio.onended = () => {
          setIsPlaying(false)
          URL.revokeObjectURL(url)
          setAudioUrl(null)
        }
        
        audio.onerror = () => {
          setIsPlaying(false)
          if (onError) {
            onError('Failed to play audio')
          }
        }
        
        await audio.play()
      }
      
    } catch (error) {
      console.error('TTS failed:', error)
      if (onError) {
        onError('Speech synthesis failed. Please try again.')
      }
    } finally {
      setIsSynthesizing(false)
    }
  }
  
  const downloadAudio = async () => {
    if (!audioUrl) {
      await synthesizeAndPlay()
      return
    }
    
    // Download the audio file
    const a = document.createElement('a')
    a.href = audioUrl
    a.download = 'speech.wav'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }
  
  return (
    <div className="flex flex-col gap-4 p-6 bg-zinc-900 rounded-lg border border-zinc-800">
      {/* Main Controls */}
      <div className="flex items-center gap-4">
        {/* Play Button */}
        <button
          onClick={synthesizeAndPlay}
          disabled={isSynthesizing || isPlaying || !text.trim()}
          className="w-16 h-16 rounded-full bg-blue-600 hover:bg-blue-700 flex items-center justify-center transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSynthesizing ? (
            <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Play size={24} className="text-white ml-1" />
          )}
        </button>
        
        {/* Info */}
        <div className="flex-1">
          <p className="text-sm text-zinc-400">
            {isSynthesizing && 'Synthesizing speech...'}
            {isPlaying && '🔊 Playing'}
            {!isSynthesizing && !isPlaying && text.trim() ? 'Click to hear' : !text.trim() ? 'Enter text to synthesize' : ''}
          </p>
          <p className="text-xs text-zinc-500 mt-1">
            Voice: {voiceId} • Emotion: {emotion} • Speed: {speed}x
          </p>
        </div>
        
        {/* Settings Button */}
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="p-2 hover:bg-zinc-800 rounded-lg transition"
          title="Voice Settings"
        >
          <Settings size={20} className="text-zinc-400" />
        </button>
      </div>
      
      {/* Settings Panel */}
      {showSettings && (
        <div className="space-y-4 pt-4 border-t border-zinc-800">
          {/* Emotion Selector */}
          <div>
            <label className="block text-sm font-semibold text-zinc-300 mb-2">
              Emotion
            </label>
            <div className="flex flex-wrap gap-2">
              {emotions.map((e) => (
                <button
                  key={e}
                  onClick={() => setEmotion(e)}
                  className={`px-3 py-1 rounded text-sm transition ${
                    emotion === e
                      ? 'bg-purple-600 text-white'
                      : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                  }`}
                >
                  {e}
                </button>
              ))}
            </div>
          </div>
          
          {/* Speed Slider */}
          <div>
            <label className="block text-sm font-semibold text-zinc-300 mb-2">
              Speech Speed: {speed}x
            </label>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
              className="w-full h-2 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <div className="flex justify-between text-xs text-zinc-500 mt-1">
              <span>Slow (0.5x)</span>
              <span>Normal (1.0x)</span>
              <span>Fast (2.0x)</span>
            </div>
          </div>
          
          {/* Voice Selector - Placeholder for future voices */}
          <div>
            <label className="block text-sm font-semibold text-zinc-300 mb-2">
              Voice
            </label>
            <select
              value={voiceId}
              onChange={(e) => setVoiceId(e.target.value)}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded text-zinc-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="default">Default Voice</option>
              <option value="male-1">Male Voice 1</option>
              <option value="female-1">Female Voice 1</option>
            </select>
          </div>
        </div>
      )}
      
      {/* Download Button */}
      {audioUrl && (
        <button
          onClick={downloadAudio}
          className="text-sm text-blue-400 hover:text-blue-300 transition"
        >
          ⬇️ Download Audio
        </button>
      )}
    </div>
  )
}

