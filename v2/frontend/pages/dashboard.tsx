// Developer Dashboard for developer.galion.app
import Head from 'next/head'
import Link from 'next/link'
import { useState, useEffect } from 'react'

export default function Dashboard() {
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v2/auth/me`, {
        headers: {'Authorization': `Bearer ${token}`}
      })
      const data = await response.json()
      setUser(data)
    } catch (error) {
      console.error('Failed to load profile')
    }
  }

  return (
    <div style={{padding: '50px'}}>
      <Head>
        <title>Dashboard - developer.galion.app</title>
      </Head>

      <h1>Developer Dashboard</h1>

      {user && (
        <div style={{marginTop: '30px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px'}}>
          <div style={{padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '12px'}}>
            <h3>Account</h3>
            <p>Email: {user.email}</p>
            <p>Credits: {user.credits.toFixed(2)}</p>
            <p>Tier: {user.subscription_tier}</p>
          </div>

          <div style={{padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '12px'}}>
            <h3>Quick Actions</h3>
            <Link href="/ide"><p>🚀 Open IDE</p></Link>
            <Link href="/chat"><p>💬 AI Chat</p></Link>
            <Link href="/pricing"><p>💰 Upgrade Plan</p></Link>
          </div>
        </div>
      )}
    </div>
  )
}

