/** @type {import('next').NextConfig} */
const nextConfig = {
    eslint: {
        ignoreDuringBuilds: true,
    },
    typescript: {
        ignoreBuildErrors: true,
    },
    async rewrites() {
        let apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080";
        
        // Ensure https:// is present for production domains
        if (apiUrl && !apiUrl.startsWith("http")) {
            apiUrl = `https://${apiUrl}`;
        }

        return [
            {
                source: "/api/:path*",
                destination: `${apiUrl}/api/:path*`,
            },
        ];
    },
};

export default nextConfig;
