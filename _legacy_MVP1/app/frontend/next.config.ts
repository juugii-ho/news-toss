import type { NextConfig } from "next";

const supabaseHost = process.env.NEXT_PUBLIC_SUPABASE_URL
  ? new URL(process.env.NEXT_PUBLIC_SUPABASE_URL).host
  : undefined;

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  turbopack: {
    root: __dirname,
  },
    images: {
        remotePatterns: [
            {
                protocol: 'https',
                hostname: supabaseHost || '**', // Fallback to wildcard if env not set (for dev), but ideally should be set.
                pathname: '/storage/v1/object/public/**',
            },
        ],
    },
};

export default nextConfig;
