'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Sparkles,
  Image as ImageIcon,
  Video,
  Mic,
  MicOff,
  Volume2,
  Code,
  Brain,
  Zap,
  Settings,
  Play,
  Pause,
  Square,
  Download,
  Upload,
  Wand2,
  Cpu,
  Network,
  Database
} from 'lucide-react'
import { ImageGenerator } from '@/components/ai/ImageGenerator'
import { openRouter, POPULAR_MODELS } from '@/lib/openrouter'
import { comfyUI, WORKFLOW_TEMPLATES } from '@/lib/comfyui'
import toast from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'

interface AIService {
  name: string
  status: 'online' | 'offline' | 'busy'
  latency: number
  credits: number
  models: number
}

export default function AIStudioPage() {
  const [activeTab, setActiveTab] = useState('chat')
  const [serviceStatus, setServiceStatus] = useState<AIService[]>([])
  const [isRecording, setIsRecording] = useState(false)
  const [audioData, setAudioData] = useState<Blob | null>(null)
  const [chatMessages, setChatMessages] = useState<Array<{
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: Date
  }>>([])
  const [chatInput, setChatInput] = useState('')
  const [selectedModel, setSelectedModel] = useState('anthropic/claude-3-haiku')
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    loadServiceStatus()
  }, [])

  const loadServiceStatus = async () => {
    try {
      // Mock service status - in production, this would check actual service health
      const mockServices: AIService[] = [
        { name: 'OpenRouter', status: 'online', latency: 145, credits: 1250, models: 150 },
        { name: 'ComfyUI', status: 'online', latency: 89, credits: 850, models: 45 },
        { name: 'ElevenLabs', status: 'online', latency: 234, credits: 420, models: 12 },
        { name: 'Whisper', status: 'online', latency: 67, credits: 680, models: 5 }
      ]
      setServiceStatus(mockServices)
    } catch (error) {
      console.error('Failed to load service status:', error)
    }
  }

  const handleChatSubmit = async () => {
    if (!chatInput.trim()) return

    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: chatInput,
      timestamp: new Date()
    }

    setChatMessages(prev => [...prev, userMessage])
    setChatInput('')
    setIsGenerating(true)

    try {
      const messages = chatMessages.concat(userMessage).map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      const response = await openRouter.chat(messages, selectedModel, {
        temperature: 0.7,
        max_tokens: 1000
      })

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: response.choices[0]?.message?.content || 'Sorry, I couldn\'t generate a response.',
        timestamp: new Date()
      }

      setChatMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat failed:', error)
      toast.error('Failed to get AI response')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleVoiceRecording = async () => {
    if (isRecording) {
      setIsRecording(false)
      // In a real implementation, this would stop recording and process the audio
      toast.success('Voice recording stopped')
    } else {
      setIsRecording(true)
      toast.success('Voice recording started')
      // Mock recording for demo
      setTimeout(() => {
        setIsRecording(false)
        toast.success('Voice processed successfully')
      }, 3000)
    }
  }

  const handleImageGenerated = (image: any) => {
    console.log('Image generated:', image)
    toast.success('Image generated successfully!')
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-600'
      case 'busy': return 'text-yellow-600'
      case 'offline': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
      case 'busy': return <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
      case 'offline': return <div className="w-2 h-2 bg-red-500 rounded-full" />
      default: return <div className="w-2 h-2 bg-gray-500 rounded-full" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Studio</h1>
          <p className="text-muted-foreground">
            Create with AI - Images, Videos, Audio, Code, and more
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="px-3 py-1">
            <Zap className="h-4 w-4 mr-1" />
            2,340 Credits
          </Badge>
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {/* Service Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5" />
            AI Services Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {serviceStatus.map((service) => (
              <div key={service.name} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-2">
                  {getStatusIcon(service.status)}
                  <span className="font-medium">{service.name}</span>
                </div>
                <div className="text-right text-sm">
                  <div className={getStatusColor(service.status)}>
                    {service.latency}ms
                  </div>
                  <div className="text-muted-foreground">
                    {service.credits} credits
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Main AI Studio */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            Chat
          </TabsTrigger>
          <TabsTrigger value="image" className="flex items-center gap-2">
            <ImageIcon className="h-4 w-4" />
            Images
          </TabsTrigger>
          <TabsTrigger value="video" className="flex items-center gap-2">
            <Video className="h-4 w-4" />
            Videos
          </TabsTrigger>
          <TabsTrigger value="audio" className="flex items-center gap-2">
            <Volume2 className="h-4 w-4" />
            Audio
          </TabsTrigger>
          <TabsTrigger value="code" className="flex items-center gap-2">
            <Code className="h-4 w-4" />
            Code
          </TabsTrigger>
          <TabsTrigger value="workflows" className="flex items-center gap-2">
            <Wand2 className="h-4 w-4" />
            Workflows
          </TabsTrigger>
        </TabsList>

        {/* Chat Tab */}
        <TabsContent value="chat" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>AI Chat Assistant</CardTitle>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Label>Model:</Label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="px-3 py-1 border border-gray-300 rounded-md bg-white text-sm"
                  >
                    {POPULAR_MODELS.chat.map((model) => (
                      <option key={model.id} value={model.id}>
                        {model.name}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  variant={isRecording ? "destructive" : "outline"}
                  onClick={handleVoiceRecording}
                  className="flex items-center gap-2"
                >
                  {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  {isRecording ? 'Stop' : 'Voice'}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {/* Chat Messages */}
              <div className="h-96 overflow-y-auto border rounded-lg p-4 mb-4 space-y-4">
                <AnimatePresence>
                  {chatMessages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[70%] p-3 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 dark:bg-gray-800'
                      }`}>
                        <p className="text-sm">{message.content}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>

                {isGenerating && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex justify-start"
                  >
                    <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>

              {/* Chat Input */}
              <div className="flex gap-2">
                <Input
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask me anything..."
                  onKeyPress={(e) => e.key === 'Enter' && handleChatSubmit()}
                  disabled={isGenerating}
                />
                <Button onClick={handleChatSubmit} disabled={isGenerating || !chatInput.trim()}>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Send
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Image Tab */}
        <TabsContent value="image" className="space-y-6">
          <ImageGenerator onImageGenerated={handleImageGenerated} />
        </TabsContent>

        {/* Video Tab */}
        <TabsContent value="video" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>AI Video Generation</CardTitle>
              <p className="text-sm text-muted-foreground">
                Create videos from text prompts using advanced AI models
              </p>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Video className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-medium mb-2">Video Generation Coming Soon</h3>
                <p className="text-muted-foreground mb-4">
                  We're working on integrating advanced video generation models
                </p>
                <Badge variant="secondary">Expected: Q1 2025</Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Audio Tab */}
        <TabsContent value="audio" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Voice Synthesis & Audio</CardTitle>
              <p className="text-sm text-muted-foreground">
                Generate speech, music, and process audio with AI
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* TTS Section */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="font-medium">Text-to-Speech</h3>
                  <textarea
                    className="w-full p-3 border border-gray-300 rounded-md"
                    rows={4}
                    placeholder="Enter text to convert to speech..."
                  />
                  <div className="flex gap-2">
                    <select className="px-3 py-2 border border-gray-300 rounded-md">
                      <option>English (Female)</option>
                      <option>English (Male)</option>
                      <option>Spanish</option>
                      <option>French</option>
                    </select>
                    <Button>
                      <Volume2 className="h-4 w-4 mr-2" />
                      Generate
                    </Button>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-medium">Speech-to-Text</h3>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                    <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">
                      Drop audio file here or click to upload
                    </p>
                  </div>
                  <Button variant="outline" className="w-full">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Audio
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Code Tab */}
        <TabsContent value="code" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>AI Code Generation</CardTitle>
              <p className="text-sm text-muted-foreground">
                Generate, explain, and improve code with AI assistance
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <Label>Code Prompt</Label>
                  <textarea
                    className="w-full p-3 border border-gray-300 rounded-md"
                    rows={6}
                    placeholder="Describe what code you want to generate..."
                  />
                  <div className="flex gap-2">
                    <select className="px-3 py-2 border border-gray-300 rounded-md">
                      <option>Python</option>
                      <option>JavaScript</option>
                      <option>TypeScript</option>
                      <option>React</option>
                      <option>SQL</option>
                    </select>
                    <Button>
                      <Code className="h-4 w-4 mr-2" />
                      Generate
                    </Button>
                  </div>
                </div>

                <div className="space-y-4">
                  <Label>Generated Code</Label>
                  <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-md font-mono text-sm min-h-[200px]">
                    <pre className="text-muted-foreground">
                      {`# Generated code will appear here
def hello_world():
    print("Hello, World!")

hello_world()`}
                    </pre>
                  </div>
                  <Button variant="outline" className="w-full">
                    <Download className="h-4 w-4 mr-2" />
                    Download Code
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>ComfyUI Workflows</CardTitle>
              <p className="text-sm text-muted-foreground">
                Advanced AI workflows with custom ComfyUI pipelines
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(WORKFLOW_TEMPLATES).map(([id, workflow]) => (
                  <Card key={id} className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Wand2 className="h-5 w-5 text-blue-600" />
                        <h3 className="font-medium">{workflow.name}</h3>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        {workflow.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <Badge variant="secondary" className="capitalize">
                          {workflow.category}
                        </Badge>
                        <Button size="sm" variant="outline">
                          <Play className="h-3 w-3 mr-1" />
                          Run
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                  About ComfyUI Workflows
                </h4>
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  ComfyUI workflows provide advanced AI capabilities with custom node-based pipelines.
                  Create complex AI workflows combining multiple models and processing steps for
                  professional-grade results.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
