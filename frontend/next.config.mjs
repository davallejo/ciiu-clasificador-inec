/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // En Vercel, esto permite que el frontend llame al backend
  // (en local el backend corre en :8000 — ver variable NEXT_PUBLIC_API_URL)
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.BACKEND_URL || "http://localhost:8000"}/api/:path*`,
      },
    ];
  },
};
export default nextConfig;
