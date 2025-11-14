'use client'

import React, { useRef, useEffect, useState } from 'react'
import Editor, { Monaco } from '@monaco-editor/react'
import * as monaco from 'monaco-editor'

interface MonacoEditorProps {
  value: string
  onChange: (value: string) => void
  language?: string
  theme?: 'vs-dark' | 'light'
  height?: string | number
  readOnly?: boolean
  onMount?: (editor: monaco.editor.IStandaloneCodeEditor, monaco: Monaco) => void
}

const MonacoEditor: React.FC<MonacoEditorProps> = ({
  value,
  onChange,
  language = 'nexuslang',
  theme = 'vs-dark',
  height = '400px',
  readOnly = false,
  onMount
}) => {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null)
  const [isEditorReady, setIsEditorReady] = useState(false)

  const handleEditorDidMount = (editor: monaco.editor.IStandaloneCodeEditor, monaco: Monaco) => {
    editorRef.current = editor
    setIsEditorReady(true)

    // Configure NexusLang syntax highlighting
    monaco.languages.register({ id: 'nexuslang' })

    monaco.languages.setMonarchTokensProvider('nexuslang', {
      tokenizer: {
        root: [
          // Keywords
          [/\b(personality|fn|let|const|if|else|for|while|return|break|continue|try|catch|import|from|as)\b/, 'keyword'],

          // Built-in functions
          [/\b(print|say|listen|knowledge|ai|compile|run)\b/, 'keyword.control'],

          // Types
          [/\b(string|int|float|bool|array|object)\b/, 'type'],

          // Personality traits
          [/\b(curiosity|analytical|creative|empathetic|adaptability|transparency|helpfulness|precision|innovation|patience)\b/, 'type.parameter'],

          // Comments
          [/\/\/.*$/, 'comment'],
          [/#.*$/, 'comment'],

          // Strings
          [/"([^"\\]|\\.)*$/, 'string.invalid'], // non-terminated string
          [/"([^"\\]|\\.)*"/, 'string'],
          [/'([^'\\]|\\.)*$/, 'string.invalid'], // non-terminated string
          [/'([^'\\]|\\.)*'/, 'string'],

          // Numbers
          [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
          [/\d+/, 'number'],

          // Operators
          [/[\+\-\*\/\%\&\|\^\~\!\=\<\>]+/, 'operator'],

          // Brackets
          [/[{}()\[\]]/, '@brackets'],

          // Identifiers
          [/[a-zA-Z_$][a-zA-Z0-9_$]*/, 'identifier'],
        ]
      }
    })

    // Define theme
    monaco.editor.defineTheme('nexuslang-theme', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'keyword', foreground: '569CD6' },
        { token: 'keyword.control', foreground: 'C586C0' },
        { token: 'type', foreground: '4EC9B0' },
        { token: 'type.parameter', foreground: '9CDCFE' },
        { token: 'string', foreground: 'CE9178' },
        { token: 'number', foreground: 'B5CEA8' },
        { token: 'comment', foreground: '6A9955' },
        { token: 'operator', foreground: 'D4D4D4' },
        { token: 'identifier', foreground: 'D4D4D4' }
      ],
      colors: {
        'editor.background': '#1e1e1e',
        'editor.foreground': '#d4d4d4',
        'editor.lineHighlightBackground': '#2d2d30',
        'editor.selectionBackground': '#264f78',
        'editor.inactiveSelectionBackground': '#3a3d41'
      }
    })

    // Set the theme
    monaco.editor.setTheme('nexuslang-theme')

    // Configure editor options
    editor.updateOptions({
      fontSize: 14,
      fontFamily: 'Fira Code, Consolas, monospace',
      lineNumbers: 'on',
      roundedSelection: false,
      scrollBeyondLastLine: false,
      automaticLayout: true,
      minimap: { enabled: true },
      wordWrap: 'on',
      tabSize: 2,
      insertSpaces: true,
      detectIndentation: false,
      folding: true,
      lineDecorationsWidth: 10,
      lineNumbersMinChars: 3,
      glyphMargin: true,
      contextmenu: true,
      mouseWheelZoom: true,
      quickSuggestions: {
        other: true,
        comments: true,
        strings: true
      },
      parameterHints: {
        enabled: true
      },
      suggestOnTriggerCharacters: true,
      acceptSuggestionOnEnter: 'on',
      tabCompletion: 'on',
      wordBasedSuggestions: true,
      snippetSuggestions: 'inline'
    })

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      // Save functionality can be added here
      console.log('Save shortcut pressed')
    })

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      // Run code functionality can be added here
      console.log('Run shortcut pressed')
    })

    // Call onMount callback if provided
    if (onMount) {
      onMount(editor, monaco)
    }
  }

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      onChange(value)
    }
  }

  return (
    <div className="w-full h-full border border-gray-600 rounded-lg overflow-hidden">
      <Editor
        height={height}
        language={language}
        value={value}
        theme={theme === 'vs-dark' ? 'nexuslang-theme' : theme}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        options={{
          readOnly,
          automaticLayout: true,
          scrollBeyondLastLine: false,
          minimap: { enabled: true },
          fontSize: 14,
          fontFamily: 'Fira Code, Consolas, monospace',
          lineNumbers: 'on',
          roundedSelection: false,
          wordWrap: 'on',
          tabSize: 2,
          insertSpaces: true,
          detectIndentation: false,
          folding: true,
          lineDecorationsWidth: 10,
          lineNumbersMinChars: 3,
          glyphMargin: true,
          contextmenu: true,
          mouseWheelZoom: true,
          quickSuggestions: {
            other: true,
            comments: true,
            strings: true
          },
          parameterHints: {
            enabled: true
          },
          suggestOnTriggerCharacters: true,
          acceptSuggestionOnEnter: 'on',
          tabCompletion: 'on',
          wordBasedSuggestions: true,
          snippetSuggestions: 'inline'
        }}
        loading={
          <div className="flex items-center justify-center h-full bg-gray-900 text-gray-400">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mr-3"></div>
            Loading NexusLang Editor...
          </div>
        }
      />
    </div>
  )
}

export default MonacoEditor
