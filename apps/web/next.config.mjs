/** @type {import('next').NextConfig} */
const nextConfig = {
    eslint: {
        ignoreDuringBuilds: true,
    },
    typescript: {
        ignoreBuildErrors: true,
    },
    async rewrites() {
        // Trim whitespace/newlines from env var (Vercel dashboard can add trailing newlines)
        const raw = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").trim();
        // Ensure the URL starts with http:// or https://
        const apiUrl = raw.startsWith("http") ? raw : `https://${raw}`;
        return [
            {
                source: "/api/:path*",
                destination: `${apiUrl}/api/:path*`,
            },
        ];
    },
};

export default nextConfig;
