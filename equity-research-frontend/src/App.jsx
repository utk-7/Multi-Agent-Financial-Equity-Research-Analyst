import React, { useState } from 'react';
import AgentProgress from './components/AgentProgress';
import { useAgentStream } from './hooks/useAgentStream';

function App() {
  const [ticker, setTicker] = useState('AAPL');
  const [mode, setMode] = useState('verified');
  const { events, latestEvent, isConnected, startStream, approve } = useAgentStream(ticker, mode);

  return (
    <div className="min-h-screen p-8 bg-finance-dark text-finance-text">
      <header className="mb-8 max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-4 text-finance-accent">Multi-Agent Equity Research (Phase 0 Demo)</h1>
        <div className="flex gap-4 items-center bg-finance-card p-4 rounded-lg border border-slate-700 shadow-lg">
          <input 
            type="text" 
            value={ticker} 
            onChange={(e) => setTicker(e.target.value)} 
            placeholder="Ticker (e.g. AAPL or ERR for error test)"
            className="bg-slate-800 border border-slate-600 px-4 py-2 rounded focus:outline-none focus:border-finance-accent text-white w-48"
          />
          <select 
            value={mode} 
            onChange={(e) => setMode(e.target.value)}
            className="bg-slate-800 border border-slate-600 px-4 py-2 rounded focus:outline-none focus:border-finance-accent text-white"
          >
            <option value="verified">Verified Mode (Requires Approval)</option>
            <option value="fast">Fast Mode (No Interrupt)</option>
          </select>
          <button 
            onClick={() => startStream(ticker, mode)}
            disabled={isConnected}
            className="bg-finance-accent hover:bg-sky-400 text-white px-6 py-2 rounded transition-colors disabled:opacity-50 ml-auto font-medium"
          >
            {isConnected ? 'Running...' : 'Start Run'}
          </button>
          
          {latestEvent?.type === 'interrupt_paused' && (
            <button 
              onClick={approve}
              className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded transition-colors shadow-[0_0_15px_rgba(16,185,129,0.3)] animate-pulse"
            >
              Simulate Approval
            </button>
          )}
        </div>
      </header>

      <main>
        <AgentProgress events={events} />
        
        {latestEvent?.type === 'run_completed' && (
          <div className="max-w-4xl mx-auto mt-8 p-6 bg-emerald-900/20 rounded-lg border border-emerald-500/30 text-emerald-400 font-medium flex items-center gap-3">
            <span className="text-xl">✅</span> Run Completed Successfully! Report would be generated here.
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
