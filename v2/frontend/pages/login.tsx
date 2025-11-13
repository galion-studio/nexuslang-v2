// Login Page for developer.galion.app
import { useState } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import Link from 'next/link'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (response.ok) {
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        router.push('/dashboard')
      } else {
        setError(data.detail || 'Login failed')
      }
    } catch (err: any) {
      setError(err.message || 'Connection error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      padding: '20px'
    }}>
      <Head>
        <title>Login - NexusLang Developer Platform</title>
      </Head>

      <div style={{
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '20px',
        boxShadow: '0 25px 80px rgba(0,0,0,0.4)',
        maxWidth: '420px',
        width: '100%'
      }}>
        <div style={{textAlign: 'center', marginBottom: '30px'}}>
          <div style={{fontSize: '48px', marginBottom: '10px'}}>👨‍💻</div>
          <h1 style={{margin: '0 0 10px 0', color: '#333', fontSize: '28px'}}>Welcome Back</h1>
          <p style={{color: '#666', margin: 0}}>Login to your developer account</p>
        </div>

        <form onSubmit={handleLogin}>
          <div style={{marginBottom: '20px'}}>
            <label style={{display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px'}}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              style={{
                width: '100%',
                padding: '14px',
                fontSize: '16px',
                border: '2px solid #e0e0e0',
                borderRadius: '10px',
                outline: 'none',
                transition: 'border 0.3s',
                boxSizing: 'border-box'
              }}
              placeholder="you@example.com"
              onFocus={(e) => e.target.style.borderColor = '#6366f1'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
            />
          </div>

          <div style={{marginBottom: '25px'}}>
            <label style={{display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px'}}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              style={{
                width: '100%',
                padding: '14px',
                fontSize: '16px',
                border: '2px solid #e0e0e0',
                borderRadius: '10px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
              placeholder="••••••••"
              onFocus={(e) => e.target.style.borderColor = '#6366f1'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0e0'}
            />
          </div>

          {error && (
            <div style={{
              padding: '14px',
              backgroundColor: '#fee',
              color: '#c00',
              borderRadius: '10px',
              marginBottom: '20px',
              fontSize: '14px',
              border: '1px solid #fcc'
            }}>
              ❌ {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '16px',
              fontSize: '16px',
              fontWeight: '600',
              backgroundColor: loading ? '#ccc' : '#6366f1',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s',
              boxShadow: loading ? 'none' : '0 4px 14px rgba(99, 102, 241, 0.4)'
            }}
            onMouseEnter={(e) => {
              if (!loading) e.currentTarget.style.transform = 'translateY(-2px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
            }}
          >
            {loading ? '⏳ Logging in...' : '🔓 Login'}
          </button>
        </form>

        <div style={{marginTop: '25px', textAlign: 'center', fontSize: '14px'}}>
          <p style={{color: '#666', margin: '0 0 10px 0'}}>
            New to NexusLang?{' '}
            <Link href="/register" style={{color: '#6366f1', textDecoration: 'none', fontWeight: '600'}}>
              Create account
            </Link>
          </p>
          <p style={{margin: '10px 0'}}>
            <a href="/forgot-password" style={{color: '#999', textDecoration: 'none', fontSize: '13px'}}>
              Forgot password?
            </a>
          </p>
        </div>

        <div style={{
          marginTop: '30px',
          padding: '15px',
          backgroundColor: '#f8f9fa',
          borderRadius: '10px',
          fontSize: '13px',
          color: '#666',
          textAlign: 'center'
        }}>
          🎁 <strong>New users get 100 free credits!</strong>
        </div>
      </div>
    </div>
  )
}
