import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The live site sits behind the monorepo's middleware; standalone, the
  // profile page is simply /.
  reactStrictMode: true,
};

export default nextConfig;
