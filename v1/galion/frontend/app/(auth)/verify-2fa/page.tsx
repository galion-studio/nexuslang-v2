"use client"

import { useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { authApi, handleApiError } from '@/lib/api'
import { useAuthStore } from '@/lib/stores/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'
import { Loader2 } from 'lucide-react'

function Verify2FAForm() {
  const [code, setCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { login } = useAuthStore()
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (code.length !== 6) {
      toast({
        title: 'Invalid code',
        description: 'Please enter a 6-digit code',
        variant: 'destructive',
      })
      return
    }

    setIsLoading(true)

    try {
      const response = await authApi.verify2FA(code)
      
      // Store auth data
      login(response.user, response.access_token)

      toast({
        title: '2FA verified',
        description: 'You have been successfully authenticated',
      })

      // Redirect to dashboard
      router.push('/dashboard')
    } catch (error) {
      toast({
        title: '2FA verification failed',
        description: handleApiError(error),
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 via-slate-900 to-purple-900 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex justify-center mb-4">
            <div className="text-4xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
              GALION.APP
            </div>
          </div>
          <CardTitle className="text-2xl text-center">Two-Factor Authentication</CardTitle>
          <CardDescription className="text-center">
            Enter the 6-digit code from your authenticator app
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="code">Verification Code</Label>
              <Input
                id="code"
                type="text"
                placeholder="000000"
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                required
                disabled={isLoading}
                className="text-center text-2xl tracking-widest"
                maxLength={6}
              />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Verifying...
                </>
              ) : (
                'Verify'
              )}
            </Button>
            <div className="text-sm text-center text-muted-foreground">
              <Link href="/login" className="text-primary hover:underline">
                Back to login
              </Link>
            </div>
          </CardContent>
        </form>
      </Card>
    </div>
  )
}

export default function Verify2FAPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Verify2FAForm />
    </Suspense>
  )
}

