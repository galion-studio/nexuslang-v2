'use client'

import { useState, useEffect } from 'react'
import { Play, Save, FolderOpen, Settings, Terminal, FileText, Code, Zap, Mic, MicOff } from 'lucide-react'
import { MonacoEditor } from '@/components/ide/MonacoEditor'
import { VoiceCommandBar } from '@/components/ide/VoiceCommandBar'
import { FileExplorer } from '@/components/ide/FileExplorer'
import { Terminal as TerminalComponent } from '@/components/ide/Terminal'
import { PersonalityEditor } from '@/components/ide/PersonalityEditor'
import { BinaryCompiler } from '@/components/ide/BinaryCompiler'
// Shared components removed for simplified deployment
// Shared components removed for simplified deployment

export default function IDEPage() {
  const [activePanel, setActivePanel] = useState<'editor' | 'terminal' | 'personality' | 'compiler'>('editor')
  const [isVoiceActive, setIsVoiceActive] = useState(false)
  const [currentFile, setCurrentFile] = useState('main.nx')
  const [code, setCode] = useState(`// Welcome to Galion IDE
// Write your NexusLang code here

function fibonacci(n: int) -> int {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

print("Fibonacci sequence:");
for (let i = 0; i < 10; i++) {
    print(fibonacci(i));
}`)

  const [isCompiling, setIsCompiling] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [output, setOutput] = useState('')

  useEffect(() => {
    // Set platform attribute for styling
    document.documentElement.setAttribute('data-platform', 'developer')
  }, [])

  const handleRun = async () => {
    setIsRunning(true)
    setActivePanel('terminal')

    // Simulate compilation and execution
    setTimeout(() => {
      setOutput(`Compiling ${currentFile}...\nRunning program...\n\nFibonacci sequence:\n0\n1\n1\n2\n3\n5\n8\n13\n21\n34\n\nProgram executed successfully in 0.023 seconds.`)
      setIsRunning(false)
    }, 2000)
  }

  const handleCompile = async () => {
    setIsCompiling(true)
    setActivePanel('compiler')

    // Simulate compilation
    setTimeout(() => {
      setIsCompiling(false)
    }, 1500)
  }

  const handleVoiceToggle = () => {
    setIsVoiceActive(!isVoiceActive)
  }

  const handleVoiceCommand = (command: string) => {
    const cmd = command.toLowerCase().trim()

    // Voice command processing
    if (cmd.includes('run') || cmd.includes('execute')) {
      handleRun()
    } else if (cmd.includes('compile') || cmd.includes('build')) {
      handleCompile()
    } else if (cmd.includes('save')) {
      handleSave()
    } else if (cmd.includes('switch to editor')) {
      setActivePanel('editor')
    } else if (cmd.includes('switch to terminal')) {
      setActivePanel('terminal')
    } else if (cmd.includes('switch to personality')) {
      setActivePanel('personality')
    } else if (cmd.includes('switch to compiler')) {
      setActivePanel('compiler')
    } else if (cmd.includes('create function')) {
      // Insert function template
      const functionTemplate = `function newFunction(param: type) -> returnType {
    // Function implementation
    return result;
}`
      setCode(prev => prev + '\n\n' + functionTemplate)
    } else if (cmd.includes('add comment') || cmd.includes('document')) {
      // Add documentation comment
      const commentTemplate = `/**
 * Function description
 * @param param description
 * @returns description
 */`
      setCode(prev => commentTemplate + '\n' + prev)
    } else {
      // Fallback: append command as comment
      setCode(prev => prev + `\n// Voice command: ${command}`)
    }
  }

  const handleSave = () => {
    // Simulate save operation
    console.log('Saving file:', currentFile, code)
  }

  const panels = [
    { id: 'editor', label: 'Editor', icon: Code },
    { id: 'terminal', label: 'Terminal', icon: Terminal },
    { id: 'personality', label: 'Personality', icon: Settings },
    { id: 'compiler', label: 'Compiler', icon: Zap }
  ]

  return (
    <ErrorBoundary>
      <div className="h-screen bg-bg-primary flex flex-col">
        {/* Top Toolbar */}
        <div className="bg-bg-secondary border-b border-border px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                <Code className="w-5 h-5 text-white" />
              </div>
              <div>
                <Text variant="h2" className="text-text-primary leading-tight">
                  Galion IDE
                </Text>
                <Text variant="caption" color="secondary" className="italic">
                  "Your imagination is the end."
                </Text>
              </div>
            </div>
            <Text variant="caption" color="secondary">
              {currentFile}
            </Text>
          </div>

          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSave}
              leftIcon={<Save className="w-4 h-4" />}
            >
              Save
            </Button>

            <Button
              variant="solid"
              color="primary"
              size="sm"
              onClick={handleCompile}
              disabled={isCompiling}
              leftIcon={isCompiling ? <Loading size="sm" /> : <Zap className="w-4 h-4" />}
            >
              Compile
            </Button>

            <Button
              variant="solid"
              color="success"
              size="sm"
              onClick={handleRun}
              disabled={isRunning}
              leftIcon={isRunning ? <Loading size="sm" /> : <Play className="w-4 h-4" />}
            >
              Run
            </Button>
          </div>
        </div>

        {/* Voice Command Bar */}
        <div className="border-b border-border bg-bg-secondary">
          <div className="max-w-2xl mx-auto px-4 py-3">
            <VoiceInterface
              onTranscription={(text, isFinal) => {
                if (isFinal) handleVoiceCommand(text)
              }}
              onStateChange={(listening, processing) => {
                setIsVoiceActive(listening)
              }}
              className="bg-bg-primary/50 backdrop-blur-sm rounded-lg border border-border/50 p-4"
            />
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex">
          {/* Left Sidebar - File Explorer */}
          <div className="w-64 bg-bg-secondary border-r border-border flex flex-col">
            <Card className="m-0 rounded-none border-0 border-b border-border">
              <div className="flex items-center space-x-2 p-4">
                <FolderOpen className="w-4 h-4 text-text-secondary" />
                <Text variant="caption" weight="medium" color="primary">
                  Project Files
                </Text>
              </div>
            </Card>
            <div className="flex-1 overflow-y-auto">
              <FileExplorer
                onFileSelect={setCurrentFile}
                currentFile={currentFile}
              />
            </div>
          </div>

          {/* Main Editor Area */}
          <div className="flex-1 flex flex-col">
            {/* Panel Tabs */}
            <div className="bg-bg-secondary border-b border-border px-4 flex items-center space-x-1">
              {panels.map((panel) => {
                const IconComponent = panel.icon
                return (
                  <Button
                    key={panel.id}
                    variant={activePanel === panel.id ? 'solid' : 'ghost'}
                    color="primary"
                    size="sm"
                    onClick={() => setActivePanel(panel.id as any)}
                    leftIcon={<IconComponent className="w-4 h-4" />}
                    className="rounded-md"
                  >
                    {panel.label}
                  </Button>
                )
              })}
            </div>

            {/* Panel Content */}
            <div className="flex-1 overflow-hidden">
              {activePanel === 'editor' && (
                <MonacoEditor
                  value={code}
                  onChange={setCode}
                  language="typescript"
                  className="h-full"
                />
              )}

              {activePanel === 'terminal' && (
                <TerminalComponent
                  output={output}
                  isRunning={isRunning}
                  className="h-full"
                />
              )}

              {activePanel === 'personality' && (
                <PersonalityEditor className="h-full" />
              )}

              {activePanel === 'compiler' && (
                <BinaryCompiler
                  code={code}
                  isCompiling={isCompiling}
                  className="h-full"
                />
              )}
            </div>
          </div>

          {/* Right Sidebar - Voice Assistant */}
          <div className="w-80 bg-bg-secondary border-l border-border flex flex-col">
            <Card className="m-0 rounded-none border-0 border-b border-border">
              <div className="flex items-center justify-between p-4">
                <div className="flex items-center space-x-2">
                  <Mic className="w-5 h-5 text-primary-500" />
                  <Text variant="caption" weight="medium" color="primary">
                    AI Assistant
                  </Text>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
                  <Text variant="caption" color="success">
                    Online
                  </Text>
                </div>
              </div>
            </Card>

            <div className="flex-1 p-4 space-y-4">
              <Card className="glass">
                <Text variant="p" className="text-sm italic">
                  "I can help you write, debug, and optimize your NexusLang code. Try asking me to explain the Fibonacci function or suggest improvements!"
                </Text>
              </Card>

              <div className="space-y-3">
                <Text variant="caption" weight="medium" color="secondary" className="uppercase tracking-wide">
                  Quick Actions
                </Text>
                <div className="space-y-2">
                  <Button variant="ghost" size="sm" className="w-full justify-start">
                    Generate unit tests
                  </Button>
                  <Button variant="ghost" size="sm" className="w-full justify-start">
                    Optimize performance
                  </Button>
                  <Button variant="ghost" size="sm" className="w-full justify-start">
                    Add documentation
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}