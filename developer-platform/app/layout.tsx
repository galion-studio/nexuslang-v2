import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'
import Script from 'next/script'
import BrowserCompatibility from '@/components/browser/BrowserCompatibility'

const inter = Inter({ subsets: ['latin'] })

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  minimumScale: 1,
  userScalable: true,
  viewportFit: 'cover',
  themeColor: [
    { media: '(prefers-color-scheme: dark)', color: '#1e293b' },
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
  ],
}

export const metadata: Metadata = {
  metadataBase: new URL('https://developer.galion.app'),
  title: {
    default: 'developer.galion.app - AI-Native Development Platform',
    template: '%s | developer.galion.app'
  },
  description: 'Build the future with AI. Web IDE, NexusLang, AI chat, and developer tools powered by advanced AI.',
  keywords: [
    'AI development',
    'Web IDE',
    'NexusLang',
    'AI programming',
    'developer tools',
    'AI chat',
    'code generation',
    'AI assistant'
  ],
  authors: [{ name: 'Galion Team' }],
  creator: 'Galion',
  publisher: 'developer.galion.app',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://developer.galion.app',
    title: 'developer.galion.app - AI-Native Development Platform',
    description: 'Build the future with AI. Web IDE, NexusLang, AI chat, and developer tools powered by advanced AI.',
    siteName: 'developer.galion.app',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'developer.galion.app - AI-Native Development Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'developer.galion.app - AI-Native Development Platform',
    description: 'Build the future with AI. Web IDE, NexusLang, AI chat, and developer tools powered by advanced AI.',
    images: ['/og-image.jpg'],
    creator: '@galion_app',
  },
  verification: {
    google: 'your-google-site-verification-code',
    yandex: 'your-yandex-verification-code',
    bing: 'your-bing-verification-code',
  },
  alternates: {
    canonical: 'https://developer.galion.app',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "developer.galion.app",
    "description": "AI-Native Development Platform with Web IDE, NexusLang, AI chat, and developer tools.",
    "url": "https://developer.galion.app",
    "applicationCategory": "DeveloperApplication",
    "operatingSystem": "Web Browser",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    },
    "featureList": [
      "Web IDE",
      "AI Code Generation",
      "NexusLang Compiler",
      "AI Chat Assistant",
      "Developer Tools",
      "Real-time Collaboration"
    ],
    "screenshot": "https://developer.galion.app/og-image.jpg",
    "author": {
      "@type": "Organization",
      "name": "Galion Team"
    },
    "publisher": {
      "@type": "Organization",
      "name": "developer.galion.app"
    }
  }

  return (
    <html lang="en">
      <head>
        {/* Browser Compatibility Meta Tags */}
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="msapplication-tap-highlight" content="no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="application-name" content="developer.galion.app" />
        <meta name="apple-mobile-web-app-title" content="developer.galion.app" />

        {/* Browser Compatibility Scripts */}
        <Script
          src="https://polyfill.io/v3/polyfill.min.js?features=es6,es7,es8,es9,fetch,Promise,Symbol,Map,Set,WeakMap,WeakSet,Array.prototype.includes,Array.prototype.find,Array.prototype.findIndex,Object.entries,Object.values,URL,URLSearchParams,IntersectionObserver,ResizeObserver"
          strategy="beforeInteractive"
        />

        {/* Web Components Polyfill for older browsers */}
        <Script
          src="https://unpkg.com/@webcomponents/webcomponentsjs@2.6.0/webcomponents-bundle.js"
          strategy="beforeInteractive"
        />

        {/* Modern CSS Grid support for older browsers */}
        <Script
          dangerouslySetInnerHTML={{
            __html: `
              if (!CSS.supports('display', 'grid')) {
                document.documentElement.classList.add('no-css-grid');
              }
              if (!CSS.supports('display', 'flex')) {
                document.documentElement.classList.add('no-css-flex');
              }
              if (!('IntersectionObserver' in window)) {
                document.documentElement.classList.add('no-intersection-observer');
              }
            `,
          }}
          strategy="beforeInteractive"
        />

        <Script
          id="structured-data"
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify(structuredData),
          }}
        />
      </head>
      <body className={inter.className}>
        <BrowserCompatibility />
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  )
}
