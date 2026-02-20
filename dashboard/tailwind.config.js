/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#0a0a0c',
                card: 'rgba(255, 255, 255, 0.03)',
                'card-hover': 'rgba(255, 255, 255, 0.06)',
                primary: '#10b981', // Emerald 500
                secondary: '#6366f1', // Indigo 500
                accent: '#34d399', // Emerald 400
            },
            backdropBlur: {
                xs: '2px',
            }
        },
    },
    plugins: [],
}
