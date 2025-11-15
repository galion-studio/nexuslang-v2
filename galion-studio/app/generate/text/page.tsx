'use client'

import { useState } from 'react'
import { Sparkles, Copy } from 'lucide-react'

export default function TextGenerationPage() {
  const [prompt, setPrompt] = useState('')
  const [generatedText, setGeneratedText] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [model, setModel] = useState('anthropic/claude-3.5-sonnet')
  
  const generateText = async () => {
    if (!prompt.trim() || isGenerating) return
    
    setIsGenerating(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          messages: [{ role: 'user', content: prompt }],
          model,
          max_tokens: 2000
        })
      })
      
      const data = await response.json()
      setGeneratedText(data.content)
    } catch (error) {
      console.error('Generation failed:', error)
    } finally {
      setIsGenerating(false)
    }
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">Text Generation</h1>
        
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Input */}
          <div className="space-y-4">
            <div>
              <label className="block text-white font-medium mb-2">What do you want to create?</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Write a blog post about AI trends in 2026..."
                rows={8}
                className="w-full px-4 py-3 bg-zinc-900 text-white rounded-lg border border-zinc-700 focus:border-blue-500 outline-none"
              />
            </div>
            
            <div>
              <label className="block text-white font-medium mb-2">Model</label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full px-4 py-3 bg-zinc-900 text-white rounded-lg border border-zinc-700"
              >
                <option value="anthropic/claude-3.5-sonnet">Claude Sonnet (Best quality)</option>
                <option value="openai/gpt-4-turbo">GPT-4 Turbo</option>
                <option value="openai/gpt-3.5-turbo">GPT-3.5 (Fastest)</option>
                <option value="google/gemini-pro">Gemini Pro</option>
              </select>
            </div>
            
            <button
              onClick={generateText}
              disabled={!prompt.trim() || isGenerating}
              className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-zinc-700 disabled:to-zinc-700 text-white rounded-lg font-bold transition flex items-center justify-center gap-2"
            >
              {isGenerating ? 'Generating...' : <><Sparkles size={20} />Generate Text (2 credits)</>}
            </button>
          </div>
          
          {/* Output */}
          <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-semibold">Generated Content</h3>
              {generatedText && (
                <button
                  onClick={() => navigator.clipboard.writeText(generatedText)}
                  className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 text-white rounded text-sm flex items-center gap-2"
                >
                  <Copy size={14} />
                  Copy
                </button>
              )}
            </div>
            <div className="prose prose-invert max-w-none">
              {generatedText ? (
                <p className="text-zinc-300 whitespace-pre-wrap">{generatedText}</p>
              ) : (
                <p className="text-zinc-500">Generated content will appear here</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

