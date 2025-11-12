"use client"

import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Mic, MicOff, Loader2 } from 'lucide-react'
import { useVoiceStore } from '@/lib/stores/voice'
import { voiceApi, handleApiError } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import { cn } from '@/lib/utils'

interface VoiceButtonProps {
  onTranscript?: (text: string) => void
  onCommand?: (response: any) => void
  className?: string
}

export function VoiceButton({ onTranscript, onCommand, className }: VoiceButtonProps) {
  const { isRecording, isProcessing, setRecording, setProcessing, setTranscript, setError } = useVoiceStore()
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const audioChunks = useRef<Blob[]>([])
  const { toast } = useToast()

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      
      audioChunks.current = []

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data)
        }
      }

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' })
        await processAudio(audioBlob)
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      recorder.start()
      setMediaRecorder(recorder)
      setRecording(true)
      setError(null)
    } catch (error) {
      toast({
        title: 'Microphone access denied',
        description: 'Please allow microphone access to use voice features',
        variant: 'destructive',
      })
      setError('Microphone access denied')
    }
  }

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
      setRecording(false)
    }
  }

  const processAudio = async (audioBlob: Blob) => {
    setProcessing(true)
    
    try {
      // Convert speech to text
      const sttResponse = await voiceApi.speechToText(audioBlob)
      setTranscript(sttResponse.text)

      if (onTranscript) {
        onTranscript(sttResponse.text)
      }

      // Process as command if handler provided
      if (onCommand && sttResponse.text) {
        const commandResponse = await voiceApi.processCommand(sttResponse.text)
        onCommand(commandResponse)
        
        toast({
          title: 'Voice command processed',
          description: commandResponse.response,
        })
      } else {
        toast({
          title: 'Transcription complete',
          description: sttResponse.text,
        })
      }
    } catch (error) {
      const errorMessage = handleApiError(error)
      setError(errorMessage)
      toast({
        title: 'Voice processing failed',
        description: errorMessage,
        variant: 'destructive',
      })
    } finally {
      setProcessing(false)
    }
  }

  const handleClick = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  return (
    <Button
      size="icon"
      variant={isRecording ? "destructive" : "default"}
      onClick={handleClick}
      disabled={isProcessing}
      className={cn(
        "relative",
        isRecording && "animate-pulse",
        className
      )}
    >
      {isProcessing ? (
        <Loader2 className="h-5 w-5 animate-spin" />
      ) : isRecording ? (
        <MicOff className="h-5 w-5" />
      ) : (
        <Mic className="h-5 w-5" />
      )}
      
      {isRecording && (
        <span className="absolute -top-1 -right-1 h-3 w-3 rounded-full bg-red-500 animate-ping" />
      )}
    </Button>
  )
}

