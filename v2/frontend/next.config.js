/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Environment variables exposed to the browser
  // For RunPod integration: Backend runs on port 8000 (standard)
  // For production: Uses environment variables from .env.local
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000',
  },
  
  // Performance: Image optimization with production domains
  images: {
    domains: ['localhost', 'developer.galion.app', 'api.developer.galion.app', 'cdn.galion.app'],
    formats: ['image/avif', 'image/webp'],  // Modern formats for faster loading
  },
  
  // Performance: Enable compression
  compress: true,
  
  // Performance: Optimize production bundle
  productionBrowserSourceMaps: false,  // Smaller bundles
  
  // Performance: Optimize fonts
  optimizeFonts: true,
  
  // Webpack configuration for Monaco Editor
  webpack: (config, { isServer, dev }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        module: false,
      };
    }
    
    // Monaco Editor support - optimized loading
    config.module.rules.push({
      test: /\.ttf$/,
      type: 'asset/resource'
    });
    
    // Performance: Minimize bundle size in production
    if (!dev) {
      config.optimization = {
        ...config.optimization,
        usedExports: true,  // Tree shaking
        sideEffects: false,
      };
    }
    
    return config;
  },
  
  // Experimental features
  experimental: {
    serverActions: true,
  },
  
  // Headers for security
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;

