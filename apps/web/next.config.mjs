/** @type {import('next').NextConfig} */
const nextConfig = {
    eslint: {
        ignoreDuringBuilds: true,
    },
    typescript: {
        ignoreBuildErrors: true,
    },
    async rewrites() {
        const raw = process.env.NEXT_PUBLIC_API_URL?.trim();
        const apiUrl = (raw && raw !== "" ? raw : "https://perplex-edge-backend-production.up.railway.app")
            .replace(/\/$/, "");
        return [
            {
                source: "/backend/api/:path*",
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
