/**
 * Voice Recorder Component
 * Records audio from microphone and sends to STT API
 */

'use client'

import { useState, useRef, useEffect } from 'react'
import { Mic, MicOff, Square, Upload } from 'lucide-react'

interface VoiceRecorderProps {
  onTranscript: (text: string) => void
  onError?: (error: string) => void
}

export default function VoiceRecorder({ onTranscript, onError }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animationFrameRef = useRef<number>()
  
  useEffect(() => {
    return () => {
      // Cleanup on unmount
      stopRecording()
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [])
  
  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Setup audio analyzer for visualization
      const audioContext = new AudioContext()
      const analyser = audioContext.createAnalyser()
      const source = audioContext.createMediaStreamSource(stream)
      source.connect(analyser)
      analyser.fftSize = 256
      analyserRef.current = analyser
      
      // Start visualizing audio level
      visualizeAudioLevel()
      
      // Setup media recorder
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }
      
      mediaRecorder.onstop = async () => {
        // Stop audio level visualization
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current)
        }
        
        // Create audio blob
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        
        // Send to API
        await sendToSTT(audioBlob)
        
        // Cleanup
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorder.start()
      setIsRecording(true)
      
    } catch (error) {
      console.error('Failed to start recording:', error)
      if (onError) {
        onError('Microphone access denied or unavailable')
      }
    }
  }
  
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setAudioLevel(0)
    }
  }
  
  const visualizeAudioLevel = () => {
    if (!analyserRef.current) return
    
    const analyser = analyserRef.current
    const dataArray = new Uint8Array(analyser.frequencyBinCount)
    
    const update = () => {
      analyser.getByteFrequencyData(dataArray)
      
      // Calculate average volume
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length
      setAudioLevel(average / 255)
      
      animationFrameRef.current = requestAnimationFrame(update)
    }
    
    update()
  }
  
  const sendToSTT = async (audioBlob: Blob) => {
    setIsProcessing(true)
    
    try {
      // Create form data
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')
      
      // Send to API
      const response = await fetch('/api/v2/voice/stt', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error('Transcription failed')
      }
      
      const data = await response.json()
      
      // Return transcript
      if (data.text) {
        onTranscript(data.text)
      }
      
    } catch (error) {
      console.error('STT failed:', error)
      if (onError) {
        onError('Speech recognition failed. Please try again.')
      }
    } finally {
      setIsProcessing(false)
    }
  }
  
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    
    if (!file.type.startsWith('audio/')) {
      if (onError) {
        onError('Please select an audio file')
      }
      return
    }
    
    setIsProcessing(true)
    
    try {
      const formData = new FormData()
      formData.append('audio', file)
      
      const response = await fetch('/api/v2/voice/stt', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error('Transcription failed')
      }
      
      const data = await response.json()
      
      if (data.text) {
        onTranscript(data.text)
      }
      
    } catch (error) {
      console.error('STT failed:', error)
      if (onError) {
        onError('Failed to transcribe audio file')
      }
    } finally {
      setIsProcessing(false)
    }
  }
  
  return (
    <div className="flex flex-col items-center gap-4 p-6 bg-zinc-900 rounded-lg border border-zinc-800">
      <div className="relative">
        {/* Recording Button */}
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${
            isRecording
              ? 'bg-red-600 hover:bg-red-700 animate-pulse'
              : 'bg-blue-600 hover:bg-blue-700'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isRecording ? (
            <Square size={32} className="text-white" />
          ) : (
            <Mic size={32} className="text-white" />
          )}
        </button>
        
        {/* Audio Level Indicator */}
        {isRecording && (
          <div
            className="absolute inset-0 rounded-full border-4 border-red-400 opacity-50"
            style={{
              transform: `scale(${1 + audioLevel * 0.5})`,
              transition: 'transform 0.1s ease-out'
            }}
          />
        )}
      </div>
      
      {/* Status Text */}
      <div className="text-center">
        {isRecording && (
          <p className="text-red-400 font-semibold animate-pulse">
            Recording... Click to stop
          </p>
        )}
        {isProcessing && (
          <p className="text-blue-400 font-semibold">
            Processing speech...
          </p>
        )}
        {!isRecording && !isProcessing && (
          <p className="text-zinc-400">
            Click to start recording
          </p>
        )}
      </div>
      
      {/* Upload Option */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-zinc-500">or</span>
        <label className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg cursor-pointer transition">
          <Upload size={16} />
          <span className="text-sm">Upload Audio</span>
          <input
            type="file"
            accept="audio/*"
            onChange={handleFileUpload}
            className="hidden"
            disabled={isProcessing || isRecording}
          />
        </label>
      </div>
    </div>
  )
}

