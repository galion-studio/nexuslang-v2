/**
 * Text Generation Dashboard
 * 
 * Generate text content using AI models.
 * Supports multiple formats: articles, stories, emails, code, and more.
 */

import { useState } from 'react';
import { useRouter } from 'next/router';

// Text generation templates
const TEMPLATES = [
  { id: 'article', name: 'Article', description: 'Blog post or article' },
  { id: 'story', name: 'Story', description: 'Creative fiction or narrative' },
  { id: 'email', name: 'Email', description: 'Professional or personal email' },
  { id: 'code', name: 'Code', description: 'Programming code with explanation' },
  { id: 'marketing', name: 'Marketing', description: 'Ad copy or marketing content' },
  { id: 'social', name: 'Social Post', description: 'Social media content' },
  { id: 'custom', name: 'Custom', description: 'Free-form text generation' }
];

// AI models for text generation
const MODELS = [
  { id: 'claude-3.5-sonnet', name: 'Claude 3.5 Sonnet', description: 'Best for reasoning and analysis' },
  { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', description: 'Powerful general-purpose model' },
  { id: 'llama-3-70b', name: 'Llama 3 70B', description: 'Open-source alternative' }
];

export default function GenerateTextPage() {
  const router = useRouter();
  const [template, setTemplate] = useState('custom');
  const [model, setModel] = useState('claude-3.5-sonnet');
  const [prompt, setPrompt] = useState('');
  const [generatedText, setGeneratedText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [wordCount, setWordCount] = useState(500);
  const [tone, setTone] = useState('professional');

  // Generate text
  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setLoading(true);
    setError('');
    setGeneratedText('');

    try {
      // Build system message based on template and settings
      let systemMessage = '';
      
      if (template === 'article') {
        systemMessage = `You are a professional content writer. Write a ${tone} article of approximately ${wordCount} words.`;
      } else if (template === 'story') {
        systemMessage = `You are a creative storyteller. Write a ${tone} story of approximately ${wordCount} words.`;
      } else if (template === 'email') {
        systemMessage = `You are a professional email writer. Write a ${tone} email.`;
      } else if (template === 'code') {
        systemMessage = `You are an expert programmer. Write well-documented code with explanations.`;
      } else if (template === 'marketing') {
        systemMessage = `You are a marketing copywriter. Write compelling ${tone} marketing content.`;
      } else if (template === 'social') {
        systemMessage = `You are a social media expert. Write engaging ${tone} social media content.`;
      } else {
        systemMessage = `You are a helpful AI assistant. Generate ${tone} text content.`;
      }

      // Call AI API
      const response = await fetch('/api/v2/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          messages: [
            { role: 'system', content: systemMessage },
            { role: 'user', content: prompt }
          ],
          model: model,
          max_tokens: Math.ceil(wordCount * 1.5),  // Approximate tokens
          temperature: tone === 'creative' ? 0.9 : tone === 'professional' ? 0.7 : 0.8
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate text');
      }

      const data = await response.json();
      setGeneratedText(data.content);

    } catch (err: any) {
      setError(err.message || 'Failed to generate text');
    } finally {
      setLoading(false);
    }
  };

  // Copy to clipboard
  const handleCopy = () => {
    navigator.clipboard.writeText(generatedText);
    alert('Copied to clipboard!');
  };

  // Download as file
  const handleDownload = () => {
    const blob = new Blob([generatedText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `generated-text-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Text Generation</h1>
          <p className="mt-2 text-gray-600">
            Generate high-quality text content using advanced AI models.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Settings */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Settings</h2>

              {/* Template Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Template
                </label>
                <select
                  value={template}
                  onChange={(e) => setTemplate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {TEMPLATES.map(t => (
                    <option key={t.id} value={t.id}>
                      {t.name} - {t.description}
                    </option>
                  ))}
                </select>
              </div>

              {/* Model Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  AI Model
                </label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {MODELS.map(m => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  {MODELS.find(m => m.id === model)?.description}
                </p>
              </div>

              {/* Word Count */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Words: {wordCount}
                </label>
                <input
                  type="range"
                  min="100"
                  max="2000"
                  step="100"
                  value={wordCount}
                  onChange={(e) => setWordCount(parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>100</span>
                  <span>2000</span>
                </div>
              </div>

              {/* Tone */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tone
                </label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="professional">Professional</option>
                  <option value="casual">Casual</option>
                  <option value="creative">Creative</option>
                  <option value="formal">Formal</option>
                  <option value="friendly">Friendly</option>
                </select>
              </div>
            </div>
          </div>

          {/* Right Column - Input & Output */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              {/* Prompt Input */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prompt
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe what you want to generate..."
                  className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={loading || !prompt.trim()}
                className="w-full mb-6 px-4 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
              >
                {loading ? 'Generating...' : 'Generate Text'}
              </button>

              {/* Error Message */}
              {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-red-600 text-sm">{error}</p>
                </div>
              )}

              {/* Generated Text Output */}
              {generatedText && (
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Generated Text
                    </label>
                    <div className="space-x-2">
                      <button
                        onClick={handleCopy}
                        className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                      >
                        Copy
                      </button>
                      <button
                        onClick={handleDownload}
                        className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                      >
                        Download
                      </button>
                    </div>
                  </div>
                  <div className="p-4 bg-gray-50 border border-gray-200 rounded-md max-h-96 overflow-y-auto">
                    <pre className="whitespace-pre-wrap font-sans text-gray-900">
                      {generatedText}
                    </pre>
                  </div>
                  <p className="mt-2 text-xs text-gray-500">
                    Word count: {generatedText.split(/\s+/).length}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

