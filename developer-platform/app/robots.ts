import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  const baseUrl = 'https://developer.galion.app'

  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: [
        '/auth/',
        '/api/',
        '/_next/',
        '/private/',
        '/dashboard/billing',
      ],
    },
    sitemap: `${baseUrl}/sitemap.xml`,
    host: baseUrl,
  }
}
