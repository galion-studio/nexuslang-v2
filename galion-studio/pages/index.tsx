// galion.studio Homepage
// Content creation platform landing page

import Head from 'next/head'
import Link from 'link'

export default function Home() {
  return (
    <div style={{padding: '50px', fontFamily: 'sans-serif'}}>
      <Head>
        <title>Galion Studio - AI Content Creation</title>
      </Head>
      
      <h1>🎨 Galion Studio</h1>
      <p>AI-Powered Content Creation Platform</p>
      
      <div style={{marginTop: '30px'}}>
        <h2>Create Amazing Content with AI</h2>
        <ul>
          <li>Generate stunning images with DALL-E & Stable Diffusion</li>
          <li>Create videos with Runway & Pika</li>
          <li>Write content with Claude & GPT-4</li>
          <li>Synthesize voice with emotional TTS</li>
        </ul>
      </div>
      
      <div style={{marginTop: '30px'}}>
        <Link href="/dashboard">
          <button style={{
            padding: '12px 24px',
            backgroundColor: '#6366f1',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            cursor: 'pointer'
          }}>
            Get Started
          </button>
        </Link>
      </div>
      
      <div style={{marginTop: '50px'}}>
        <p>Backend API: <a href={`${process.env.NEXT_PUBLIC_API_URL}/health`}>Health Check</a></p>
        <p>Status: Running ✅</p>
      </div>
    </div>
  )
}

