import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Turbopack is the default in Next.js 16
  // diff-match-patch is loaded dynamically, so no special config needed
  // Add empty turbopack config to silence the warning
  turbopack: {},
};

export default nextConfig;
