/** @type {import('next').NextConfig} */
const nextConfig = {
  // Docker standalone output
  output: 'standalone',

  // Performance optimizations
  swcMinify: true,
  compress: true,
  poweredByHeader: false,

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'production'
          ? 'http://backend:8000/api/:path*'
          : 'http://localhost:8080/api/:path*',
      },
    ]
  },

  // Enhanced Security Headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()'
          }
        ]
      },
      {
        source: '/_next/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable'
          }
        ]
      }
    ]
  },
}

module.exports = nextConfig
