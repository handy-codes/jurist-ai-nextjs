/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': __dirname,
    };
    return config;
  },
  // For FastAPI backend integration
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: '/backend/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;