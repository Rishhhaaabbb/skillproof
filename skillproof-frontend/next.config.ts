import type { NextConfig } from "next";
// eslint-disable-next-line @typescript-eslint/no-require-imports
const withPWAInit = require("next-pwa");

const withPWA = withPWAInit({
  dest: "public",
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === "development",
  // Cache strategies for offline support
  runtimeCaching: [
    {
      // API calls — network first, fall back to cache
      urlPattern: /^https:\/\/.*\/api\/.*/i,
      handler: "NetworkFirst",
      options: {
        cacheName: "api-cache",
        expiration: {
          maxEntries: 64,
          maxAgeSeconds: 60 * 60 * 24, // 24 hours
        },
      },
    },
    {
      // Static assets — cache first
      urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp|ico|woff2?)$/i,
      handler: "CacheFirst",
      options: {
        cacheName: "static-assets",
        expiration: {
          maxEntries: 64,
          maxAgeSeconds: 60 * 60 * 24 * 30, // 30 days
        },
      },
    },
    {
      // Next.js page navigations — network first
      urlPattern: /^https:\/\/.+\/_next\/data\/.+\.json/i,
      handler: "NetworkFirst",
      options: {
        cacheName: "next-data",
        expiration: {
          maxEntries: 32,
          maxAgeSeconds: 60 * 60 * 24, // 24 hours
        },
      },
    },
  ],
});

const nextConfig: NextConfig = {
  // Silence the next-pwa webpack warnings in newer Next.js versions
  webpack: (config) => {
    return config;
  },
};

export default withPWA(nextConfig);
