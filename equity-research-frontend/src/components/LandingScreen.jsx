import React from 'react';

export default function LandingScreen({ onStart }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center px-4">
      <div className="relative mb-6">
        {/* Ambient glow behind hero text - using the gradient/glow rules */}
        <div className="absolute inset-0 bg-finance-accent/20 blur-[80px] rounded-full w-full h-full -z-10" />
        <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-slate-900 dark:text-white pb-2">
          Multi-Agent <br className="md:hidden" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-finance-accent to-sky-400">Equity Research</span>
        </h1>
      </div>
      <p className="text-lg text-slate-600 dark:text-slate-400 mb-12 max-w-2xl leading-relaxed">
        A LangGraph-orchestrated system coordinating seven specialized AI agents to produce a source-cited investment thesis, complete with forensic red-flag checks and DCF valuation.
      </p>
      <button 
        onClick={onStart}
        className="px-8 py-4 bg-gradient-to-r from-finance-accent to-sky-500 hover:from-sky-500 hover:to-sky-400 text-white font-medium rounded-lg text-lg transition-all shadow-[0_0_20px_rgba(14,165,233,0.3)] hover:shadow-[0_0_25px_rgba(14,165,233,0.5)] transform hover:-translate-y-0.5"
      >
        Enter Workspace
      </button>
    </div>
  );
}
