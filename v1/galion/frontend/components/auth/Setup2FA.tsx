"use client"

import { useState } from 'react'
import { authApi, handleApiError } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast'
import { Loader2, Copy, CheckCircle2 } from 'lucide-react'
import Image from 'next/image'

interface Setup2FAProps {
  onComplete?: () => void
}

export function Setup2FA({ onComplete }: Setup2FAProps) {
  const [step, setStep] = useState<'setup' | 'verify'>('setup')
  const [secret, setSecret] = useState('')
  const [qrCode, setQrCode] = useState('')
  const [code, setCode] = useState('')
  const [backupCodes, setBackupCodes] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [copiedSecret, setCopiedSecret] = useState(false)
  const [copiedBackup, setCopiedBackup] = useState(false)
  const { toast } = useToast()

  const handleSetup = async () => {
    setIsLoading(true)
    try {
      const response = await authApi.setup2FA()
      setSecret(response.secret)
      setQrCode(response.qr_code)
      setStep('verify')
    } catch (error) {
      toast({
        title: 'Setup failed',
        description: handleApiError(error),
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerify = async () => {
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
      const response = await authApi.enable2FA(code)
      setBackupCodes(response.backup_codes)
      toast({
        title: '2FA enabled',
        description: 'Two-factor authentication has been enabled successfully',
      })
      if (onComplete) onComplete()
    } catch (error) {
      toast({
        title: 'Verification failed',
        description: handleApiError(error),
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (text: string, type: 'secret' | 'backup') => {
    navigator.clipboard.writeText(text)
    if (type === 'secret') {
      setCopiedSecret(true)
      setTimeout(() => setCopiedSecret(false), 2000)
    } else {
      setCopiedBackup(true)
      setTimeout(() => setCopiedBackup(false), 2000)
    }
    toast({
      title: 'Copied!',
      description: 'Copied to clipboard',
    })
  }

  if (backupCodes.length > 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Backup Codes</CardTitle>
          <CardDescription>
            Save these backup codes in a safe place. You can use them to access your account if you lose your authenticator device.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-muted p-4 rounded-lg font-mono text-sm space-y-2">
            {backupCodes.map((code, index) => (
              <div key={index} className="flex justify-between items-center">
                <span>{code}</span>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => copyToClipboard(backupCodes.join('\n'), 'backup')}
            >
              {copiedBackup ? (
                <>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="mr-2 h-4 w-4" />
                  Copy All
                </>
              )}
            </Button>
            <Button onClick={onComplete} className="flex-1">
              Done
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (step === 'setup') {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Enable Two-Factor Authentication</CardTitle>
          <CardDescription>
            Add an extra layer of security to your account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Two-factor authentication adds an additional layer of security to your account by requiring more than just a password to sign in.
          </p>
          <Button onClick={handleSetup} className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Setting up...
              </>
            ) : (
              'Set up 2FA'
            )}
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Scan QR Code</CardTitle>
        <CardDescription>
          Scan this QR code with your authenticator app
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {qrCode && (
          <div className="flex justify-center">
            <div className="bg-white p-4 rounded-lg">
              <img src={qrCode} alt="QR Code" className="w-64 h-64" />
            </div>
          </div>
        )}
        {secret && (
          <div className="space-y-2">
            <Label>Or enter this code manually:</Label>
            <div className="flex gap-2">
              <Input value={secret} readOnly className="font-mono" />
              <Button
                variant="outline"
                size="icon"
                onClick={() => copyToClipboard(secret, 'secret')}
              >
                {copiedSecret ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        )}
        <div className="space-y-2">
          <Label htmlFor="code">Verification Code</Label>
          <Input
            id="code"
            type="text"
            placeholder="000000"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
            maxLength={6}
            className="text-center text-2xl tracking-widest"
          />
        </div>
        <Button onClick={handleVerify} className="w-full" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Verifying...
            </>
          ) : (
            'Verify and Enable'
          )}
        </Button>
      </CardContent>
    </Card>
  )
}

