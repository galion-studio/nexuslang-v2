'use client'

import { useState } from 'react'
import { Sparkles, Download } from 'lucide-react'

export default function ImageGenerationPage() {
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedImage, setGeneratedImage] = useState<string | null>(null)
  
  const generateImage = async () => {
    if (!prompt.trim() || isGenerating) return
    
    setIsGenerating(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/ai/generate/image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          prompt,
          model: 'stable-diffusion-xl',
          size: '1024x1024'
        })
      })
      
      const data = await response.json()
      setGeneratedImage(data.image_url)
    } catch (error) {
      console.error('Generation failed:', error)
    } finally {
      setIsGenerating(false)
    }
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">Image Generation</h1>
        
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Input */}
          <div className="space-y-4">
            <div>
              <label className="block text-white font-medium mb-2">Describe your image</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="A futuristic AI laboratory with holographic displays..."
                rows={6}
                className="w-full px-4 py-3 bg-zinc-900 text-white rounded-lg border border-zinc-700 focus:border-purple-500 outline-none"
              />
            </div>
            
            <button
              onClick={generateImage}
              disabled={!prompt.trim() || isGenerating}
              className="w-full px-6 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-zinc-700 disabled:to-zinc-700 text-white rounded-lg font-bold transition flex items-center justify-center gap-2"
            >
              {isGenerating ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  Generate Image (5 credits)
                </>
              )}
            </button>
          </div>
          
          {/* Output */}
          <div className="bg-zinc-900 rounded-lg border border-zinc-800 p-6 flex items-center justify-center min-h-[400px]">
            {generatedImage ? (
              <div>
                <img src={generatedImage} alt="Generated" className="rounded-lg max-w-full" />
                <button className="mt-4 w-full px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg flex items-center justify-center gap-2">
                  <Download size={18} />
                  Download
                </button>
              </div>
            ) : (
              <p className="text-zinc-500">Your generated image will appear here</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

