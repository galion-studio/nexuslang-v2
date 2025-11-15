'use client'

import { useRef, useEffect, useState } from 'react'
import Editor from '@monaco-editor/react'
import { Play, Settings, Save, Download } from 'lucide-react'
import { developerAPI } from '@/lib/api-client'
import toast from 'react-hot-toast'

interface CodeEditorProps {
  initialCode?: string
  language?: string
  onCodeChange?: (code: string) => void
  readOnly?: boolean
}

export function CodeEditor({
  initialCode = '',
  language = 'nexuslang',
  onCodeChange,
  readOnly = false
}: CodeEditorProps) {
  const editorRef = useRef<any>(null)
  const [code, setCode] = useState(initialCode)
  const [output, setOutput] = useState('')
  const [isRunning, setIsRunning] = useState(false)
  const [selectedLanguage, setSelectedLanguage] = useState(language)

  useEffect(() => {
    setCode(initialCode)
  }, [initialCode])

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor

    // Configure Monaco for NexusLang
    monaco.languages.register({ id: 'nexuslang' })

    monaco.languages.setMonarchTokensProvider('nexuslang', {
      tokenizer: {
        root: [
          [/\b(fn|let|const|if|else|for|while|return|import|export)\b/, 'keyword'],
          [/\b(personality|knowledge|Sequential|Linear|ReLU|say)\b/, 'keyword.control'],
          [/\b(true|false|null)\b/, 'constant'],
          [/"([^"\\]|\\.)*$/, 'string.invalid'],
          [/"([^"\\]|\\.)*"/, 'string'],
          [/\b\d+\.\d+\b/, 'number.float'],
          [/\b\d+\b/, 'number'],
          [/\/\/.*$/, 'comment'],
          [/{/, 'delimiter.curly', '@object'],
        ],
        object: [
          [/\}/, 'delimiter.curly', '@pop'],
          [/\w+/, 'variable'],
          [/:/, 'delimiter'],
          [/,/, 'delimiter'],
        ],
      }
    })

    monaco.editor.defineTheme('nexus-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'keyword', foreground: '569CD6' },
        { token: 'keyword.control', foreground: 'C586C0' },
        { token: 'string', foreground: 'CE9178' },
        { token: 'number', foreground: 'B5CEA8' },
        { token: 'comment', foreground: '6A9955' },
        { token: 'variable', foreground: '9CDCFE' },
      ],
      colors: {
        'editor.background': '#1e1e1e',
      }
    })

    editor.updateOptions({
      theme: 'nexus-dark',
      fontSize: 14,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      automaticLayout: true,
    })
  }

  const handleCodeChange = (value: string | undefined) => {
    const newCode = value || ''
    setCode(newCode)
    onCodeChange?.(newCode)
  }

  const runCode = async () => {
    if (!code.trim()) {
      toast.error('Please enter some code to run')
      return
    }

    setIsRunning(true)
    setOutput('Running...')

    try {
      let result

      switch (selectedLanguage) {
        case 'nexuslang':
          result = await developerAPI.executeCode(code, 'nexuslang')
          break
        case 'python':
          result = await developerAPI.runPython(code)
          break
        case 'javascript':
          result = await developerAPI.runJavaScript(code)
          break
        default:
          throw new Error(`Unsupported language: ${selectedLanguage}`)
      }

      setOutput(result.output || result.result || 'Code executed successfully')
      toast.success('Code executed successfully')
    } catch (error: any) {
      const errorMessage = error.message || 'Execution failed'
      setOutput(`Error: ${errorMessage}`)
      toast.error('Code execution failed')
    } finally {
      setIsRunning(false)
    }
  }

  const saveCode = () => {
    const blob = new Blob([code], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `code.${selectedLanguage}`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Code downloaded')
  }

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center gap-4">
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="px-3 py-1 bg-gray-700 border border-gray-600 rounded text-white text-sm"
          >
            <option value="nexuslang">NexusLang</option>
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="bash">Bash</option>
          </select>

          <button
            onClick={runCode}
            disabled={isRunning || readOnly}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded text-sm font-medium transition"
          >
            <Play className="h-4 w-4" />
            {isRunning ? 'Running...' : 'Run Code'}
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={saveCode}
            className="p-2 text-gray-400 hover:text-white transition"
            title="Download Code"
          >
            <Download className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Editor and Output */}
      <div className="flex-1 flex">
        {/* Code Editor */}
        <div className="flex-1">
          <Editor
            height="100%"
            language={selectedLanguage}
            value={code}
            onChange={handleCodeChange}
            onMount={handleEditorDidMount}
            options={{
              readOnly,
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              roundedSelection: false,
              scrollBeyondLastLine: false,
              automaticLayout: true,
              wordWrap: 'on',
              theme: 'nexus-dark',
            }}
          />
        </div>

        {/* Output Panel */}
        <div className="w-96 border-l border-gray-700 bg-gray-800">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-white font-medium">Output</h3>
          </div>
          <div className="p-4 h-full overflow-auto">
            <pre className="text-green-400 text-sm font-mono whitespace-pre-wrap">
              {output || 'Run your code to see output here...'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  )
}
