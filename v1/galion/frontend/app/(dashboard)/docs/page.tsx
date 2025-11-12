"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BookOpen, Code, Zap, Shield, Cloud } from 'lucide-react'

export default function DocsPage() {
  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Documentation</h1>
        <p className="text-muted-foreground">
          Complete guide to using GALION.APP
        </p>
      </div>

      {/* Getting Started */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-500" />
            <CardTitle>Quick Start</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">1. Authentication</h3>
            <p className="text-sm text-muted-foreground">
              Register an account or login to get started. Enable 2FA for enhanced security.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">2. Upload Documents</h3>
            <p className="text-sm text-muted-foreground">
              Navigate to the Documents page to upload and manage your files. Supported formats: PDF, PNG, JPG.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">3. Use Voice Commands</h3>
            <p className="text-sm text-muted-foreground">
              Click the microphone button to interact with the platform using voice. Try saying "Show my documents" or "Go to dashboard".
            </p>
          </div>
        </CardContent>
      </Card>

      {/* API Reference */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Code className="h-5 w-5 text-blue-500" />
            <CardTitle>API Reference</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">Base URL</h3>
            <code className="text-sm bg-muted px-2 py-1 rounded">
              http://localhost:8080/api/v1
            </code>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Authentication</h3>
            <p className="text-sm text-muted-foreground mb-2">
              All API requests require a JWT token in the Authorization header:
            </p>
            <code className="text-sm bg-muted px-2 py-1 rounded block">
              Authorization: Bearer {'<your-token>'}
            </code>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Key Endpoints</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <code className="bg-green-500/10 text-green-500 px-2 py-1 rounded">POST</code>
                <code>/auth/login</code>
              </div>
              <div className="flex items-center gap-2">
                <code className="bg-blue-500/10 text-blue-500 px-2 py-1 rounded">GET</code>
                <code>/users</code>
              </div>
              <div className="flex items-center gap-2">
                <code className="bg-green-500/10 text-green-500 px-2 py-1 rounded">POST</code>
                <code>/documents/upload</code>
              </div>
              <div className="flex items-center gap-2">
                <code className="bg-green-500/10 text-green-500 px-2 py-1 rounded">POST</code>
                <code>/voice/stt</code>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Architecture */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Cloud className="h-5 w-5 text-purple-500" />
            <CardTitle>Architecture</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            GALION.APP is built using a microservices architecture:
          </p>
          <div className="space-y-2 text-sm">
            <div>• <strong>API Gateway</strong> - Request routing and load balancing</div>
            <div>• <strong>Auth Service</strong> - User authentication and JWT management</div>
            <div>• <strong>User Service</strong> - User profile management</div>
            <div>• <strong>Document Service</strong> - File upload and verification</div>
            <div>• <strong>Voice Service</strong> - Speech-to-text and text-to-speech</div>
            <div>• <strong>Permissions Service</strong> - Role-based access control</div>
            <div>• <strong>Analytics Service</strong> - Metrics and monitoring</div>
          </div>
        </CardContent>
      </Card>

      {/* Security */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-red-500" />
            <CardTitle>Security</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">Encryption</h3>
            <p className="text-sm text-muted-foreground">
              All data is encrypted in transit using TLS 1.3 and at rest using AES-256.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Two-Factor Authentication</h3>
            <p className="text-sm text-muted-foreground">
              We support TOTP-based 2FA for enhanced account security.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Rate Limiting</h3>
            <p className="text-sm text-muted-foreground">
              API requests are rate-limited to prevent abuse: 60 requests per minute per user.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

