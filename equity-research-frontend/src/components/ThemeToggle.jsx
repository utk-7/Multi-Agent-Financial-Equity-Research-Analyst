import React, { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';

export default function ThemeToggle() {
  const [theme, setTheme] = useState(() => {
    if (typeof localStorage !== 'undefined' && localStorage.getItem('theme')) {
      return localStorage.getItem('theme');
    }
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  });

  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  return (
    <button
      onClick={toggleTheme}
      className="p-2.5 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? <Sun className="w-5 h-5 text-slate-400" /> : <Moon className="w-5 h-5 text-slate-600" />}
    </button>
  );
}
