import { Inter, JetBrains_Mono } from 'next/font/google';
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

export const metadata = {
  title: "LUCRIX",
  description: "Professional betting intelligence platform",
  icons: {
    icon: "/icon-192.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`} suppressHydrationWarning>
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#0f1117" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="Lucrix" />
        <link rel="apple-touch-icon" href="/icons/icon-192.png" />
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="antialiased bg-[#080810] text-[#f1f5f9] font-sans selection:bg-[#F5C518] selection:text-black relative" suppressHydrationWarning>
        <PWASetup />
        <OnboardingModal />
        <Providers>
          {children}
        </Providers>
        <footer style={{
          padding: '20px', textAlign: 'center', fontSize: '0.75rem',
          color: '#666', borderTop: '1px solid #1a1a2e', marginTop: 'auto'
        }}>
          For informational and entertainment purposes only. Not financial advice. Bet responsibly.
          If you have a gambling problem, call 1-800-GAMBLER. &copy; 2026 Lucrix Intelligence.
        </footer>
      </body>
    </html>
  );
}
