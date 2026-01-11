/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configuration for Next.js 14
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'pixabay.com',
        pathname: '/get/**',
      },
      {
        protocol: 'https',
        hostname: 'cdn.pixabay.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'placehold.co',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '5000',
        pathname: '/**',
      },
    ],
  },
};

module.exports = nextConfig;

