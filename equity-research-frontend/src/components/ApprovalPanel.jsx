import React, { useState } from 'react';
import { AlertTriangle, Check, Edit2 } from 'lucide-react';

export default function ApprovalPanel({ redFlags = [], onApprove }) {
  const [isEditing, setIsEditing] = useState(false);
  
  const handleApprove = () => {
    onApprove(isEditing ? redFlags.map(f => f.id) : [], redFlags.map(f => f.id));
  };

  const getSeverityColors = (severity) => {
    switch(severity) {
      case 'high': return 'bg-red-50 text-red-900 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-800/50';
      case 'medium': return 'bg-amber-50 text-amber-900 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200 dark:border-amber-800/50';
      case 'low': return 'bg-yellow-50 text-yellow-900 dark:bg-yellow-900/30 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800/50';
      default: return 'bg-slate-50 text-slate-800 dark:bg-slate-800 dark:text-slate-400 border-slate-200 dark:border-slate-700';
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white dark:bg-finance-card rounded-xl border border-amber-500/30 shadow-[0_0_20px_rgba(245,158,11,0.1)]">
      <div className="flex items-center gap-3 mb-6 border-b border-slate-200 dark:border-slate-700 pb-4">
        <div className="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
          <AlertTriangle className="w-6 h-6 text-amber-600 dark:text-amber-400" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-slate-900 dark:text-white">Analyst Review Required</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">Please review the forensic red flags identified by the system before synthesizing the final thesis.</p>
        </div>
      </div>
      
      <div className="space-y-4 mb-6">
        {redFlags.map(flag => (
          <div key={flag.id} className={`p-4 rounded-lg border flex flex-col sm:flex-row sm:items-start justify-between gap-4 transition-colors ${getSeverityColors(flag.severity)}`}>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-white/60 dark:bg-black/30">
                  {flag.severity} Severity
                </span>
                <span className="text-xs opacity-80">Source: {flag.source_ref}</span>
              </div>
              
              {isEditing ? (
                <textarea 
                  className="w-full mt-1 p-2 bg-white/50 dark:bg-black/20 border border-black/10 dark:border-white/10 rounded focus:outline-none focus:ring-1 focus:ring-amber-500/50 text-sm"
                  defaultValue={flag.description}
                  rows={2}
                />
              ) : (
                <p className="font-medium text-[15px]">{flag.description}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
        <button 
          onClick={() => setIsEditing(!isEditing)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
        >
          <Edit2 className="w-4 h-4" />
          {isEditing ? 'Cancel Editing' : 'Edit Findings'}
        </button>
        <button 
          onClick={handleApprove}
          className="flex items-center gap-2 px-6 py-2 rounded-lg font-medium bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)] transform hover:-translate-y-0.5"
        >
          <Check className="w-4 h-4" />
          {isEditing ? 'Save & Approve' : 'Approve & Continue'}
        </button>
      </div>
    </div>
  );
}
