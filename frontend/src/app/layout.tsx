import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";
import AIHandler from "@/components/ai/AIHandler";
import Header from "@/components/layout/Header";
import AlertFeed from "@/components/AlertFeed";
import OracleChatbot from "@/components/OracleChatbot";
import CommandPalette from "@/components/CommandPalette";
import PWASetup from "@/components/PWASetup";

export const metadata: Metadata = {
  title: "Perplex Edge | Institutional Sports Betting Intelligence",
  description: "The world's fastest Real-Time Expected Value (+EV) Engine, Arbitrage Scanner, and Live Middle betting radar. Stop guessing. Start investing with an Edge.",
  keywords: ["Expected Value", "+EV", "Sports Betting", "Arbitrage", "Middling", "Player Props", "DFS", "PrizePicks"],
  authors: [{ name: "Perplex Engine" }],
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://perplexedge.com",
    title: "Perplex Edge | Intuitive Actionable Intelligence",
    description: "Access institutional-grade Real-Time EV streams, Arbitrage Scanners, and Live Middle betting radars.",
    siteName: "Perplex Edge",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Perplex Edge Dashboard",
      }
    ]
  },
  twitter: {
    card: "summary_large_image",
    title: "Perplex Edge",
    description: "The world's fastest Real-Time Expected Value (+EV) Engine.",
    images: ["/og-image.png"],
  },
  manifest: "/manifest.json",
  themeColor: "#3b82f6",
  viewport: "width=device-width, initial-scale=1, maximum-scale=1",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "Perplex Edge",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased">
        <PWASetup />
        <div className="flex h-screen w-full overflow-hidden bg-background-dark text-slate-100 font-display selection:bg-primary selection:text-background-dark relative">
          {/* Animated Background Elements */}
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/5 rounded-full blur-[120px] animate-pulse-slow"></div>
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-primary/5 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '1.5s' }}></div>

          <Sidebar />

          <main className="flex-1 flex flex-col h-full overflow-hidden bg-transparent z-10">
            <AlertFeed />
            <Header />
            <div className="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth custom-scrollbar">
              <main className="flex-1 overflow-y-auto px-6 py-8">
                <AIHandler />
                {children}
              </main>
            </div>

            {/* Global Modals & Listeners */}
            <CommandPalette />
            <OracleChatbot />
          </main>
        </div>
      </body>
    </html>
  );
}

