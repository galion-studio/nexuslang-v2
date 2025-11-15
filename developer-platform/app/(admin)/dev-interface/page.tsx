'use client'

import { useState, useEffect } from 'react'
import { FileManager } from '@/components/admin/FileManager'
import { AgentPrompt } from '@/components/admin/AgentPrompt'
import { AgentMonitor } from '@/components/admin/AgentMonitor'
import { AdminDashboard } from '@/components/admin/AdminDashboard'
import { CodeExecutor } from '@/components/admin/CodeExecutor'
import { TerminalEmulator } from '@/components/admin/TerminalEmulator'
// Shared components removed for simplified deployment
import { FolderOpen, Code, Terminal, Activity, Play, Save, Settings } from 'lucide-react'

export default function DevInterfacePage() {
  const [currentView, setCurrentView] = useState<'files' | 'editor' | 'terminal' | 'agents' | 'admin'>('editor')
  const [currentFile, setCurrentFile] = useState<string | null>(null)
  const [code, setCode] = useState('')
  const [isExecuting, setIsExecuting] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [terminalOutput, setTerminalOutput] = useState('')
  const [showAgentMonitor, setShowAgentMonitor] = useState(false)

  useEffect(() => {
    // Set platform attribute for styling
    document.documentElement.setAttribute('data-platform', 'developer')

    // Load initial file content
    if (currentFile) {
      loadFileContent(currentFile)
    }
  }, [currentFile])

  const loadFileContent = async (filePath: string) => {
    try {
      // In a real implementation, this would fetch from the backend
      const mockContent = `// ${filePath}
// This is a mock file loaded in the Galion Dev Interface
// Similar to Cursor's in-editor development experience

function exampleFunction() {
    console.log("Hello from Galion Dev Interface!");
    return "development";
}

export default exampleFunction;`
      setCode(mockContent)
    } catch (error) {
      console.error('Failed to load file:', error)
    }
  }

  const handleExecute = async () => {
    setIsExecuting(true)
    setCurrentView('terminal')

    try {
      // Simulate code execution
      setTerminalOutput('Compiling...\nRunning...\n\nOutput: Hello from Galion Dev Interface!\nExecution completed successfully.')
    } catch (error) {
      setTerminalOutput(`Error: ${error}`)
    } finally {
      setIsExecuting(false)
    }
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      // Simulate save operation
      await new Promise(resolve => setTimeout(resolve, 1000))
      console.log('File saved:', currentFile, code)
    } finally {
      setIsSaving(false)
    }
  }

  const views = [
    { id: 'files', label: 'Files', icon: FolderOpen },
    { id: 'editor', label: 'Editor', icon: Code },
    { id: 'terminal', label: 'Terminal', icon: Terminal },
    { id: 'agents', label: 'Agents', icon: Activity },
    { id: 'admin', label: 'Admin', icon: Settings }
  ]

  return (
    <ErrorBoundary>
      <div className="h-screen bg-background flex flex-col">
        {/* Top Header */}
        <div className="bg-surface border-b border-border px-6 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold text-foreground">Galion Dev Interface</h1>
            <span className="text-sm text-foreground-muted">
              {currentFile || 'No file selected'}
            </span>
          </div>

          <div className="flex items-center space-x-3">
            <VoiceButton size="small" platform="developer" />
            <button
              onClick={() => setShowAgentMonitor(!showAgentMonitor)}
              className="flex items-center space-x-2 px-3 py-1.5 bg-surface-hover hover:bg-surface-active rounded-md transition-colors"
            >
              <Activity className="w-4 h-4" />
              <span className="text-sm">Agents</span>
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center space-x-2 px-3 py-1.5 bg-primary text-primary-foreground rounded-md hover:bg-primary-hover disabled:opacity-50 transition-colors"
            >
              {isSaving ? (
                <LoadingStates type="spinner" size="sm" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              <span className="text-sm">Save</span>
            </button>
            <button
              onClick={handleExecute}
              disabled={isExecuting}
              className="flex items-center space-x-2 px-3 py-1.5 bg-accent text-accent-foreground rounded-md hover:bg-accent-active disabled:opacity-50 transition-colors"
            >
              {isExecuting ? (
                <LoadingStates type="spinner" size="sm" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              <span className="text-sm">Run</span>
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex">
          {/* Left Sidebar - File Explorer */}
          <div className={`bg-surface border-r border-border transition-all duration-300 ${
            currentView === 'files' ? 'w-80' : 'w-16'
          }`}>
            <div className="p-3 border-b border-border">
              <button
                onClick={() => setCurrentView(currentView === 'files' ? 'editor' : 'files')}
                className="flex items-center space-x-2 hover:bg-surface-hover rounded px-2 py-1 transition-colors w-full text-left"
              >
                <FolderOpen className="w-4 h-4" />
                {currentView === 'files' && <span className="text-sm font-medium">Project Files</span>}
              </button>
            </div>
            {currentView === 'files' && (
              <div className="flex-1 overflow-y-auto">
                <FileManager onFileSelect={setCurrentFile} currentFile={currentFile} />
              </div>
            )}
          </div>

          {/* Main Editor Area */}
          <div className="flex-1 flex flex-col">
            {/* View Tabs */}
            <div className="bg-surface border-b border-border px-4 flex items-center space-x-1">
              {views.map((view) => {
                const IconComponent = view.icon
                return (
                  <button
                    key={view.id}
                    onClick={() => setCurrentView(view.id as any)}
                    className={`flex items-center space-x-2 px-3 py-2 text-sm rounded-md transition-colors ${
                      currentView === view.id
                        ? 'bg-primary text-primary-foreground'
                        : 'text-foreground-muted hover:text-foreground hover:bg-surface-hover'
                    }`}
                  >
                    <IconComponent className="w-4 h-4" />
                    <span>{view.label}</span>
                  </button>
                )
              })}
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-hidden">
              {currentView === 'editor' && (
                <div className="h-full p-4">
                  {currentFile ? (
                    <textarea
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      className="w-full h-full bg-gray-900 text-green-400 font-mono text-sm p-4 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="Select a file to start editing..."
                    />
                  ) : (
                    <div className="h-full flex items-center justify-center text-center">
                      <div>
                        <Code className="w-16 h-16 text-foreground-muted mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-foreground mb-2">
                          Select a file to start coding
                        </h3>
                        <p className="text-foreground-muted">
                          Choose a file from the explorer or create a new one
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {currentView === 'terminal' && (
                <TerminalEmulator output={terminalOutput} isRunning={isExecuting} />
              )}

              {currentView === 'agents' && (
                <div className="h-full p-6">
                  <AgentPrompt />
                </div>
              )}

              {currentView === 'admin' && (
                <div className="h-full p-6">
                  <AdminDashboard />
                </div>
              )}
            </div>
          </div>

          {/* Right Sidebar - Agent Monitor */}
          <div className={`bg-surface border-l border-border transition-all duration-300 ${
            showAgentMonitor ? 'w-80' : 'w-0 overflow-hidden'
          }`}>
            <div className="p-3 border-b border-border">
              <h3 className="text-sm font-medium text-foreground">Agent Monitor</h3>
            </div>
            <div className="flex-1 overflow-y-auto">
              <AgentMonitor />
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div className="bg-surface border-t border-border px-4 py-2 flex items-center justify-between text-xs text-foreground-muted">
          <div className="flex items-center space-x-4">
            <span>Galion v2.2</span>
            <span>•</span>
            <span>{currentFile ? 'Modified' : 'Ready'}</span>
          </div>
          <div className="flex items-center space-x-4">
            <span>UTF-8</span>
            <span>•</span>
            <span>JavaScript</span>
            <span>•</span>
            <span>Ln 1, Col 1</span>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}
