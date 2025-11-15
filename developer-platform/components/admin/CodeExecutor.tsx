'use client'

import { useState } from 'react'
import { Play, Square, RotateCcw, Download } from 'lucide-react'
// Shared components removed for simplified deployment

interface CodeExecutorProps {
  code?: string
  language?: string
  className?: string
}

export function CodeExecutor({ code = '', language = 'javascript', className = '' }: CodeExecutorProps) {
  const [output, setOutput] = useState('')
  const [isRunning, setIsRunning] = useState(false)
  const [executionTime, setExecutionTime] = useState<number | null>(null)

  const handleExecute = async () => {
    setIsRunning(true)
    setOutput('')

    const startTime = Date.now()

    try {
      // Simulate code execution
      setOutput('Executing code...\n')

      setTimeout(() => {
        setOutput(prev => prev + 'Compilation successful.\nRunning program...\n\n')
      }, 500)

      setTimeout(() => {
        setOutput(prev => prev + 'Hello, World!\nProgram executed successfully.\n')
        setExecutionTime(Date.now() - startTime)
        setIsRunning(false)
      }, 1000)

    } catch (error) {
      setOutput(`Error: ${error}`)
      setIsRunning(false)
    }
  }

  const handleStop = () => {
    setIsRunning(false)
    setOutput(prev => prev + '\nExecution stopped by user.\n')
  }

  const handleClear = () => {
    setOutput('')
    setExecutionTime(null)
  }

  const handleDownload = () => {
    const blob = new Blob([output], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'execution_output.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className={`bg-gray-900 text-green-400 font-mono text-sm ${className}`}>
      {/* Header */}
      <div className="bg-gray-800 px-4 py-3 flex items-center justify-between border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <span className="text-green-400">Code Executor</span>
          <span className="text-gray-400">•</span>
          <span className="text-gray-400">{language}</span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleExecute}
            disabled={isRunning}
            className="flex items-center space-x-2 px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            {isRunning ? (
              <LoadingStates type="spinner" size="sm" />
            ) : (
              <Play className="w-3 h-3" />
            )}
            <span className="text-xs">Run</span>
          </button>

          {isRunning && (
            <button
              onClick={handleStop}
              className="flex items-center space-x-2 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              <Square className="w-3 h-3" />
              <span className="text-xs">Stop</span>
            </button>
          )}

          <button
            onClick={handleClear}
            className="flex items-center space-x-2 px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
          >
            <RotateCcw className="w-3 h-3" />
            <span className="text-xs">Clear</span>
          </button>

          <button
            onClick={handleDownload}
            disabled={!output}
            className="flex items-center space-x-2 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <Download className="w-3 h-3" />
            <span className="text-xs">Export</span>
          </button>
        </div>
      </div>

      {/* Output Area */}
      <div className="p-4 min-h-[300px]">
        {output ? (
          <pre className="whitespace-pre-wrap break-words">{output}</pre>
        ) : (
          <div className="text-gray-500 italic">
            {isRunning ? 'Executing...' : 'Click "Run" to execute code and see output here.'}
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="bg-gray-800 px-4 py-2 border-t border-gray-700 flex items-center justify-between text-xs text-gray-400">
        <div className="flex items-center space-x-4">
          <span>Status: {isRunning ? 'Running' : 'Ready'}</span>
          {executionTime && (
            <span>Execution time: {executionTime}ms</span>
          )}
        </div>
        <div className="flex items-center space-x-4">
          <span>Language: {language}</span>
          <span>Mode: Sandbox</span>
        </div>
      </div>
    </div>
  )
}

export default CodeExecutor
