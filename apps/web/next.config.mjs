/** @type {import('next').NextConfig} */
const nextConfig = {
    eslint: {
        ignoreDuringBuilds: true,
    },
    typescript: {
        ignoreBuildErrors: true,
    },
    async rewrites() {
        const raw = process.env.NEXT_PUBLIC_API_URL || "https://perplex-edge-backend-production.up.railway.app";
        const apiUrl = (raw.startsWith("http") ? raw : `https://${raw}`).replace(/\/$/, "");
        return [
            {
                source: "/backend/:path*",
                destination: `${apiUrl}/:path*`, // Keeps /api from the frontend request
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
