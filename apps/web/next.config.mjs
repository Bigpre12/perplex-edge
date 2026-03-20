/** @type {import('next').NextConfig} */
const nextConfig = {
    eslint: {
        ignoreDuringBuilds: true,
    },
    typescript: {
        ignoreBuildErrors: true,
    },
    async rewrites() {
<<<<<<< HEAD
        let apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080";
        
        // Ensure https:// is present for production domains
        if (apiUrl && !apiUrl.startsWith("http")) {
            apiUrl = `https://${apiUrl}`;
        }

=======
        // Trim whitespace/newlines from env var (Vercel dashboard can add trailing newlines)
        const raw = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").trim();
        // Ensure the URL starts with http:// or https://
        const apiUrl = raw.startsWith("http") ? raw : `https://${raw}`;
>>>>>>> f64e8d8167c22f2db5be4c20b757dac1a282d2cb
        return [
            {
                source: "/api/:path*",
                destination: `${apiUrl}/api/:path*`,
            },
        ];
    },
};

export default nextConfig;
