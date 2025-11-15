import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  const baseUrl = 'https://galion.app'

  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: [
        '/auth/',
        '/admin/',
        '/api/',
        '/_next/',
        '/private/',
        '/dashboard/billing',
        '/dashboard/profile',
      ],
    },
    sitemap: `${baseUrl}/sitemap.xml`,
    host: baseUrl,
  }
}
