// Image Generation Component for galion.studio
// Generate images using DALL-E and Stable Diffusion

import { useState } from 'react'
import apiClient from '../lib/api-client'

export default function ImageGenerator() {
  const [prompt, setPrompt] = useState('')
  const [model, setModel] = useState('stability-ai/stable-diffusion-xl')
  const [size, setSize] = useState('1024x1024')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const generate = async () => {
    if (!prompt.trim()) return
    
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const data = await apiClient.generateImage(prompt, model, size)
      setResult(data)
    } catch (err: any) {
      setError(err.message || 'Generation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{padding: '20px', maxWidth: '800px', margin: '0 auto'}}>
      <h2>🎨 Image Generation</h2>
      
      <div style={{marginTop: '20px'}}>
        <label>Prompt:</label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe the image you want to create..."
          style={{
            width: '100%',
            minHeight: '100px',
            padding: '10px',
            fontSize: '16px',
            borderRadius: '8px',
            border: '1px solid #ccc'
          }}
        />
      </div>

      <div style={{marginTop: '20px', display: 'flex', gap: '20px'}}>
        <div>
          <label>Model:</label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            style={{
              padding: '10px',
              fontSize: '16px',
              borderRadius: '8px',
              border: '1px solid #ccc'
            }}
          >
            <option value="stability-ai/stable-diffusion-xl">Stable Diffusion XL</option>
            <option value="openai/dall-e-3">DALL-E 3</option>
          </select>
        </div>

        <div>
          <label>Size:</label>
          <select
            value={size}
            onChange={(e) => setSize(e.target.value)}
            style={{
              padding: '10px',
              fontSize: '16px',
              borderRadius: '8px',
              border: '1px solid #ccc'
            }}
          >
            <option value="1024x1024">1024x1024 (Square)</option>
            <option value="1024x1792">1024x1792 (Portrait)</option>
            <option value="1792x1024">1792x1024 (Landscape)</option>
          </select>
        </div>
      </div>

      <button
        onClick={generate}
        disabled={loading || !prompt.trim()}
        style={{
          marginTop: '20px',
          padding: '12px 32px',
          fontSize: '16px',
          backgroundColor: loading ? '#999' : '#6366f1',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Generating...' : 'Generate Image'}
      </button>

      {error && (
        <div style={{
          marginTop: '20px',
          padding: '15px',
          backgroundColor: '#fee',
          color: '#c00',
          borderRadius: '8px'
        }}>
          ❌ {error}
        </div>
      )}

      {result && (
        <div style={{marginTop: '30px'}}>
          <h3>Generated Image:</h3>
          <img
            src={result.url}
            alt={prompt}
            style={{
              maxWidth: '100%',
              borderRadius: '12px',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}
          />
          <p style={{marginTop: '10px', color: '#666'}}>
            Credits used: {result.credits_used} | Model: {result.model}
          </p>
        </div>
      )}
    </div>
  )
}

