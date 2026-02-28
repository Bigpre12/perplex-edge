import { Inter, JetBrains_Mono } from 'next/font/google';
import "./globals.css";
import PWASetup from "@/components/PWASetup";

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

// ... meta tags ...
// (keeping the metadata object as is, just updating the export and body)

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="antialiased bg-[#080810] text-[#f1f5f9] font-sans selection:bg-[#F5C518] selection:text-black relative">
        <PWASetup />
        {children}
      </body>
    </html>
  );
}

