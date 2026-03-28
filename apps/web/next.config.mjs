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
};

export default nextConfig;
