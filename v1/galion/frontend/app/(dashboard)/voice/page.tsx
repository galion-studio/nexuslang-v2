"use client"

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { VoiceButton } from '@/components/voice/VoiceButton'
import { Mic, MessageSquare } from 'lucide-react'

export default function VoicePage() {
  const [transcript, setTranscript] = useState('')
  const [response, setResponse] = useState<any>(null)

  const handleTranscript = (text: string) => {
    setTranscript(text)
  }

  const handleCommand = (commandResponse: any) => {
    setResponse(commandResponse)
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Voice Commands</h1>
        <p className="text-muted-foreground">
          Use voice to interact with GALION.APP
        </p>
      </div>

      {/* Voice Interface */}
      <Card>
        <CardHeader>
          <CardTitle>Voice Input</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-col items-center justify-center p-12">
            <VoiceButton
              onTranscript={handleTranscript}
              onCommand={handleCommand}
              className="h-24 w-24"
            />
            <p className="text-sm text-muted-foreground mt-4">
              Click the microphone to start recording
            </p>
          </div>

          {transcript && (
            <div className="p-4 bg-muted rounded-lg">
              <div className="flex items-start gap-2">
                <Mic className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="text-sm font-medium mb-1">You said:</p>
                  <p className="text-sm">{transcript}</p>
                </div>
              </div>
            </div>
          )}

          {response && (
            <div className="p-4 bg-primary/10 rounded-lg">
              <div className="flex items-start gap-2">
                <MessageSquare className="h-5 w-5 text-primary mt-0.5" />
                <div>
                  <p className="text-sm font-medium mb-1">Response:</p>
                  <p className="text-sm">{response.response}</p>
                  {response.intent && (
                    <p className="text-xs text-muted-foreground mt-2">
                      Intent: {response.intent}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Voice Commands Reference */}
      <Card>
        <CardHeader>
          <CardTitle>Available Commands</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div>
              <p className="font-medium text-sm">Navigation:</p>
              <ul className="text-sm text-muted-foreground space-y-1 mt-2">
                <li>• "Go to dashboard"</li>
                <li>• "Show my profile"</li>
                <li>• "Open user management"</li>
                <li>• "Show documents"</li>
              </ul>
            </div>
            <div>
              <p className="font-medium text-sm">Actions:</p>
              <ul className="text-sm text-muted-foreground space-y-1 mt-2">
                <li>• "Upload a document"</li>
                <li>• "Show system status"</li>
                <li>• "Open analytics"</li>
              </ul>
            </div>
            <div>
              <p className="font-medium text-sm">Queries:</p>
              <ul className="text-sm text-muted-foreground space-y-1 mt-2">
                <li>• "How many users do we have?"</li>
                <li>• "What's the system health?"</li>
                <li>• "Show pending documents"</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

