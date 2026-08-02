import React from 'react';
import { AlertTriangle, TrendingUp, TrendingDown, BookOpen, BarChart3, Scale } from 'lucide-react';

export default function ReportView({ report }) {
  if (!report) return null;

  return (
    <div className="w-full max-w-4xl mx-auto p-8 bg-white dark:bg-finance-card rounded-xl border border-slate-200 dark:border-slate-700 shadow-xl overflow-hidden mt-6">
      
      {/* Header */}
      <div className="border-b border-slate-200 dark:border-slate-700 pb-6 mb-8 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-3">Final Investment Thesis</h2>
          <div className="flex flex-wrap gap-4 text-sm">
            <span className="flex items-center gap-1.5 px-3 py-1 bg-slate-100 dark:bg-slate-800 rounded-md border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300">
              <BookOpen className="w-4 h-4 text-finance-accent" />
              <span className="font-semibold text-slate-900 dark:text-white">Coverage:</span> 
              {report.eval_metrics.citation_coverage_pct}%
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1 bg-slate-100 dark:bg-slate-800 rounded-md border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300">
              <Scale className="w-4 h-4 text-finance-accent" />
              <span className="font-semibold text-slate-900 dark:text-white">Grounded:</span> 
              {report.eval_metrics.groundedness_flag ? 'Yes ✅' : 'No ❌'}
            </span>
          </div>
        </div>
        <button className="px-4 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-md text-sm font-medium transition-colors shrink-0">
          Export PDF
        </button>
      </div>

      <div className="space-y-10">
        
        {/* Executive Summary */}
        <section>
          <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-200 mb-4 flex items-center gap-2">
            Executive Summary
          </h3>
          <p className="text-slate-700 dark:text-slate-300 leading-relaxed text-[17px]">
            {report.thesis_summary}
          </p>
        </section>

        {/* Bull / Bear Cases */}
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

        {/* Financial Ratios & Valuation */}
        <section>
          <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-200 mb-6 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-finance-accent" /> Financials & Valuation
          </h3>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-slate-50 dark:bg-slate-800/40 p-5 rounded-lg border border-slate-200 dark:border-slate-700/50">
              <h4 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">Key Ratios</h4>
              <table className="w-full text-left border-collapse">
                <tbody>
                  {Object.entries(report.ratio_table || {}).map(([key, val]) => (
                    <tr key={key} className="border-b border-slate-200 dark:border-slate-700/50 last:border-0">
                      <td className="py-2.5 text-[15px] text-slate-700 dark:text-slate-300">{key}</td>
                      <td className="py-2.5 text-right font-medium text-slate-900 dark:text-white">{val}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="bg-slate-50 dark:bg-slate-800/40 p-5 rounded-lg border border-slate-200 dark:border-slate-700/50">
              <h4 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">DCF Scenarios</h4>
              <table className="w-full text-left border-collapse">
                <tbody>
                  {Object.entries(report.valuation_range || {}).map(([scenario, val]) => (
                    <tr key={scenario} className="border-b border-slate-200 dark:border-slate-700/50 last:border-0">
                      <td className="py-2.5 text-[15px] text-slate-700 dark:text-slate-300">{scenario} Case</td>
                      <td className="py-2.5 text-right font-medium text-slate-900 dark:text-white">${val}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Red Flags */}
        {report.red_flags?.length > 0 && (
          <section className="bg-amber-50/30 dark:bg-amber-900/5 p-6 rounded-xl border border-amber-200/50 dark:border-amber-800/30">
            <h3 className="text-lg font-semibold text-amber-700 dark:text-amber-500 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" /> Verified Red Flags
            </h3>
            <ul className="space-y-3 text-[15px] text-slate-700 dark:text-slate-300">
              {report.red_flags.map((flag, idx) => (
                <li key={idx} className="flex gap-3">
                  <span className="text-amber-500 font-bold">•</span>
                  <span>{flag.description}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
        
        {/* Citations */}
        <section className="pt-6 border-t border-slate-200 dark:border-slate-700">
          <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">Sources & Citations</h3>
          <ol className="list-decimal pl-5 text-sm text-slate-600 dark:text-slate-500 space-y-2">
            {report.citations?.map((cite, idx) => (
              <li key={idx}>{cite}</li>
            ))}
          </ol>
        </section>
      </div>
    </div>
  );
}
