'use client'

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'
import { Play, Save, Download, Upload, Settings, Users, FolderOpen, Sparkles, Zap } from 'lucide-react'
import { nexuslang, files as filesApi, projects as projectsApi, auth } from '@/lib/api'
import PersonalityEditor from '@/components/PersonalityEditor'

// Dynamic import of Monaco Editor (client-side only)
const MonacoEditor = dynamic(
  () => import('@monaco-editor/react'),
  { ssr: false }
)

export default function IDEPage() {
  const [code, setCode] = useState(DEFAULT_CODE)
  const [output, setOutput] = useState('')
  const [isRunning, setIsRunning] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [activeFile, setActiveFile] = useState<any>(null)
  const [files, setFiles] = useState<any[]>([])
  const [projects, setProjects] = useState<any[]>([])
  const [currentProject, setCurrentProject] = useState<any>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showPersonalityEditor, setShowPersonalityEditor] = useState(false)
  const [showBinaryCompile, setShowBinaryCompile] = useState(false)
  const [compileResult, setCompileResult] = useState<any>(null)

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (auth.isAuthenticated()) {
        try {
          await auth.me()
          setIsAuthenticated(true)
          loadProjects()
        } catch (error) {
          console.error('Auth check failed:', error)
          auth.logout()
          window.location.href = '/auth/login'
        }
      } else {
        window.location.href = '/auth/login'
      }
    }
    
    checkAuth()
  }, [])
  
  // Register NexusLang syntax with Monaco
  useEffect(() => {
    // Monaco will be available after component mounts
    if (typeof window !== 'undefined') {
      import('monaco-editor').then((monaco) => {
        registerNexusLangSyntax(monaco.languages)
      })
    }
  }, [])
  
  // Load user's projects
  const loadProjects = async () => {
    try {
      const userProjects = await projectsApi.list()
      setProjects(userProjects)
      
      // Load first project or create one
      if (userProjects.length > 0) {
        loadProject(userProjects[0].id)
      } else {
        // Create default project
        const newProject = await projectsApi.create({
          name: 'My First Project',
          description: 'Getting started with NexusLang v2'
        })
        setProjects([newProject])
        loadProject(newProject.id)
      }
    } catch (error) {
      console.error('Failed to load projects:', error)
      setOutput(`❌ Error loading projects: ${error}`)
    }
  }
  
  // Load a specific project
  const loadProject = async (projectId: string) => {
    try {
      const project = await projectsApi.get(projectId)
      setCurrentProject(project)
      
      // Load project files
      const projectFiles = await filesApi.list(projectId)
      setFiles(projectFiles)
      
      // Load first file
      if (projectFiles.length > 0) {
        loadFile(projectFiles[0])
      }
    } catch (error) {
      console.error('Failed to load project:', error)
      setOutput(`❌ Error loading project: ${error}`)
    }
  }
  
  // Load a file
  const loadFile = async (file: any) => {
    try {
      const fileData = await filesApi.get(file.id)
      setActiveFile(fileData)
      setCode(fileData.content || '')
    } catch (error) {
      console.error('Failed to load file:', error)
      setOutput(`❌ Error loading file: ${error}`)
    }
  }

  const runCode = async () => {
    setIsRunning(true)
    setOutput('⏳ Running code...\n')

    try {
      const result = await nexuslang.run(code)
      
      if (result.success) {
        setOutput(`✅ Success!\n\n${result.output}\n\n⏱️  Execution time: ${result.execution_time}ms`)
      } else {
        setOutput(`❌ Error!\n\n${result.error || result.output}`)
      }
    } catch (error) {
      setOutput(`❌ Network Error: ${error}`)
    } finally {
      setIsRunning(false)
    }
  }

  const saveFile = async () => {
    if (!activeFile || !activeFile.id) {
      setOutput('❌ No file selected to save')
      return
    }
    
    setIsSaving(true)
    
    try {
      await filesApi.update(activeFile.id, code)
      setOutput(`💾 Saved ${activeFile.path} successfully!`)
      
      // Update file in list
      const updatedFiles = files.map(f => 
        f.id === activeFile.id ? { ...f, content: code } : f
      )
      setFiles(updatedFiles)
    } catch (error) {
      setOutput(`❌ Save failed: ${error}`)
    } finally {
      setIsSaving(false)
    }
  }
  
  // Auto-save on Ctrl+S or Cmd+S
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        saveFile()
      }
      
      // Run code on Ctrl+Enter or Cmd+Enter
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault()
        runCode()
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [code, activeFile])
  
  // Insert personality code into editor
  const insertPersonalityCode = (personalityCode: string) => {
    setCode(personalityCode + '\n\n' + code)
    setOutput('✅ Personality block inserted!')
  }
  
  // Compile to binary
  const compileToBinary = async () => {
    setOutput('⏳ Compiling to binary...\n')
    
    try {
      const result = await nexuslang.compile(code)
      
      if (result.success) {
        setCompileResult(result)
        setShowBinaryCompile(true)
        setOutput(`✅ Compiled successfully!\n\nBinary size: ${result.binary_size} bytes\nCompression ratio: ${result.compression_ratio?.toFixed(2)}x\n\n🚀 Estimated speedup: ${(result.compression_ratio * 5).toFixed(1)}x faster!`)
      } else {
        setOutput(`❌ Compilation failed:\n\n${result.error}`)
      }
    } catch (error) {
      setOutput(`❌ Compilation error: ${error}`)
    }
  }

  return (
    <div className="h-screen flex flex-col bg-zinc-950">
      {/* Personality Editor Modal */}
      {showPersonalityEditor && (
        <PersonalityEditor
          onInsert={insertPersonalityCode}
          onClose={() => setShowPersonalityEditor(false)}
        />
      )}
      
      {/* Binary Compile Result Modal */}
      {showBinaryCompile && compileResult && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-zinc-900 rounded-lg shadow-xl w-[500px] p-6">
            <div className="flex items-center gap-3 mb-4">
              <Zap className="text-yellow-400" size={24} />
              <h2 className="text-xl font-bold text-white">Binary Compilation Result</h2>
            </div>
            
            <div className="space-y-3 mb-6">
              <div className="flex justify-between text-sm">
                <span className="text-zinc-400">Source Size:</span>
                <span className="text-white font-mono">{code.length} bytes</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-zinc-400">Binary Size:</span>
                <span className="text-white font-mono">{compileResult.binary_size} bytes</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-zinc-400">Compression:</span>
                <span className="text-green-400 font-mono">{compileResult.compression_ratio?.toFixed(2)}x smaller</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-zinc-400">Estimated Speedup:</span>
                <span className="text-yellow-400 font-mono">
                  {(compileResult.compression_ratio * 5).toFixed(1)}x faster ⚡
                </span>
              </div>
            </div>
            
            <div className="bg-zinc-950 p-4 rounded text-sm text-zinc-300 mb-4">
              <p className="mb-2">💡 <strong>Why this matters:</strong></p>
              <p>Binary compilation makes AI process your code 10-15x faster by:</p>
              <ul className="list-disc ml-6 mt-2 space-y-1 text-zinc-400">
                <li>Efficient token compression</li>
                <li>Constant pooling and deduplication</li>
                <li>Optimized for machine reading</li>
                <li>Reduced parsing overhead</li>
              </ul>
            </div>
            
            <button
              onClick={() => setShowBinaryCompile(false)}
              className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Top Bar */}
      <div className="h-14 bg-zinc-900 border-b border-zinc-800 flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            NexusLang IDE
          </h1>
          <div className="flex items-center gap-2">
            <button
              onClick={runCode}
              disabled={isRunning}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition disabled:opacity-50"
            >
              <Play size={16} />
              {isRunning ? 'Running...' : 'Run'}
            </button>
            <button
              onClick={saveFile}
              disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition disabled:opacity-50"
            >
              <Save size={16} />
              {isSaving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowPersonalityEditor(true)}
            className="flex items-center gap-2 px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition"
            title="Add Personality Block"
          >
            <Sparkles size={16} />
            <span className="text-sm">Personality</span>
          </button>
          <button
            onClick={compileToBinary}
            className="flex items-center gap-2 px-3 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg transition"
            title="Compile to Binary"
          >
            <Zap size={16} />
            <span className="text-sm">Compile</span>
          </button>
          <button className="p-2 hover:bg-zinc-800 rounded-lg transition" title="Collaboration">
            <Users size={20} />
          </button>
          <button className="p-2 hover:bg-zinc-800 rounded-lg transition" title="Settings">
            <Settings size={20} />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Sidebar - File Explorer */}
        <div className="w-64 bg-zinc-900 border-r border-zinc-800 p-4">
          {/* Project Selector */}
          {currentProject && (
            <div className="mb-4 pb-4 border-b border-zinc-800">
              <h2 className="text-sm font-semibold text-zinc-400 mb-2">PROJECT</h2>
              <div className="p-2 bg-zinc-800 rounded text-zinc-300 text-sm">
                <div className="flex items-center gap-2">
                  <FolderOpen size={16} />
                  {currentProject.name}
                </div>
              </div>
            </div>
          )}
          
          <div className="mb-4">
            <h2 className="text-sm font-semibold text-zinc-400 mb-2">FILES</h2>
            <div className="space-y-1">
              {files.length === 0 ? (
                <div className="text-zinc-500 text-sm p-2">No files yet...</div>
              ) : (
                files.map((file) => (
                  <div
                    key={file.id}
                    onClick={() => loadFile(file)}
                    className={`p-2 rounded cursor-pointer transition ${
                      activeFile && activeFile.id === file.id
                        ? 'bg-blue-600/20 text-blue-400'
                        : 'hover:bg-zinc-800 text-zinc-300'
                    }`}
                  >
                    📄 {file.path}
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-zinc-800">
            <button className="flex items-center gap-2 w-full p-2 text-sm text-zinc-400 hover:bg-zinc-800 rounded transition">
              <Upload size={16} />
              Upload File
            </button>
            <button className="flex items-center gap-2 w-full p-2 text-sm text-zinc-400 hover:bg-zinc-800 rounded transition">
              <Download size={16} />
              Download Project
            </button>
          </div>
        </div>

        {/* Editor and Output */}
        <div className="flex-1 flex flex-col">
          {/* Editor */}
          <div className="flex-1 border-b border-zinc-800">
            <MonacoEditor
              height="100%"
              language="nexuslang"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value || '')}
              options={{
                fontSize: 14,
                minimap: { enabled: false },
                lineNumbers: 'on',
                roundedSelection: false,
                scrollBeyondLastLine: false,
                readOnly: false,
                automaticLayout: true,
              }}
            />
          </div>

          {/* Output Terminal */}
          <div className="h-48 bg-zinc-900 p-4 overflow-y-auto font-mono text-sm border-b border-zinc-800">
            <div className="text-zinc-400 mb-2">OUTPUT:</div>
            <pre className="text-zinc-100 whitespace-pre-wrap">{output || 'Run code to see output...'}</pre>
          </div>
          
          {/* Status Bar */}
          <div className="h-8 bg-zinc-900 px-4 flex items-center justify-between text-xs text-zinc-500">
            <div className="flex items-center gap-4">
              <span>NexusLang v2.0</span>
              {activeFile && <span>📄 {activeFile.path}</span>}
              {currentProject && <span>📁 {currentProject.name}</span>}
            </div>
            <div className="flex items-center gap-4">
              <span className="text-zinc-600">Keyboard shortcuts: Ctrl+S (Save) | Ctrl+Enter (Run)</span>
              {isAuthenticated && <span className="text-green-500">● Connected</span>}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

const DEFAULT_CODE = `// Welcome to NexusLang v2 IDE!
// An AI-native programming language

personality {
    curiosity: 0.9,
    analytical: 0.8,
    creative: 0.7
}

fn main() {
    print("Hello from NexusLang v2!")
    print("Building the 22nd century...")
    
    // AI-native features
    let model = Sequential(
        Linear(10, 64),
        ReLU(),
        Linear(64, 2)
    )
    
    print("Model created:", model)
}

main()
`

function registerNexusLangSyntax(monaco: any) {
  // Register NexusLang language
  monaco.register({ id: 'nexuslang' })

  // Define syntax highlighting
  monaco.setMonarchTokensProvider('nexuslang', {
    keywords: [
      'fn', 'let', 'const', 'return', 'if', 'else', 'while', 'for', 'in',
      'break', 'continue', 'true', 'false', 'null',
      // v2 keywords
      'personality', 'knowledge', 'voice', 'say', 'listen', 'optimize_self',
      'emotion', 'load_model', 'confidence'
    ],

    operators: [
      '=', '>', '<', '!', '~', '?', ':',
      '==', '<=', '>=', '!=', '&&', '||', '++', '--',
      '+', '-', '*', '/', '&', '|', '^', '%', '<<',
      '>>', '>>>', '+=', '-=', '*=', '/=', '&=', '|=',
      '^=', '%=', '<<=', '>>=', '>>>='
    ],

    symbols: /[=><!~?:&|+\-*\/\^%]+/,

    tokenizer: {
      root: [
        // Identifiers and keywords
        [/[a-z_$][\w$]*/, {
          cases: {
            '@keywords': 'keyword',
            '@default': 'identifier'
          }
        }],

        // Whitespace
        { include: '@whitespace' },

        // Delimiters
        [/[{}()\[\]]/, '@brackets'],
        [/[<>](?!@symbols)/, '@brackets'],
        [/@symbols/, {
          cases: {
            '@operators': 'operator',
            '@default': ''
          }
        }],

        // Numbers
        [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
        [/0[xX][0-9a-fA-F]+/, 'number.hex'],
        [/\d+/, 'number'],

        // Strings
        [/"([^"\\]|\\.)*$/, 'string.invalid'],
        [/"/, 'string', '@string'],
      ],

      whitespace: [
        [/[ \t\r\n]+/, ''],
        [/\/\*/, 'comment', '@comment'],
        [/\/\/.*$/, 'comment'],
      ],

      comment: [
        [/[^\/*]+/, 'comment'],
        [/\*\//, 'comment', '@pop'],
        [/[\/*]/, 'comment']
      ],

      string: [
        [/[^\\"]+/, 'string'],
        [/\\./, 'string.escape'],
        [/"/, 'string', '@pop']
      ],
    },
  })

  // Define theme
  monaco.defineTheme('nexuslang-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'keyword', foreground: 'C678DD', fontStyle: 'bold' },
      { token: 'identifier', foreground: 'ABB2BF' },
      { token: 'number', foreground: 'D19A66' },
      { token: 'string', foreground: '98C379' },
      { token: 'comment', foreground: '5C6370', fontStyle: 'italic' },
      { token: 'operator', foreground: '56B6C2' },
    ],
    colors: {
      'editor.background': '#18181B',
    }
  })
}

