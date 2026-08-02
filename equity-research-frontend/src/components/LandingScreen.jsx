import React from 'react';

export default function LandingScreen({ onStart }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center px-4">
      <div className="relative mb-6">
        {/* Ambient glow behind hero text */}
        <div className="absolute inset-0 bg-finance-gradient blur-[100px] rounded-full w-full h-full opacity-20 dark:opacity-30 -z-10" />
        <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-slate-900 dark:text-white pb-2">
          Multi-Agent <br className="md:hidden" />
          <span className="text-finance-gradient">Equity Research</span>
        </h1>
      </div>
      <p className="text-lg text-slate-600 dark:text-finance-muted mb-12 max-w-2xl leading-relaxed font-light">
        A LangGraph-orchestrated system coordinating seven specialized AI agents to produce a source-cited investment thesis, complete with forensic red-flag checks and DCF valuation.
      </p>
      <button 
        onClick={onStart}
        className="px-8 py-4 bg-finance-gradient hover:opacity-90 text-white font-medium rounded-full text-lg transition-all shadow-[0_4px_20px_rgba(20,184,166,0.3)] hover:shadow-[0_4px_25px_rgba(20,184,166,0.5)] transform hover:-translate-y-0.5 border-none"
      >
        Enter Workspace
      </button>
    </div>
  );
}
