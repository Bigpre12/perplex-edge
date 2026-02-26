import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
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
    },
  },
  plugins: [],
};
export default config;
