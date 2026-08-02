import React from 'react';

export default function ModeToggle({ mode, setMode }) {
  return (
    <div className="flex bg-slate-200 dark:bg-slate-900 p-1 rounded-lg border border-slate-300 dark:border-slate-700 shrink-0">
      <button
        onClick={() => setMode('verified')}
        className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
          mode === 'verified' 
            ? 'bg-white dark:bg-slate-800 text-finance-accent shadow-sm' 
            : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
        }`}
      >
        Verified Mode
      </button>
      <button
        onClick={() => setMode('fast')}
        className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
          mode === 'fast' 
            ? 'bg-white dark:bg-slate-800 text-finance-accent shadow-sm' 
            : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
        }`}
      >
        Fast Mode
      </button>
    </div>
  );
}
