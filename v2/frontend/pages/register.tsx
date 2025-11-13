// Registration Page for developer.galion.app
// Beautiful, modern signup with validation

import { useState } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import Link from 'next/link'

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [passwordStrength, setPasswordStrength] = useState(0)

  const checkPasswordStrength = (pass: string) => {
    let strength = 0
    if (pass.length >= 12) strength++
    if (/[a-z]/.test(pass)) strength++
    if (/[A-Z]/.test(pass)) strength++
    if (/[0-9]/.test(pass)) strength++
    if (/[^a-zA-Z0-9]/.test(pass)) strength++
    setPasswordStrength(strength)
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (passwordStrength < 5) {
      setError('Password must be at least 12 characters with uppercase, lowercase, number, and special character')
      return
    }

    setLoading(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          username: formData.username,
          password: formData.password,
          full_name: formData.fullName
        })
      })

      const data = await response.json()

      if (response.ok) {
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        router.push('/dashboard')
      } else {
        setError(data.detail || 'Registration failed')
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
        <title>Sign Up - NexusLang Developer Platform</title>
      </Head>

      <div style={{
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '20px',
        boxShadow: '0 25px 80px rgba(0,0,0,0.4)',
        maxWidth: '480px',
        width: '100%'
      }}>
        <div style={{textAlign: 'center', marginBottom: '30px'}}>
          <div style={{fontSize: '48px', marginBottom: '10px'}}>🚀</div>
          <h1 style={{margin: '0 0 10px 0', color: '#333', fontSize: '28px'}}>Create Account</h1>
          <p style={{color: '#666', margin: 0}}>Join NexusLang Developer Platform</p>
        </div>

        <form onSubmit={handleRegister}>
          <div style={{marginBottom: '20px'}}>
            <label style={{display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px'}}>
              Full Name (Optional)
            </label>
            <input
              type="text"
              value={formData.fullName}
              onChange={(e) => setFormData({...formData, fullName: e.target.value})}
              style={{
                width: '100%',
                padding: '14px',
                fontSize: '16px',
                border: '2px solid #e0e0e0',
                borderRadius: '10px',
                outline: 'none',
                transition: 'all 0.3s',
                boxSizing: 'border-box'
              }}
              placeholder="John Doe"
            />
          </div>

          <div style={{marginBottom: '20px'}}>
            <label style={{display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px'}}>
              Email *
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
              style={{
                width: '100%',
                padding: '14px',
                fontSize: '16px',
                border: '2px solid #e0e0e0',
                borderRadius: '10px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
              placeholder="you@example.com"
            />
          </div>

          <div style={{marginBottom: '20px'}}>
            <label style={{display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px'}}>
              Username *
            </label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              required
              minLength={3}
              style={{
                width: '100%',
                padding: '14px',
                fontSize: '16px',
                border: '2px solid #e0e0e0',
                borderRadius: '10px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
              placeholder="johndoe"
            />
          </div>

          <div style={{marginBottom: '20px'}}>
            <label style={{display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px'}}>
              Password *
            </label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => {
                setFormData({...formData, password: e.target.value})
                checkPasswordStrength(e.target.value)
              }}
              required
              style={{
                width: '100%',
                padding: '14px',
                fontSize: '16px',
                border: '2px solid #e0e0e0',
                borderRadius: '10px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
              placeholder="Min 12 characters"
            />
            {/* Password strength indicator */}
            {formData.password && (
              <div style={{marginTop: '8px'}}>
                <div style={{
                  height: '4px',
                  backgroundColor: '#e0e0e0',
                  borderRadius: '2px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    height: '100%',
                    width: `${(passwordStrength / 5) * 100}%`,
                    backgroundColor: passwordStrength < 3 ? '#f00' : passwordStrength < 5 ? '#fa0' : '#0f0',
                    transition: 'all 0.3s'
                  }} />
                </div>
                <p style={{fontSize: '12px', color: '#666', marginTop: '4px'}}>
                  {passwordStrength < 3 && 'Weak'}
                  {passwordStrength === 3 && 'Fair'}
                  {passwordStrength === 4 && 'Good'}
                  {passwordStrength === 5 && 'Strong'}
                </p>
              </div>
            )}
          </div>

          <div style={{marginBottom: '25px'}}>
            <label style={{display: 'block', marginBottom: '8px', color: '#333', fontWeight: '500', fontSize: '14px'}}>
              Confirm Password *
            </label>
            <input
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
              required
              style={{
                width: '100%',
                padding: '14px',
                fontSize: '16px',
                border: '2px solid #e0e0e0',
                borderRadius: '10px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
              placeholder="Repeat password"
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
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div style={{marginTop: '25px', textAlign: 'center', fontSize: '14px'}}>
          <p style={{color: '#666', margin: '0 0 10px 0'}}>
            Already have an account?{' '}
            <Link href="/login" style={{color: '#6366f1', textDecoration: 'none', fontWeight: '600'}}>
              Login
            </Link>
          </p>
          <p style={{color: '#999', fontSize: '12px', marginTop: '15px'}}>
            By signing up, you get <strong>100 free credits</strong> to start!
          </p>
        </div>
      </div>
    </div>
  )
}

