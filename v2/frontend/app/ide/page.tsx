'use client'

import { useState, useEffect } from 'react'
import MonacoEditor from '@/components/ide/MonacoEditor'
import PersonalityEditor from '@/components/ide/PersonalityEditor'
import BinaryCompiler from '@/components/ide/BinaryCompiler'
import ExamplesLibrary from '@/components/ide/ExamplesLibrary'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface ExecutionResult {
  stdout: string
  stderr: string
  return_code: number
  execution_time: number
  success: boolean
  error?: string
  credits_used: number
}

type TabType = 'editor' | 'personality' | 'compiler' | 'examples' | 'results'

export default function IDE() {
  const [code, setCode] = useState(`// Welcome to NexusLang IDE!
// Write your AI-native code here

personality {
    curious: 0.8,
    analytical: 0.7
}

fn greet_user(name: string) {
    let greeting = "Hello, " + name + "!"
    say(greeting, emotion="excited")
    return greeting
}

// Execute this function
greet_user("Developer")`)

  const [isExecuting, setIsExecuting] = useState(false)
  const [result, setResult] = useState<ExecutionResult | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>('editor')
  const [personalityTraits, setPersonalityTraits] = useState<Record<string, number>>({})

  const executeCode = async () => {
    if (!code.trim()) return

    setIsExecuting(true)
    setResult(null)

    try {
      const response = await fetch('http://localhost:8010/api/v2/nexuslang/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code,
          language: 'nexuslang'
        }),
      })

      const data = await response.json()
      setResult(data)
      setActiveTab('results')
    } catch (error) {
      setResult({
        stdout: '',
        stderr: 'Connection failed. Please check if the backend is running.',
        return_code: 1,
        execution_time: 0,
        success: false,
        error: 'Network error',
        credits_used: 0
      })
      setActiveTab('results')
    } finally {
      setIsExecuting(false)
    }
  }

  const handleExampleSelect = (example: any) => {
    setCode(example.code)
    setActiveTab('editor')
  }

  const tabs = [
    { id: 'editor' as TabType, name: 'Code Editor', icon: '📝', description: 'Write and edit NexusLang code' },
    { id: 'personality' as TabType, name: 'Personality', icon: '🎭', description: 'Configure AI behavior traits' },
    { id: 'compiler' as TabType, name: 'Compiler', icon: '⚡', description: 'Compile to optimized binary' },
    { id: 'examples' as TabType, name: 'Examples', icon: '📚', description: 'Browse code examples and templates' },
    { id: 'results' as TabType, name: 'Results', icon: '🎯', description: 'View execution results and output' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-6xl font-bold text-white mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            NexusLang IDE
          </h1>
          <p className="text-xl text-gray-300 mb-6">
            Complete AI-native development environment with personality, voice, and binary optimization
          </p>

          {/* Quick Stats */}
          <div className="flex justify-center gap-6 mb-8">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg px-4 py-2 border border-gray-700">
              <div className="text-2xl font-bold text-green-400">⚡</div>
              <div className="text-sm text-gray-300">Real-time</div>
            </div>
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg px-4 py-2 border border-gray-700">
              <div className="text-2xl font-bold text-blue-400">🤖</div>
              <div className="text-sm text-gray-300">AI-Powered</div>
            </div>
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg px-4 py-2 border border-gray-700">
              <div className="text-2xl font-bold text-purple-400">🎤</div>
              <div className="text-sm text-gray-300">Voice-Ready</div>
            </div>
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg px-4 py-2 border border-gray-700">
              <div className="text-2xl font-bold text-yellow-400">🔧</div>
              <div className="text-sm text-gray-300">Binary Opt</div>
            </div>
          </div>
        </div>

        {/* Main IDE Interface */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700 overflow-hidden">
          {/* Tab Navigation */}
          <div className="flex border-b border-gray-700 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Editor Tab */}
            {activeTab === 'editor' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <div>
                    <h2 className="text-2xl font-semibold text-white">Code Editor</h2>
                    <p className="text-gray-400">Write and edit NexusLang code with full syntax highlighting</p>
                  </div>
                  <Button
                    onClick={executeCode}
                    disabled={isExecuting || !code.trim()}
                    size="lg"
                    className="px-8"
                  >
                    {isExecuting ? '⚡ Executing...' : '▶️ Run Code'}
                  </Button>
                </div>

                <MonacoEditor
                  value={code}
                  onChange={setCode}
                  height="600px"
                />

                {/* Quick Actions */}
                <div className="flex gap-4">
                  <Button
                    onClick={() => setCode('')}
                    variant="outline"
                    size="sm"
                  >
                    🗑️ Clear Code
                  </Button>
                  <Button
                    onClick={() => navigator.clipboard?.writeText(code)}
                    variant="outline"
                    size="sm"
                  >
                    📋 Copy Code
                  </Button>
                  <Button
                    onClick={() => setActiveTab('examples')}
                    variant="outline"
                    size="sm"
                  >
                    📚 Browse Examples
                  </Button>
                </div>
              </div>
            )}

            {/* Personality Tab */}
            {activeTab === 'personality' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-semibold text-white">AI Personality Editor</h2>
                  <p className="text-gray-400">Configure 24+ personality traits to customize AI behavior</p>
                </div>

                <PersonalityEditor
                  onPersonalityChange={setPersonalityTraits}
                />

                {/* Personality Code Integration */}
                <Card>
                  <CardHeader>
                    <CardTitle>🎭 Personality Code</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-400 mb-4">
                      Add this personality configuration to your code:
                    </p>
                    <div className="bg-gray-900 p-4 rounded-lg font-mono text-sm text-green-400">
                      <pre>{`personality {
${Object.entries(personalityTraits)
  .filter(([, value]) => value > 0.1)
  .map(([trait, value]) => `    ${trait}: ${value.toFixed(1)},`)
  .join('\n')}
}`}</pre>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Compiler Tab */}
            {activeTab === 'compiler' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-semibold text-white">Binary Compiler</h2>
                  <p className="text-gray-400">Compile NexusLang to optimized binary for 10-15x performance boost</p>
                </div>

                <BinaryCompiler
                  code={code}
                  onCompile={(result) => {
                    if (result.status === 'success') {
                      setActiveTab('results')
                    }
                  }}
                />
              </div>
            )}

            {/* Examples Tab */}
            {activeTab === 'examples' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-semibold text-white">Code Examples</h2>
                  <p className="text-gray-400">Browse 16+ comprehensive examples and templates</p>
                </div>

                <ExamplesLibrary
                  onExampleSelect={handleExampleSelect}
                />
              </div>
            )}

            {/* Results Tab */}
            {activeTab === 'results' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-semibold text-white">Execution Results</h2>
                  <p className="text-gray-400">View code execution output and performance metrics</p>
                </div>

                {isExecuting && (
                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mr-3"></div>
                        <span className="text-blue-300 text-lg">Executing code...</span>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {result && (
                  <div className="space-y-4">
                    {/* Execution Summary */}
                    <Card>
                      <CardHeader>
                        <CardTitle className={`flex items-center gap-2 ${
                          result.success ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {result.success ? '✅' : '❌'}
                          Execution {result.success ? 'Successful' : 'Failed'}
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="text-center">
                            <div className="text-xl font-bold text-blue-400">{result.return_code}</div>
                            <div className="text-sm text-gray-300">Exit Code</div>
                          </div>
                          <div className="text-center">
                            <div className="text-xl font-bold text-purple-400">{result.execution_time.toFixed(1)}ms</div>
                            <div className="text-sm text-gray-300">Execution Time</div>
                          </div>
                          <div className="text-center">
                            <div className="text-xl font-bold text-yellow-400">{result.credits_used}</div>
                            <div className="text-sm text-gray-300">Credits Used</div>
                          </div>
                          <div className="text-center">
                            <div className="text-xl font-bold text-green-400">
                              {result.success ? 'Success' : 'Failed'}
                            </div>
                            <div className="text-sm text-gray-300">Status</div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Output */}
                    {result.stdout && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-green-400">📤 Standard Output</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <pre className="text-green-200 whitespace-pre-wrap font-mono text-sm bg-green-900/30 p-4 rounded overflow-auto max-h-96">
                            {result.stdout}
                          </pre>
                        </CardContent>
                      </Card>
                    )}

                    {/* Error Output */}
                    {(result.stderr || result.error) && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-red-400">⚠️ Error Output</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <pre className="text-red-200 whitespace-pre-wrap font-mono text-sm bg-red-900/30 p-4 rounded overflow-auto max-h-96">
                            {result.stderr || result.error}
                          </pre>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                )}

                {!result && !isExecuting && (
                  <Card>
                    <CardContent className="text-center py-12">
                      <div className="text-4xl mb-4">🎯</div>
                      <h3 className="text-xl font-semibold text-white mb-2">No Results Yet</h3>
                      <p className="text-gray-400 mb-4">
                        Execute your code to see results here
                      </p>
                      <Button onClick={() => setActiveTab('editor')}>
                        Go to Editor
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-400">
          <p className="mb-2">
            NexusLang v2 - Complete AI-Native Development Platform
          </p>
          <p className="text-sm">
            Monaco Editor • Personality System • Binary Compilation • Voice AI • Real-time Execution
          </p>
        </div>
      </div>
    </div>
  )
}
