'use client'

import { useEffect, useRef } from 'react'
import * as monaco from 'monaco-editor'

interface MonacoEditorProps {
  value: string
  onChange: (value: string) => void
  language?: string
  theme?: string
  className?: string
  readOnly?: boolean
  minimap?: boolean
  fontSize?: number
  wordWrap?: boolean
}

export function MonacoEditor({
  value,
  onChange,
  language = 'typescript',
  theme = 'vs-dark',
  className = '',
  readOnly = false,
  minimap = true,
  fontSize = 14,
  wordWrap = false
}: MonacoEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null)
  const monacoRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null)
  const subscriptionRef = useRef<monaco.IDisposable | null>(null)

  useEffect(() => {
    if (!editorRef.current) return

    // Initialize Monaco Editor
    monacoRef.current = monaco.editor.create(editorRef.current, {
      value,
      language,
      theme,
      automaticLayout: true,
      minimap: { enabled: minimap },
      fontSize,
      fontFamily: 'JetBrains Mono, SF Mono, Monaco, Consolas, monospace',
      lineNumbers: 'on',
      roundedSelection: false,
      scrollBeyondLastLine: false,
      readOnly,
      wordWrap: wordWrap ? 'on' : 'off',
      tabSize: 2,
      insertSpaces: true,
      detectIndentation: true,
      folding: true,
      foldingStrategy: 'indentation',
      showFoldingControls: 'mouseover',
      unfoldOnClickAfterEndOfLine: true,
      renderWhitespace: 'selection',
      renderControlCharacters: true,
      renderLineHighlight: 'line',
      selectionHighlight: true,
      occurrencesHighlight: true,
      codeLens: true,
      lightbulb: {
        enabled: true
      },
      quickSuggestions: {
        other: true,
        comments: true,
        strings: true
      },
      parameterHints: {
        enabled: true
      },
      hover: {
        enabled: true
      },
      contextmenu: true,
      mouseWheelZoom: true,
      smoothScrolling: true,
      cursorBlinking: 'blink',
      cursorSmoothCaretAnimation: true,
      renderFinalNewline: true,
      rulers: [80, 120],
      guides: {
        bracketPairs: true,
        indentation: true
      }
    })

    // Listen for changes
    subscriptionRef.current = monacoRef.current.onDidChangeModelContent(() => {
      const newValue = monacoRef.current?.getValue() || ''
      onChange(newValue)
    })

    // Configure NexusLang syntax highlighting if needed
    if (language === 'nexuslang' || language === 'nx') {
      configureNexusLangSyntax()
    }

    return () => {
      subscriptionRef.current?.dispose()
      monacoRef.current?.dispose()
    }
  }, [language, theme, readOnly, minimap, fontSize, wordWrap])

  // Update value when prop changes
  useEffect(() => {
    if (monacoRef.current && value !== monacoRef.current.getValue()) {
      monacoRef.current.setValue(value)
    }
  }, [value])

  const configureNexusLangSyntax = () => {
    // Register NexusLang language
    monaco.languages.register({ id: 'nexuslang' })

    // Set syntax highlighting rules
    monaco.languages.setMonarchTokenizer('nexuslang', {
      tokenizer: {
        root: [
          // Keywords
          [/\b(function|if|else|for|while|return|let|const|var|import|export|class|interface|type|enum)\b/, 'keyword'],

          // Types
          [/\b(int|string|bool|float|void|any)\b/, 'type'],

          // Built-in functions
          [/\b(print|len|append|slice|range)\b/, 'predefined'],

          // Strings
          [/"([^"\\]|\\.)*$/, 'string.invalid'], // non-terminated string
          [/"([^"\\]|\\.)*"/, 'string'],

          // Numbers
          [/\d+/, 'number'],

          // Comments
          [/\/\/.*$/, 'comment'],
          [/\/\*/, 'comment', '@comment'],

          // Operators
          [/[+\-*/%=<>!&|]/, 'operator'],

          // Brackets
          [/[{}()[\]]/, '@brackets'],
        ],

        comment: [
          [/[^/*]+/, 'comment'],
          [/\*\//, 'comment', '@pop'],
          [/[/*]/, 'comment']
        ]
      }
    })

    // Configure language features
    monaco.languages.setLanguageConfiguration('nexuslang', {
      comments: {
        lineComment: '//',
        blockComment: ['/*', '*/']
      },
      brackets: [
        ['{', '}'],
        ['[', ']'],
        ['(', ')']
      ],
      autoClosingPairs: [
        { open: '{', close: '}' },
        { open: '[', close: ']' },
        { open: '(', close: ')' },
        { open: '"', close: '"', notIn: ['string'] }
      ],
      surroundingPairs: [
        { open: '{', close: '}' },
        { open: '[', close: ']' },
        { open: '(', close: ')' },
        { open: '"', close: '"' }
      ]
    })
  }

  const handleResize = () => {
    monacoRef.current?.layout()
  }

  useEffect(() => {
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <div className={`relative ${className}`}>
      <div
        ref={editorRef}
        className="w-full h-full min-h-[400px] rounded-lg overflow-hidden"
        style={{ height: '100%' }}
      />

      {/* Loading indicator */}
      {!monacoRef.current && (
        <div className="absolute inset-0 flex items-center justify-center bg-surface">
          <div className="text-center">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
            <p className="text-sm text-foreground-muted">Loading editor...</p>
          </div>
        </div>
      )}

      {/* Accessibility: Screen reader description */}
      <div className="sr-only">
        Code editor for {language} files. Current content: {value.substring(0, 100)}...
      </div>
    </div>
  )
}

export default MonacoEditor