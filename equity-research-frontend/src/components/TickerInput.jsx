import React, { useState } from 'react';

export default function TickerInput({ value, onChange, onSubmit }) {
  const [error, setError] = useState('');

  const handleBlur = () => {
    if (!value.trim()) {
      setError('Ticker cannot be empty');
    } else if (!/^[A-Za-z]+$/.test(value)) {
      setError('Invalid format (e.g. AAPL)');
    } else {
      setError('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !error && value.trim()) {
      onSubmit();
    }
  };

  return (
    <div className="flex flex-col relative w-48 shrink-0">
      <input
        type="text"
        value={value}
        onChange={(e) => {
          onChange(e.target.value.toUpperCase());
          setError('');
        }}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        placeholder="Ticker (e.g. AAPL)"
        className={`w-full px-4 py-2.5 rounded-md border bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-finance-accent/50 uppercase font-medium transition-colors ${
          error ? 'border-red-500' : 'border-slate-300 dark:border-slate-600 focus:border-finance-accent'
        }`}
      />
      {error && <span className="absolute -bottom-5 left-1 text-[11px] text-red-500 font-medium whitespace-nowrap">{error}</span>}
    </div>
  );
}
