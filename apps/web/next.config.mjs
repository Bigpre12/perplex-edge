/** @type {import('next').NextConfig} */
const nextConfig = {
    eslint: {
        ignoreDuringBuilds: true,
    },
    typescript: {
        ignoreBuildErrors: true,
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
        return [
            {
                source: "/backend/:path*",
                destination: "http://localhost:8000/:path*",
            },
        ];
    },
};

export default nextConfig;
