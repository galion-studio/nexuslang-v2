import { Metadata } from 'next'

interface HeadProps {
  title?: string
  description?: string
  keywords?: string[]
  image?: string
  url?: string
  type?: 'website' | 'article'
  publishedTime?: string
  modifiedTime?: string
  author?: string
  section?: string
  tags?: string[]
}

export function generateSEOMetadata({
  title,
  description,
  keywords = [],
  image = '/og-image.jpg',
  url,
  type = 'website',
  publishedTime,
  modifiedTime,
  author,
  section,
  tags = []
}: HeadProps): Metadata {
  const baseUrl = 'https://galion.app'
  const fullUrl = url ? `${baseUrl}${url}` : baseUrl
  const fullImage = image.startsWith('http') ? image : `${baseUrl}${image}`

  const metadata: Metadata = {
    title: title ? `${title} | Galion.app` : 'Galion.app - Voice AI Assistant | Talk Naturally with AI',
    description: description || 'Experience the future of AI interaction with voice-powered productivity tools. Natural conversations, instant research, and intelligent assistance.',
    keywords: [
      'voice AI assistant',
      'voice commands',
      'AI productivity',
      'voice-powered research',
      'natural language AI',
      ...keywords
    ],
    authors: author ? [{ name: author }] : [{ name: 'Galion Team' }],
    openGraph: {
      type,
      url: fullUrl,
      title: title ? `${title} | Galion.app` : 'Galion.app - Voice AI Assistant | Talk Naturally with AI',
      description: description || 'Experience the future of AI interaction with voice-powered productivity tools. Natural conversations, instant research, and intelligent assistance.',
      siteName: 'Galion.app',
      images: [
        {
          url: fullImage,
          width: 1200,
          height: 630,
          alt: title || 'Galion.app - Voice AI Assistant',
        },
      ],
      ...(publishedTime && { publishedTime }),
      ...(modifiedTime && { modifiedTime }),
      ...(author && { authors: [author] }),
      ...(section && { section }),
      ...(tags.length > 0 && { tags }),
    },
    twitter: {
      card: 'summary_large_image',
      title: title ? `${title} | Galion.app` : 'Galion.app - Voice AI Assistant | Talk Naturally with AI',
      description: description || 'Experience the future of AI interaction with voice-powered productivity tools.',
      images: [fullImage],
      creator: '@galion_app',
    },
    alternates: {
      canonical: fullUrl,
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
  }

  return metadata
}

export default function Head({ ...props }: HeadProps) {
  // This component is mainly for generating metadata
  // The actual metadata is handled by Next.js metadata API
  return null
}
