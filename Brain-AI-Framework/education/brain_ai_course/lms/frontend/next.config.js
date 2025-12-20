/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
    serverComponentsExternalPackages: ['prisma', '@prisma/client'],
  },
  images: {
    domains: [
      'images.unsplash.com',
      'avatars.githubusercontent.com',
      'lh3.googleusercontent.com',
      'res.cloudinary.com',
      'brainai.storage.googleapis.com',
    ],
    formats: ['image/avif', 'image/webp'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.API_BASE_URL || 'http://localhost:8000/api/v1/:path*',
      },
    ]
  },
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
    NEXT_PUBLIC_BRAIN_AI_API_URL: process.env.NEXT_PUBLIC_BRAIN_AI_API_URL || 'http://localhost:8000/api/v1',
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY,
  },
  // Performance optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  // Bundle analyzer (optional)
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
          },
        },
      }
    }
    return config
  },
}

module.exports = nextConfig