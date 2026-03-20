/** @type {import('next').NextConfig} */
const nextConfig = {
    eslint: {
        ignoreDuringBuilds: true,
    },
    typescript: {
        ignoreBuildErrors: true,
    },
    async rewrites() {
        const raw = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").trim();
        const apiUrl = raw.startsWith("http") ? raw : `https://${raw}`;
        return [
            {
                source: "/api/:path*",
                destination: `${apiUrl}/api/:path*`,
            },
        ];
    },
    async redirects() {
        return [
            {
                source: "/props",
                destination: "/player-props",
                permanent: true,
            },
        ];
    },
};

export default nextConfig;
