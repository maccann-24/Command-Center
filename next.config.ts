import type { NextConfig } from "next";

// Ensure Turbopack/Next resolves the project root correctly in monorepo-like setups
// (especially when multiple lockfiles exist on the machine running the build).
const nextConfig: NextConfig = {
  turbopack: {
    root: process.cwd(),
  },
};

export default nextConfig;
