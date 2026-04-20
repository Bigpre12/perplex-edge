/** @type {import('next').NextConfig} */
const nextConfig = {
    eslint: {
        ignoreDuringBuilds: false,
    },
    typescript: {
        ignoreBuildErrors: false,
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
    async rewrites() {
        const isProd = process.env.NODE_ENV === "production";
        let backendUrl = process.env.NEXT_PUBLIC_API_URL || "https://perplex-edge-backend-copy-production.up.railway.app";
        
        // Prevent accidental localhost copy-paste to Vercel
        if (isProd && backendUrl.includes("localhost")) {
            backendUrl = "https://perplex-edge-backend-copy-production.up.railway.app";
        }

        return [
            {
                source: "/backend/:path*",
                destination: `${backendUrl}/:path*`,
            },
        ];
    },
};

export default nextConfig;
