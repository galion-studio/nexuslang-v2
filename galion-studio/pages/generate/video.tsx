/**
 * Video Generation Page
 * 
 * Generate videos from text prompts or animate images.
 * Powered by Stability AI and RunwayML.
 */

import { useState } from 'react';
import Head from 'next/head';

export default function VideoGenerationPage() {
  const [mode, setMode] = useState<'text' | 'image'>('text');
  const [prompt, setPrompt] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Settings
  const [duration, setDuration] = useState(4);
  const [fps, setFps] = useState(24);
  const [model, setModel] = useState('stable-video');

  // Generate video from text
  const handleGenerateFromText = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setLoading(true);
    setError('');
    setVideoUrl('');

    try {
      const response = await fetch('/api/v2/video/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          prompt,
          duration,
          fps,
          model
        })
      });

      if (!response.ok) {
        throw new Error('Video generation failed');
      }

      const data = await response.json();
      setVideoUrl(data.video_url);

    } catch (err: any) {
      setError(err.message || 'Failed to generate video');
    } finally {
      setLoading(false);
    }
  };

  // Animate image
  const handleAnimateImage = async () => {
    if (!imageFile) {
      setError('Please select an image');
      return;
    }

    setLoading(true);
    setError('');
    setVideoUrl('');

    try {
      const formData = new FormData();
      formData.append('image', imageFile);
      formData.append('prompt', prompt);
      formData.append('duration', duration.toString());

      const response = await fetch('/api/v2/video/animate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Image animation failed');
      }

      const data = await response.json();
      setVideoUrl(data.video_url);

    } catch (err: any) {
      setError(err.message || 'Failed to animate image');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Video Generation - Galion Studio</title>
      </Head>

      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-5xl mx-auto px-4">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Video Generation</h1>
          <p className="text-gray-600 mb-8">
            Create stunning videos from text or animate your images with AI.
          </p>

          {/* Mode Selector */}
          <div className="bg-white rounded-lg shadow mb-6 p-4">
            <div className="flex space-x-4">
              <button
                onClick={() => setMode('text')}
                className={`px-6 py-2 rounded-md font-medium transition ${
                  mode === 'text'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Text to Video
              </button>
              <button
                onClick={() => setMode('image')}
                className={`px-6 py-2 rounded-md font-medium transition ${
                  mode === 'image'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Image to Video
              </button>
            </div>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Settings */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">Settings</h2>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Model
                    </label>
                    <select
                      value={model}
                      onChange={(e) => setModel(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    >
                      <option value="stable-video">Stable Video Diffusion</option>
                      <option value="runway-gen2">RunwayML Gen-2</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Duration: {duration}s
                    </label>
                    <input
                      type="range"
                      min="2"
                      max="10"
                      step="1"
                      value={duration}
                      onChange={(e) => setDuration(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      FPS
                    </label>
                    <select
                      value={fps}
                      onChange={(e) => setFps(parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    >
                      <option value="16">16 FPS</option>
                      <option value="24">24 FPS (Cinematic)</option>
                      <option value="30">30 FPS (Smooth)</option>
                    </select>
                  </div>

                  <div className="pt-4 border-t">
                    <p className="text-sm text-gray-600">
                      <strong>Cost:</strong> 5 credits per video
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Generation Area */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow p-6">
                {mode === 'text' ? (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Describe your video
                    </label>
                    <textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="A serene sunset over mountains with birds flying..."
                      className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={handleGenerateFromText}
                      disabled={loading || !prompt.trim()}
                      className="mt-4 w-full px-4 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:bg-gray-300 transition"
                    >
                      {loading ? 'Generating Video...' : 'Generate Video'}
                    </button>
                  </div>
                ) : (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Upload Image
                    </label>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => setImageFile(e.target.files?.[0] || null)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    />
                    <label className="block text-sm font-medium text-gray-700 mb-2 mt-4">
                      Motion Description (optional)
                    </label>
                    <textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="Gentle zoom in with parallax effect..."
                      className="w-full h-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={handleAnimateImage}
                      disabled={loading || !imageFile}
                      className="mt-4 w-full px-4 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:bg-gray-300 transition"
                    >
                      {loading ? 'Animating Image...' : 'Animate Image'}
                    </button>
                  </div>
                )}

                {error && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-red-600 text-sm">{error}</p>
                  </div>
                )}

                {videoUrl && (
                  <div className="mt-6">
                    <h3 className="text-lg font-semibold mb-2">Generated Video</h3>
                    <video
                      src={videoUrl}
                      controls
                      className="w-full rounded-lg"
                    />
                    <a
                      href={videoUrl}
                      download
                      className="mt-2 inline-block px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                    >
                      Download Video
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

