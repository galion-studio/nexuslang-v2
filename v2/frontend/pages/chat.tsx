// Full-Page AI Chat Interface
import Head from 'next/head'
import { useState } from 'react'

interface Message {
  role: string
  content: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input.trim() }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const token = localStorage.getItem('access_token')

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          model: 'anthropic/claude-3.5-sonnet'
        })
      })

      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.content }])

    } catch (err: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err.message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{height: '100vh', display: 'flex', flexDirection: 'column'}}>
      <Head>
        <title>AI Chat - NexusLang</title>
      </Head>

      <div style={{
        padding: '20px',
        backgroundColor: '#6366f1',
        color: 'white'
      }}>
        <h1>🤖 AI Chat</h1>
        <p>Chat with Claude 3.5 Sonnet</p>
      </div>

      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px',
        backgroundColor: '#f9f9f9'
      }}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              maxWidth: '700px',
              margin: '0 auto 20px auto',
              padding: '15px 20px',
              borderRadius: '12px',
              backgroundColor: msg.role === 'user' ? '#6366f1' : 'white',
              color: msg.role === 'user' ? 'white' : '#333',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
          >
            <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong>
            <div style={{marginTop: '5px', whiteSpace: 'pre-wrap'}}>{msg.content}</div>
          </div>
        ))}
        
        {loading && (
          <div style={{textAlign: 'center', color: '#666'}}>
            AI is thinking...
          </div>
        )}
      </div>

      <div style={{
        padding: '20px',
        backgroundColor: 'white',
        borderTop: '1px solid #ddd'
      }}>
        <div style={{maxWidth: '700px', margin: '0 auto', display: 'flex', gap: '10px'}}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            style={{
              flex: 1,
              padding: '12px',
              fontSize: '16px',
              border: '1px solid #ddd',
              borderRadius: '8px'
            }}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            style={{
              padding: '12px 32px',
              fontSize: '16px',
              backgroundColor: loading || !input.trim() ? '#ccc' : '#6366f1',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: loading || !input.trim() ? 'not-allowed' : 'pointer'
            }}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

