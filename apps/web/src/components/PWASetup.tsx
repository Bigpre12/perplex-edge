"use client";
// components/PWASetup.tsx
// Add <PWASetup /> to your root layout.tsx
'use client';
import { useEffect } from 'react';

export default function PWASetup() {
  useEffect(() => {
    if ("serviceWorker" in navigator) {
      // In dev, always unregister to avoid stale SW issues
      if (process.env.NODE_ENV === "development") {
        navigator.serviceWorker.getRegistrations().then((regs) => {
          regs.forEach((reg) => reg.unregister());
        });
        return;
      }

      // Production only â€” register SW
      navigator.serviceWorker.register("/sw.js").catch(console.error);
    }
  }, []);
  return null;
}

// Add to your <head> in layout.tsx:
// <link rel='manifest' href='/manifest.json' />
// <meta name='theme-color' content='#3b82f6' />
// <meta name='mobile-web-app-capable' content='yes' />
// <meta name='apple-mobile-web-app-capable' content='yes' />
// <meta name='apple-mobile-web-app-status-bar-style' content='black-translucent' />
// <meta name='apple-mobile-web-app-title' content='LOLA' />
// <link rel='apple-touch-icon' href='/icons/icon-192.png' />
