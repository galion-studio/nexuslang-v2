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
  metadataBase: new URL('https://galion.app'),
  title: {
    default: 'Galion.app - Voice AI Assistant | Talk Naturally with AI',
    template: '%s | Galion.app'
  },
  other: {
    'dns-prefetch': ['//fonts.googleapis.com', '//fonts.gstatic.com'],
    'preconnect': ['//fonts.googleapis.com', '//fonts.gstatic.com'],
  },
  description: 'Experience the future of AI interaction with voice-powered productivity tools. Natural conversations, instant research, and intelligent assistance through the power of your voice.',
  keywords: [
    'voice AI assistant',
    'voice commands',
    'AI productivity',
    'voice-powered research',
    'natural language AI',
    'speech recognition',
    'voice automation',
    'AI research assistant',
    'voice interface',
    'conversational AI'
  ],
  authors: [{ name: 'Galion Team' }],
  creator: 'Galion',
  publisher: 'Galion.app',
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
    url: 'https://galion.app',
    title: 'Galion.app - Voice AI Assistant | Talk Naturally with AI',
    description: 'Experience the future of AI interaction with voice-powered productivity tools. Natural conversations, instant research, and intelligent assistance.',
    siteName: 'Galion.app',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Galion.app - Voice AI Assistant',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Galion.app - Voice AI Assistant | Talk Naturally with AI',
    description: 'Experience the future of AI interaction with voice-powered productivity tools.',
    images: ['/og-image.jpg'],
    creator: '@galion_app',
  },
  verification: {
    google: 'your-google-site-verification-code',
    yandex: 'your-yandex-verification-code',
    bing: 'your-bing-verification-code',
  },
  alternates: {
    canonical: 'https://galion.app',
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
    "name": "Galion.app",
    "description": "Voice AI Assistant for natural conversations, instant research, and intelligent productivity tools.",
    "url": "https://galion.app",
    "applicationCategory": "BusinessApplication",
    "operatingSystem": "Web Browser",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    },
    "featureList": [
      "Voice Commands",
      "Natural Language Processing",
      "Instant Research",
      "AI Assistant",
      "Voice Automation",
      "Productivity Tools"
    ],
    "screenshot": "https://galion.app/og-image.jpg",
    "author": {
      "@type": "Organization",
      "name": "Galion Team"
    },
    "publisher": {
      "@type": "Organization",
      "name": "Galion.app"
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
        <meta name="application-name" content="Galion.app" />
        <meta name="apple-mobile-web-app-title" content="Galion.app" />

        {/* Performance Optimizations */}
        <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
        <link rel="dns-prefetch" href="//fonts.googleapis.com" />
        <link rel="preconnect" href="//fonts.gstatic.com" crossOrigin="" />

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

              // Performance optimizations
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js').then(function(registration) {
                    console.log('SW registered: ', registration);
                  }).catch(function(registrationError) {
                    console.log('SW registration failed: ', registrationError);
                  });
                });
              }

              // Preload critical resources
              if ('link' in document.createElement('link')) {
                const link = document.createElement('link');
                link.rel = 'prefetch';
                link.href = '/api/health';
                document.head.appendChild(link);
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
