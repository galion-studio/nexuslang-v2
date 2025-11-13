/**
 * New Modern Landing Page for Galion Ecosystem
 * Beautiful, responsive, feature-rich UI
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

export default function HomePage() {
  const router = useRouter();
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Check backend status
  useEffect(() => {
    fetch('/api/v2/health')
      .then(res => res.json())
      .then(() => setBackendStatus('online'))
      .catch(() => setBackendStatus('offline'));
  }, []);

  return (
    <>
      <Head>
        <title>Galion - AI-Powered Development Platform</title>
        <meta name="description" content="Build, create, and deploy with AI" />
      </Head>

      <div style={{ 
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}>
        {/* Header */}
        <header style={{
          padding: '20px 50px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(255,255,255,0.1)',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
            <div style={{
              width: '40px',
              height: '40px',
              background: 'linear-gradient(45deg, #FFD700, #FFA500)',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px'
            }}>
              ⚡
            </div>
            <h1 style={{ color: 'white', fontSize: '24px', margin: 0 }}>
              Galion
            </h1>
          </div>
          <div style={{ display: 'flex', gap: '15px' }}>
            <button 
              onClick={() => router.push('/login')}
              style={{
                padding: '10px 25px',
                background: 'transparent',
                border: '2px solid white',
                color: 'white',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: '600',
                transition: 'all 0.3s'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = 'white';
                e.currentTarget.style.color = '#667eea';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.color = 'white';
              }}
            >
              Sign In
            </button>
            <button 
              onClick={() => router.push('/register')}
              style={{
                padding: '10px 25px',
                background: 'white',
                border: 'none',
                color: '#667eea',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: '600',
                boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
                transition: 'transform 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              Get Started →
            </button>
          </div>
        </header>

        {/* Hero Section */}
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '100px 50px',
          textAlign: 'center'
        }}>
          {/* Status Badge */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '10px',
            padding: '8px 20px',
            background: 'rgba(255,255,255,0.2)',
            borderRadius: '50px',
            marginBottom: '30px',
            backdropFilter: 'blur(10px)'
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: backendStatus === 'online' ? '#00ff88' : '#ff4444',
              animation: 'pulse 2s infinite'
            }} />
            <span style={{ color: 'white', fontSize: '14px' }}>
              {backendStatus === 'online' ? '✅ All Systems Operational' : 
               backendStatus === 'checking' ? '⏳ Checking...' : '⚠️ Backend Offline'}
            </span>
          </div>

          <h1 style={{
            fontSize: '72px',
            fontWeight: '800',
            color: 'white',
            marginBottom: '30px',
            lineHeight: '1.1'
          }}>
            Build with AI
            <br />
            <span style={{
              background: 'linear-gradient(45deg, #FFD700, #FFA500)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Ship Faster
            </span>
          </h1>

          <p style={{
            fontSize: '24px',
            color: 'rgba(255,255,255,0.9)',
            marginBottom: '50px',
            maxWidth: '700px',
            margin: '0 auto 50px'
          }}>
            The complete AI-powered platform for developers. Code, create, and deploy
            with 30+ AI models, instant execution, and powerful tools.
          </p>

          {/* CTA Buttons */}
          <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', marginBottom: '80px' }}>
            <button 
              onClick={() => router.push('/register')}
              style={{
                padding: '18px 40px',
                background: 'white',
                border: 'none',
                color: '#667eea',
                borderRadius: '12px',
                cursor: 'pointer',
                fontSize: '18px',
                fontWeight: '700',
                boxShadow: '0 8px 30px rgba(0,0,0,0.3)',
                transition: 'all 0.3s'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-3px)';
                e.currentTarget.style.boxShadow = '0 12px 40px rgba(0,0,0,0.4)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 8px 30px rgba(0,0,0,0.3)';
              }}
            >
              Start Building Free 🚀
            </button>
            <button 
              onClick={() => router.push('/docs')}
              style={{
                padding: '18px 40px',
                background: 'rgba(255,255,255,0.2)',
                border: '2px solid white',
                color: 'white',
                borderRadius: '12px',
                cursor: 'pointer',
                fontSize: '18px',
                fontWeight: '700',
                backdropFilter: 'blur(10px)',
                transition: 'all 0.3s'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.3)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
              }}
            >
              View Docs 📚
            </button>
          </div>

          {/* Feature Cards */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '30px',
            marginTop: '80px'
          }}>
            {[
              { icon: '🤖', title: 'AI Chat', desc: '30+ models including Claude, GPT-4, Llama', color: '#667eea' },
              { icon: '⚡', title: 'Instant Execution', desc: 'Run NexusLang, Python, JavaScript instantly', color: '#764ba2' },
              { icon: '🎨', title: 'Create Anything', desc: 'Images, videos, text, voice - all AI-powered', color: '#f093fb' },
              { icon: '💻', title: 'Web IDE', desc: 'Code editor with AI assistance built-in', color: '#4facfe' },
              { icon: '📊', title: 'Analytics', desc: 'Track usage, monitor performance, optimize', color: '#43e97b' },
              { icon: '👥', title: 'Team Collab', desc: 'Share projects, work together seamlessly', color: '#fa709a' }
            ].map((feature, i) => (
              <div key={i} style={{
                padding: '40px 30px',
                background: 'rgba(255,255,255,0.15)',
                backdropFilter: 'blur(10px)',
                borderRadius: '20px',
                border: '1px solid rgba(255,255,255,0.2)',
                transition: 'all 0.3s',
                cursor: 'pointer'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-10px)';
                e.currentTarget.style.background = 'rgba(255,255,255,0.25)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.background = 'rgba(255,255,255,0.15)';
              }}
              >
                <div style={{ fontSize: '48px', marginBottom: '20px' }}>{feature.icon}</div>
                <h3 style={{ color: 'white', fontSize: '24px', marginBottom: '15px' }}>{feature.title}</h3>
                <p style={{ color: 'rgba(255,255,255,0.8)', fontSize: '16px', lineHeight: '1.6' }}>
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>

          {/* Stats */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '30px',
            marginTop: '100px',
            padding: '60px',
            background: 'rgba(255,255,255,0.1)',
            borderRadius: '20px',
            backdropFilter: 'blur(10px)'
          }}>
            {[
              { num: '50+', label: 'API Endpoints' },
              { num: '30+', label: 'AI Models' },
              { num: '20+', label: 'Features' },
              { num: '99.9%', label: 'Uptime' }
            ].map((stat, i) => (
              <div key={i} style={{ textAlign: 'center' }}>
                <div style={{ 
                  fontSize: '48px', 
                  fontWeight: '800', 
                  color: 'white',
                  marginBottom: '10px'
                }}>
                  {stat.num}
                </div>
                <div style={{ 
                  fontSize: '16px', 
                  color: 'rgba(255,255,255,0.8)'
                }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <footer style={{
          padding: '40px 50px',
          textAlign: 'center',
          borderTop: '1px solid rgba(255,255,255,0.1)',
          color: 'rgba(255,255,255,0.7)'
        }}>
          <p style={{ margin: 0, fontSize: '14px' }}>
            © 2025 Galion. Built with ⚡ First Principles. Shipped with 🚀 Speed.
          </p>
        </footer>

        {/* Add pulse animation */}
        <style jsx global>{`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}</style>
      </div>
    </>
  );
}
