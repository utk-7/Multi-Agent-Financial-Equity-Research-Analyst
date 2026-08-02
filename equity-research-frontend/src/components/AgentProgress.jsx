import React from 'react';
import { CheckCircle2, Circle, Loader2, XCircle } from 'lucide-react';

const NodeItem = ({ id, label, status, summary, error }) => {
  let icon = <Circle className="w-5 h-5 text-finance-muted" />;
  let borderClass = 'bg-slate-800/20'; // Soft background, no hard borders
  
  if (status === 'running') {
    icon = <Loader2 className="w-5 h-5 text-finance-grad-start animate-spin" />;
    borderClass = 'bg-finance-card relative overflow-hidden shadow-lg shadow-black/10';
  } else if (status === 'completed') {
    icon = <div className="bg-finance-gradient rounded-full p-0.5"><CheckCircle2 className="w-4 h-4 text-white" /></div>;
    borderClass = 'bg-finance-card shadow-sm shadow-black/10';
  } else if (status === 'error') {
    icon = <XCircle className="w-5 h-5 text-red-400" />;
    borderClass = 'bg-red-900/10';
  }

  return (
    <div className={`p-4 rounded-[16px] transition-all duration-300 flex flex-col gap-2 ${borderClass}`}>
      {status === 'running' && (
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-finance-gradient" />
      )}
      <div className="flex items-center gap-3">
        {icon}
        <span className="font-medium text-slate-200">{label}</span>
      </div>
      {summary && <div className="text-sm text-finance-muted ml-8">{summary}</div>}
      {error && <div className="text-sm text-red-400 ml-8">{error}</div>}
    </div>
  );
};

export default function AgentProgress({ events }) {
  const nodeStates = {
    ingestion: { status: 'pending' },
    ratio: { status: 'pending' },
    sentiment: { status: 'pending' },
    valuation: { status: 'pending' },
    red_flag: { status: 'pending' },
    synthesis: { status: 'pending' }
  };

  events.forEach(event => {
    if (event.type === 'node_started' && nodeStates[event.payload.node]) {
      nodeStates[event.payload.node] = { status: 'running' };
    } else if (event.type === 'node_completed' && nodeStates[event.payload.node]) {
      nodeStates[event.payload.node] = { status: 'completed', summary: event.payload.output_summary };
    } else if (event.type === 'node_error' && nodeStates[event.payload.node]) {
      nodeStates[event.payload.node] = { status: 'error', error: event.payload.message };
    }
  });

  return (
    <div className="w-full max-w-4xl mx-auto p-6 flex flex-col gap-6">
      <h2 className="text-xl font-semibold text-slate-100 mb-2">Pipeline Progress</h2>
      
      {/* 1. Ingestion */}
      <NodeItem id="ingestion" label="Ingestion & Data" {...nodeStates.ingestion} />
      
      {/* 2. Parallel fan-out */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pl-8 border-l-2 border-slate-700 ml-4 relative">
        {/* Subtle connecting line for the fan-out structure */}
        <div className="absolute -left-[2px] top-4 bottom-4 w-0.5 bg-slate-700"></div>
        <NodeItem id="ratio" label="Ratio / Quant" {...nodeStates.ratio} />
        <NodeItem id="sentiment" label="Sentiment" {...nodeStates.sentiment} />
        <NodeItem id="valuation" label="DCF Valuation" {...nodeStates.valuation} />
      </div>

      {/* 3. Red Flag */}
      <NodeItem id="red_flag" label="Red-Flag Checks" {...nodeStates.red_flag} />

      {/* 4. Synthesis */}
      <NodeItem id="synthesis" label="Report Synthesis" {...nodeStates.synthesis} />
    </div>
  );
}
