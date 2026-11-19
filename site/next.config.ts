import type { NextConfig } from "next";
// Static site for GitHub Pages: every page is plain HTML in out/, copied to ../docs.
const nextConfig: NextConfig = {
  output: "export",
  basePath: process.env.PAGES_BASE ?? "",
  trailingSlash: true,
  images: { unoptimized: true },
  typescript: { ignoreBuildErrors: true },
};
export default nextConfig;
