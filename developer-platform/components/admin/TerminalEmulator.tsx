'use client'

import { useState, useRef, useEffect } from 'react'
import { Terminal as TerminalIcon } from 'lucide-react'

interface TerminalEmulatorProps {
  output?: string
  isRunning?: boolean
  onCommand?: (command: string) => void
  className?: string
}

export function TerminalEmulator({
  output = '',
  isRunning = false,
  onCommand,
  className = ''
}: TerminalEmulatorProps) {
  const [command, setCommand] = useState('')
  const [history, setHistory] = useState<string[]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!command.trim()) return

    // Add to history
    setHistory(prev => [...prev, command])
    setHistoryIndex(-1)

    // Execute command
    onCommand?.(command)

    // Clear input
    setCommand('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      if (historyIndex < history.length - 1) {
        const newIndex = historyIndex + 1
        setHistoryIndex(newIndex)
        setCommand(history[history.length - 1 - newIndex])
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault()
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1
        setHistoryIndex(newIndex)
        setCommand(history[history.length - 1 - newIndex])
      } else if (historyIndex === 0) {
        setHistoryIndex(-1)
        setCommand('')
      }
    }
  }

  return (
    <div className={`bg-gray-900 text-green-400 font-mono text-sm ${className}`}>
      {/* Terminal Header */}
      <div className="bg-gray-800 px-4 py-2 flex items-center space-x-2 border-b border-gray-700">
        <TerminalIcon className="w-4 h-4" />
        <span>Galion Terminal</span>
        {isRunning && (
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-xs">Running</span>
          </div>
        )}
      </div>

      {/* Terminal Output */}
      <div className="p-4 min-h-[200px] max-h-[400px] overflow-y-auto">
        <div className="space-y-1">
          {/* Welcome message */}
          <div className="text-gray-500">
            <div>Galion Development Terminal v2.2</div>
            <div>Type 'help' for available commands.</div>
            <div></div>
          </div>

          {/* Command history and output */}
          {history.map((cmd, index) => (
            <div key={index}>
              <div className="flex items-center">
                <span className="text-green-400 mr-2">$</span>
                <span>{cmd}</span>
              </div>
              {/* Mock output for demonstration */}
              <div className="text-gray-300 ml-4">
                {cmd === 'help' && 'Available commands: help, ls, cd, run, deploy, status, clear'}
                {cmd === 'ls' && 'main.nx  utils.nx  tests/  docs/'}
                {cmd === 'status' && 'All systems operational. Agents: 5/5 active.'}
                {cmd.startsWith('run') && 'Executing code...\nOutput: Hello World!\nExecution completed.'}
                {cmd === 'deploy' && 'Deployment started...\nBuilding application...\nDeploying to production...\nDeployment successful!'}
              </div>
            </div>
          ))}

          {/* Current output */}
          {output && (
            <div className="text-gray-300 whitespace-pre-wrap">{output}</div>
          )}

          {/* Command prompt */}
          <form onSubmit={handleSubmit} className="flex items-center">
            <span className="text-green-400 mr-2">$</span>
            <input
              ref={inputRef}
              type="text"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyDown={handleKeyDown}
              className="flex-1 bg-transparent outline-none text-green-400"
              placeholder="Enter command..."
              autoComplete="off"
            />
          </form>
        </div>
      </div>
    </div>
  )
}

export default TerminalEmulator
