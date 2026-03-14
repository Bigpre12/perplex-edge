/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./app/**/*.{js,jsx,ts,tsx}",
        "./components/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                lucrix: {
                    surface: '#0a0a0f',
                    card: '#16161f',
                    border: '#2a2a3a',
                    primary: '#7c3aed',
                    secondary: '#5a5a7a',
                    success: '#00ff88',
                    danger: '#ff4466',
                    info: '#06b6d4',
                    warning: '#ffcc00',
                }
            }
        },
    },
    plugins: [],
}
