// galion.studio Dashboard
// Main dashboard showing recent generations and quick actions

import { useState, useEffect } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import apiClient from '../lib/api-client'

export default function Dashboard() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const profile = await apiClient.getProfile()
      setUser(profile)
    } catch (error) {
      console.error('Failed to load profile:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div style={{padding: '50px'}}>Loading...</div>
  }

  if (!user) {
    return (
      <div style={{padding: '50px'}}>
        <h1>Please login</h1>
        <Link href="/login">Go to Login</Link>
      </div>
    )
  }

  return (
    <div style={{padding: '50px', fontFamily: 'sans-serif'}}>
      <Head>
        <title>Dashboard - Galion Studio</title>
      </Head>

      <h1>Welcome back, {user.username}!</h1>
      
      <div style={{
        marginTop: '30px',
        padding: '20px',
        backgroundColor: '#f5f5f5',
        borderRadius: '12px'
      }}>
        <h3>Your Account</h3>
        <p>Credits: <strong>{user.credits.toFixed(2)}</strong></p>
        <p>Subscription: <strong>{user.subscription_tier}</strong></p>
        <p>Status: <strong>{user.subscription_status}</strong></p>
      </div>

      <div style={{marginTop: '40px'}}>
        <h2>Create Content</h2>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginTop: '20px'}}>
          <Link href="/generate/image">
            <div style={{
              padding: '30px',
              backgroundColor: '#6366f1',
              color: 'white',
              borderRadius: '12px',
              textAlign: 'center',
              cursor: 'pointer'
            }}>
              <div style={{fontSize: '48px'}}>🎨</div>
              <h3>Generate Image</h3>
              <p style={{fontSize: '14px'}}>1 credit</p>
            </div>
          </Link>

          <div style={{
            padding: '30px',
            backgroundColor: '#8b5cf6',
            color: 'white',
            borderRadius: '12px',
            textAlign: 'center',
            opacity: 0.6
          }}>
            <div style={{fontSize: '48px'}}>🎬</div>
            <h3>Generate Video</h3>
            <p style={{fontSize: '14px'}}>5 credits (Coming Soon)</p>
          </div>

          <div style={{
            padding: '30px',
            backgroundColor: '#ec4899',
            color: 'white',
            borderRadius: '12px',
            textAlign: 'center',
            opacity: 0.6
          }}>
            <div style={{fontSize: '48px'}}>✍️</div>
            <h3>Generate Text</h3>
            <p style={{fontSize: '14px'}}>~0.01 credits (Coming Soon)</p>
          </div>

          <div style={{
            padding: '30px',
            backgroundColor: '#f59e0b',
            color: 'white',
            borderRadius: '12px',
            textAlign: 'center',
            opacity: 0.6
          }}>
            <div style={{fontSize: '48px'}}>🎙️</div>
            <h3>Generate Voice</h3>
            <p style={{fontSize: '14px'}}>~0.01 credits (Coming Soon)</p>
          </div>
        </div>
      </div>

      <div style={{marginTop: '40px'}}>
        <h2>Recent Generations</h2>
        <p style={{color: '#666'}}>Your recent content will appear here</p>
      </div>
    </div>
  )
}

