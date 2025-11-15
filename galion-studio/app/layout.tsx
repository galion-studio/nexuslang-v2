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
  metadataBase: new URL('https://studio.galion.app'),
  title: {
    default: 'Galion Studio - AI Content Creation Platform',
    template: '%s | Galion Studio'
  },
  description: 'Create stunning images, videos, and content with AI. Professional tools for creators powered by advanced AI technology.',
  keywords: [
    'AI content creation',
    'image generation',
    'video generation',
    'AI art',
    'creative tools',
    'Galion Studio',
    'AI design',
    'content creation'
  ],
  authors: [{ name: 'Galion Team' }],
  creator: 'Galion',
  publisher: 'Galion Studio',
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
    url: 'https://studio.galion.app',
    title: 'Galion Studio - AI Content Creation Platform',
    description: 'Create stunning images, videos, and content with AI. Professional tools for creators.',
    siteName: 'Galion Studio',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Galion Studio - AI Content Creation Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Galion Studio - AI Content Creation Platform',
    description: 'Create stunning images, videos, and content with AI. Professional tools for creators.',
    images: ['/og-image.jpg'],
    creator: '@galion_app',
  },
  verification: {
    google: 'your-google-site-verification-code',
    yandex: 'your-yandex-verification-code',
  },
  alternates: {
    canonical: 'https://studio.galion.app',
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
    "name": "Galion Studio",
    "description": "AI Content Creation Platform for generating images, videos, and creative content with advanced AI tools.",
    "url": "https://studio.galion.app",
    "applicationCategory": "CreativeApplication",
    "operatingSystem": "Web Browser",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    },
    "featureList": [
      "AI Image Generation",
      "Video Creation",
      "Content Design",
      "Creative Tools",
      "AI Art",
      "Professional Templates"
    ],
    "screenshot": "https://studio.galion.app/og-image.jpg",
    "author": {
      "@type": "Organization",
      "name": "Galion Team"
    },
    "publisher": {
      "@type": "Organization",
      "name": "Galion Studio"
    }
  }

  return (
    <html lang="en" className="dark">
      <head>
        {/* Browser Compatibility Meta Tags */}
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="msapplication-tap-highlight" content="no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="application-name" content="Galion Studio" />
        <meta name="apple-mobile-web-app-title" content="Galion Studio" />

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
        <Toaster position="bottom-right" />
      </body>
    </html>
  )
}

