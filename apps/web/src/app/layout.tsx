import type { Metadata, Viewport } from 'next';
import { Inter, JetBrains_Mono, Space_Grotesk } from 'next/font/google';
import "./globals.css";
import PWASetup from "@/components/PWASetup";
import { OnboardingModal } from "@/components/OnboardingModal";
import { Providers } from "@/components/Providers";

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const mono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

const space = Space_Grotesk({
  subsets: ['latin'],
  weight: ['400', '700'],
  variable: '--font-space',
  display: 'swap',
});

export const metadata: Metadata = {
  title: "LUCRIX | Quantum Analytics. Institutional Edge.",
  description: "Professional betting intelligence platform",
  icons: {
    icon: [
      { url: "/icon-192.png", sizes: "192x192", type: "image/png" },
      { url: "/favicon.ico", sizes: "any" }
    ],
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" }
    ],
  },
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#0A0A0F",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable} ${space.variable}`} suppressHydrationWarning>
      <head />
      <body className="antialiased bg-lucrix-dark text-textPrimary font-sans selection:bg-brand-purple selection:text-white relative" suppressHydrationWarning>
        <PWASetup />
        <Providers>
          <OnboardingModal />
          {children}
        </Providers>
        <footer className="lucrix-footer">
          For informational and entertainment purposes only. Not financial advice. Bet responsibly.
          If you have a gambling problem, call 1-800-GAMBLER. &copy; 2026 Lucrix Intelligence.
        </footer>
      </body>
    </html>
  );
}

