'use client'

import { useEffect, useRef } from 'react'
import { Terminal as TerminalIcon } from 'lucide-react'

interface TerminalProps {
  output: string
  isRunning?: boolean
  onCommand?: (command: string) => void
  className?: string
}

export function Terminal({ output, isRunning = false, onCommand, className = '' }: TerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Auto-scroll to bottom when output changes
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [output])

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
      <div
        ref={terminalRef}
        className="p-4 overflow-y-auto h-full min-h-[300px]"
      >
        <div className="whitespace-pre-wrap">
          {output || (
            <div className="text-gray-500">
              <div>$ Welcome to Galion Terminal</div>
              <div>$ Type 'help' for available commands</div>
              <div>$ Ready for input...</div>
            </div>
          )}
        </div>

        {/* Command Prompt */}
        <div className="flex items-center mt-2">
          <span className="text-green-400">$</span>
          <span className="ml-2 animate-pulse">_</span>
        </div>
      </div>
    </div>
  )
}

export default Terminal