import React from 'react';
import { AlertTriangle, TrendingUp, TrendingDown, BookOpen, BarChart3, Scale } from 'lucide-react';
import SensitivityGrid from './SensitivityGrid';
import RatioTrendChart from './RatioTrendChart';

export default function ReportView({ payload }) {
  if (!payload) return null;

  const report = payload.final_report || {};
  const metrics = payload.eval_metrics || {};
  const citations = payload.citations || [];
  const ratios = payload.ratio_table || {};
  const redFlags = payload.red_flags || [];
  const valuation = payload.valuation_range || {};

  return (
    <div className="w-full max-w-4xl mx-auto p-8 bg-white dark:bg-finance-card rounded-xl border border-slate-200 dark:border-slate-700 shadow-xl overflow-hidden mt-6">
      
      <div className="border-b border-slate-200 dark:border-slate-700 pb-6 mb-8 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-3">Final Investment Thesis</h2>
          <div className="flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-6 mt-4 md:mt-0 bg-slate-50 dark:bg-slate-800/50 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700/50">
            <span className="flex items-center gap-2 text-sm">
              <BookOpen className="w-4 h-4 text-finance-accent" />
              <span className="font-semibold text-slate-900 dark:text-white">Coverage:</span> 
              <span className={metrics.citation_coverage_percent === 100 ? "text-emerald-600 dark:text-emerald-400 font-bold" : ""}>
                {metrics.citation_coverage_percent}%
              </span>
            </span>
            <div className="w-px h-4 bg-slate-300 dark:bg-slate-600"></div>
            <span className="flex items-center gap-2 text-sm">
              <Scale className="w-4 h-4 text-finance-accent" />
              <span className="font-semibold text-slate-900 dark:text-white">Grounded:</span> 
              {metrics.groundedness ? 'Yes ✅' : 'No ❌'}
            </span>
          </div>
        </div>
        </div>
        <button 
          onClick={async () => {
            try {
              const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
              const response = await fetch(`${API_BASE_URL}/export`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ thread_id: payload.threadId })
              });
              
              if (!response.ok) throw new Error("Export failed");
              
              const blob = await response.blob();
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              
              const disposition = response.headers.get('Content-Disposition');
              let filename = 'report.pdf';
              if (disposition && disposition.includes('filename=')) {
                filename = disposition.split('filename=')[1].replace(/["']/g, '');
              }
              
              a.download = filename;
              document.body.appendChild(a);
              a.click();
              window.URL.revokeObjectURL(url);
              document.body.removeChild(a);
            } catch (err) {
              console.error("Failed to export PDF:", err);
              alert("Failed to export PDF");
            }
          }}
          className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-md text-sm font-medium transition-colors shrink-0">
          Export PDF
        </button>
      </div>

      <div className="space-y-10">
        
        <section>
          <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-200 mb-4 flex items-center gap-2">
            Executive Summary
          </h3>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-[17px]">
            {report.executive_summary}
          </p>
        </section>

        <div className="grid md:grid-cols-2 gap-6">
          <section className="p-5 bg-emerald-50/50 dark:bg-emerald-900/10 rounded-xl border border-emerald-200/50 dark:border-emerald-900/30">
            <h3 className="text-lg font-semibold text-emerald-800 dark:text-emerald-400 mb-3 flex items-center gap-2">
              <TrendingUp className="w-5 h-5" /> Bull Case
            </h3>
            <p className="text-emerald-900/80 dark:text-emerald-200/80 leading-relaxed text-[15px]">
              {report.bull_case}
            </p>
          </section>
          <section className="p-5 bg-red-50/50 dark:bg-red-900/10 rounded-xl border border-red-200/50 dark:border-red-900/30">
            <h3 className="text-lg font-semibold text-red-800 dark:text-red-400 mb-3 flex items-center gap-2">
              <TrendingDown className="w-5 h-5" /> Bear Case
            </h3>
            <p className="text-red-900/80 dark:text-red-200/80 leading-relaxed text-[15px]">
              {report.bear_case}
            </p>
          </section>
        </div>
        
        <section>
          <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-200 mb-4 flex items-center gap-2">
            Synthesized View
          </h3>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-[17px]">
            {report.synthesized_view}
          </p>
        </section>

        <section>
          <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-200 mb-6 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-finance-accent" /> Financials & Valuation
          </h3>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-slate-50 dark:bg-slate-800/40 p-5 rounded-lg border border-slate-200 dark:border-slate-700/50">
              <h4 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">Key Ratios</h4>
              <table className="w-full text-left border-collapse">
                <tbody>
                  {Object.entries(ratios).map(([key, val]) => {
                    if (typeof val === 'object') return null; // Skip non-numeric fields if any
                    return (
                    <tr key={key} className="border-b border-slate-200 dark:border-slate-700/50 last:border-0">
                      <td className="py-2.5 text-[15px] text-slate-700 dark:text-slate-300 capitalize">{key.replace(/_/g, ' ')}</td>
                      <td className="py-2.5 text-right font-medium text-slate-900 dark:text-white">
                        {typeof val === 'number' ? val.toLocaleString(undefined, {maximumFractionDigits: 2}) : val}
                      </td>
                    </tr>
                  )})}
                </tbody>
              </table>
            </div>
            <div className="bg-slate-50 dark:bg-slate-800/40 p-5 rounded-lg border border-slate-200 dark:border-slate-700/50">
              <h4 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">DCF Scenarios</h4>
              <table className="w-full text-left border-collapse mb-6">
                <tbody>
                  {['bear_case', 'base_case', 'bull_case'].map((scenario) => {
                    const val = valuation[scenario];
                    if (!val) return null;
                    return (
                    <tr key={scenario} className="border-b border-slate-200 dark:border-slate-700/50 last:border-0">
                      <td className="py-2.5 text-[15px] text-slate-700 dark:text-slate-300 capitalize">{scenario.replace('_', ' ')}</td>
                      <td className="py-2.5 text-right font-medium text-slate-900 dark:text-white">${val.toLocaleString()}</td>
                    </tr>
                  )})}
                </tbody>
              </table>
              <SensitivityGrid dcfValuation={valuation} />
            </div>
          </div>
          <RatioTrendChart ratios={ratios} />
        </section>

        {redFlags.length > 0 && (
          <section className="bg-amber-50/30 dark:bg-amber-900/5 p-6 rounded-xl border border-amber-200/50 dark:border-amber-800/30">
            <h3 className="text-lg font-semibold text-amber-700 dark:text-amber-500 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" /> Verified Red Flags
            </h3>
            <ul className="space-y-3 text-[15px] text-slate-700 dark:text-slate-300">
              {redFlags.map((flag, idx) => (
                <li key={idx} className="flex gap-3">
                  <span className="text-amber-500 font-bold">•</span>
                  <span><strong>{flag.type}:</strong> {flag.description}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
        
        {citations.length > 0 && (
        <section className="pt-6 border-t border-slate-200 dark:border-slate-700">
          <h3 className="text-sm font-semibold text-red-500 uppercase tracking-wider mb-4">Unsupported Claims (Citation Issues)</h3>
          <ul className="list-disc pl-5 text-sm text-red-600 dark:text-red-400 space-y-2">
            {citations.map((cite, idx) => (
              <li key={idx}><strong>{cite.claim}</strong>: {cite.reasoning}</li>
            ))}
          </ul>
        </section>
        )}
      </div>
      
      <div className="mt-8 text-center text-xs text-slate-400 dark:text-slate-500 border-t border-slate-200 dark:border-slate-700 pt-4">
        {report.disclaimer || "This is research synthesis, not investment advice."}
      </div>
    </div>
  );
}
