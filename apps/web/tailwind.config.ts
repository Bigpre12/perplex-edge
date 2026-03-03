import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        lucrix: {
          gold: '#F5C518',
          dark: '#080810',
          surface: '#0F0F1A',
          card: '#141424',
          border: '#1E1E35',
          muted: '#2A2A45',
        },
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: "var(--primary)",
        "primary-dark": "var(--primary-dark)",
        secondary: "var(--secondary)",
        "background-dark": "var(--background-dark)",
        surface: "var(--surface)",
        "surface-highlight": "var(--surface-highlight)",
        "accent-green": "var(--accent-green)",
        "accent-red": "var(--accent-red)",
        "accent-orange": "var(--accent-orange)",
        "emerald-primary": "var(--emerald-primary)",
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          from: { boxShadow: '0 0 5px rgba(245, 197, 24, 0.2)' },
          to: { boxShadow: '0 0 20px rgba(245, 197, 24, 0.4)' },
        }
      }
    },
  },
  plugins: [],
};
export default config;
