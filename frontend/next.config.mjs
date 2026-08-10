/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true,
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
      {
        protocol: "http",
        hostname: "**",
      },
    ],
  },
  // Better caching for static assets
  generateBuildId: undefined,
  compress: true,
  poweredByHeader: false,
  trailingSlash: true,
};

export default nextConfig;