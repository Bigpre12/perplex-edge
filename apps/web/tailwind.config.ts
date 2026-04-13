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
        sans: ['var(--font-inter)', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
        display: ['var(--font-space)', 'sans-serif'],
      },
      colors: {
        lucrix: {
          dark: '#0A0A0F',
          surface: '#111118',
          elevated: '#1A1A24',
          border: '#2A2A3A',
          borderBright: '#3A3A5A',
        },
        brand: {
          purple: '#6C63FF',
          cyan: '#00D4FF',
          success: '#00FF88',
          warning: '#FFB800',
          danger: '#FF4466',
        },
        primary: '#6C63FF', // Alias for brand.purple
        'brand-primary': '#6C63FF', // Alias for brand.purple
        background: "var(--background)",
        foreground: "var(--foreground)",
        textPrimary: '#FFFFFF',
        textSecondary: '#8888AA',
        textMuted: '#44445A',
      },
      borderRadius: {
        card: '12px',
        badge: '6px',
        btn: '8px',
      },
      boxShadow: {
        card: '0 0 0 1px #2A2A3A, 0 4px 24px rgba(0,0,0,0.4)',
        glow: '0 0 20px rgba(108,99,255,0.15)',
        live: '0 0 12px rgba(0,212,255,0.2)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          from: { boxShadow: '0 0 5px rgba(108, 99, 255, 0.2)' },
          to: { boxShadow: '0 0 20px rgba(108, 99, 255, 0.4)' },
        }
      }
    },
  },
  plugins: [],
};
export default config;
