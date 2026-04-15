"use client";
import { useEffect, useState } from 'react';

export default function ThemeToggle() {
  const [dark, setDark] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem('lola-theme');
    const isDark = saved ? saved === 'dark' : true;
    setDark(isDark);
    document.documentElement.classList.toggle('dark', isDark);
  }, []);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    localStorage.setItem('lola-theme', next ? 'dark' : 'light');
    document.documentElement.classList.toggle('dark', next);
  };

  return (
    <button onClick={toggle} title='Toggle theme'
      style={{ background: 'transparent', border: '1px solid #333', borderRadius: 8,
               padding: '6px 12px', cursor: 'pointer', fontSize: 18 }}>
      {dark ? '☀ï¸' : '🌙'}
    </button>
  );
}
// Add to tailwind.config.js: darkMode: 'class'
// Add ThemeToggle to your Navbar component
// Prefix dark-mode styles with dark: in Tailwind
