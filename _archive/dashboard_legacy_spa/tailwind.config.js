/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                "primary": "#0dccf2",
                "primary-dark": "#0ab8da",
                "secondary": "#90c1cb",
                "background-dark": "#0f1719",
                "surface": "#16262a",
                "surface-highlight": "#1e3238",
                "accent-green": "#0bda54",
                "accent-red": "#ff4d4d",
                "accent-orange": "#ffa600",
                "emerald-primary": "#0df233", // From Arbitrage/Parlay mocks
            },
            fontFamily: {
                "display": ["Inter", "sans-serif"],
                "body": ["Inter", "sans-serif"],
                "mono": ["ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "Liberation Mono", "Courier New", "monospace"],
            },
            backdropBlur: {
                xs: '2px',
            },
            borderRadius: {
                "DEFAULT": "0.5rem",
                "lg": "0.75rem",
                "xl": "1rem",
                "2xl": "1.5rem",
                "full": "9999px"
            },
        },
    },
    plugins: [],
}
