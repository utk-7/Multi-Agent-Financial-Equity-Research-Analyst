import React, { useState } from 'react';
import LandingScreen from './components/LandingScreen';
import TickerInput from './components/TickerInput';
import ModeToggle from './components/ModeToggle';
import AgentProgress from './components/AgentProgress';
import ApprovalPanel from './components/ApprovalPanel';
import ReportView from './components/ReportView';
import ThemeToggle from './components/ThemeToggle';
import { useAgentStream } from './hooks/useAgentStream';

function App() {
  const [hasStarted, setHasStarted] = useState(false);
  const [ticker, setTicker] = useState('');
  const [mode, setMode] = useState('verified');
  const { events, latestEvent, isConnected, startStream, approve, editAndApprove } = useAgentStream(ticker, mode);

  const handleStartRun = () => {
    if (ticker.trim() && !isConnected) {
      startStream(ticker, mode);
    }
  };

  const isPaused = latestEvent?.type === 'interrupt_paused';
  const isComplete = latestEvent?.type === 'run_completed';

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-finance-dark transition-colors duration-300 font-sans flex flex-col">
      <div className="absolute top-4 right-6 z-50">
        <ThemeToggle />
      </div>

      {!hasStarted ? (
        <LandingScreen onStart={() => setHasStarted(true)} />
      ) : (
        <div className="w-full max-w-5xl mx-auto pt-16 pb-24 px-4 sm:px-6 flex-1 flex flex-col">
          <header className="mb-10 flex flex-col md:flex-row gap-6 justify-between items-center bg-white dark:bg-finance-card p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-finance-accent"></div>
            <div className="flex flex-col sm:flex-row gap-5 items-center w-full md:w-auto">
              <TickerInput 
                value={ticker} 
                onChange={setTicker}
                onSubmit={handleStartRun}
              />
              <ModeToggle mode={mode} setMode={setMode} />
            </div>
            
            <button 
              onClick={handleStartRun}
              disabled={isConnected || !ticker.trim()}
              className="w-full md:w-auto px-8 py-2.5 bg-gradient-to-r from-finance-accent to-sky-500 hover:from-sky-500 hover:to-sky-400 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_15px_rgba(14,165,233,0.3)] hover:shadow-[0_0_20px_rgba(14,165,233,0.5)] whitespace-nowrap"
            >
              {isConnected ? 'Run in Progress...' : 'Start Research'}
            </button>
          </header>

          <main className="space-y-10 flex-1">
            {(events.length > 0) && (
              <AgentProgress events={events} />
            )}

            {isPaused && (
              <ApprovalPanel 
                redFlags={latestEvent.payload.red_flags} 
                onApprove={approve}
              />
            )}
            
            {isComplete && (
              <ReportView report={latestEvent.payload.final_report} />
            )}
          </main>
        </div>
      )}
    </div>
  );
}

export default App;
