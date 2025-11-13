// Code Editor Component using Monaco Editor
// Web IDE for NexusLang code execution

import { useState } from 'react'

export default function CodeEditor() {
  const [code, setCode] = useState(`# Welcome to NexusLang!
print("Hello, NexusLang!")

# Use AI capabilities
response = ai.chat("What is quantum computing?")
print(response)
`)
  const [output, setOutput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const executeCode = async () => {
    setLoading(true)
    setError('')
    setOutput('')

    try {
      const token = localStorage.getItem('access_token')
      
      if (!token) {
        setError('Please login to execute code')
        setLoading(false)
        return
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/nexuslang/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          code,
          language: 'nexuslang',
          timeout: 30
        })
      })

      const data = await response.json()

      if (data.success) {
        setOutput(data.stdout || 'Execution completed')
        if (data.stderr) {
          setOutput(prev => prev + '\n\nWarnings:\n' + data.stderr)
        }
      } else {
        setError(data.stderr || data.error || 'Execution failed')
      }

    } catch (err: any) {
      setError(err.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{display: 'flex', flexDirection: 'column', height: '600px', border: '1px solid #ccc', borderRadius: '8px'}}>
      {/* Toolbar */}
      <div style={{
        padding: '10px',
        backgroundColor: '#2d2d2d',
        color: 'white',
        borderTopLeftRadius: '8px',
        borderTopRightRadius: '8px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <span>📝 NexusLang Editor</span>
        <button
          onClick={executeCode}
          disabled={loading}
          style={{
            padding: '8px 16px',
            backgroundColor: loading ? '#666' : '#22c55e',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? '⏳ Running...' : '▶️ Run Code'}
        </button>
      </div>

      {/* Code Editor */}
      <textarea
        value={code}
        onChange={(e) => setCode(e.target.value)}
        spellCheck={false}
        style={{
          flex: 1,
          padding: '15px',
          fontFamily: 'monospace',
          fontSize: '14px',
          border: 'none',
          outline: 'none',
          resize: 'none',
          backgroundColor: '#1e1e1e',
          color: '#d4d4d4'
        }}
      />

      {/* Output Terminal */}
      <div style={{
        height: '200px',
        padding: '15px',
        backgroundColor: '#000',
        color: '#0f0',
        fontFamily: 'monospace',
        fontSize: '13px',
        overflow: 'auto',
        borderBottomLeftRadius: '8px',
        borderBottomRightRadius: '8px',
        whiteSpace: 'pre-wrap'
      }}>
        {output && <div>{output}</div>}
        {error && <div style={{color: '#f00'}}>ERROR: {error}</div>}
        {!output && !error && <div style={{color: '#666'}}>Output will appear here...</div>}
      </div>
    </div>
  )
}

