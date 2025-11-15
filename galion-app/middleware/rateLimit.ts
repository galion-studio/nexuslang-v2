import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Simple in-memory rate limiting (in production, use Redis)
const rateLimitMap = new Map()

export function middleware(request: NextRequest) {
  const ip = request.ip || 'anonymous'
  const key = `${ip}:${request.nextUrl.pathname}`
  const now = Date.now()
  const windowMs = 60 * 1000 // 1 minute
  const maxRequests = 100 // 100 requests per minute

  const userRequests = rateLimitMap.get(key) || []
  const validRequests = userRequests.filter((timestamp: number) => now - timestamp < windowMs)

  if (validRequests.length >= maxRequests) {
    return new NextResponse(
      JSON.stringify({
        error: 'Too many requests',
        message: 'Rate limit exceeded. Please try again later.'
      }),
      {
        status: 429,
        headers: {
          'Content-Type': 'application/json',
          'Retry-After': '60'
        }
      }
    )
  }

  validRequests.push(now)
  rateLimitMap.set(key, validRequests)

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/api/:path*',
    '/voice/:path*',
    '/analytics/:path*'
  ]
}
