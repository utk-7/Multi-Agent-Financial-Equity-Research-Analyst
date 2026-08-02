import React from 'react';
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ZAxis, Cell } from 'recharts';
import { Target, TrendingUp, AlertCircle } from 'lucide-react';

export default function SensitivityGrid({ dcfValuation }) {
  if (!dcfValuation) return null;
  
  // Create a stylized grid based on the valuation ranges
  // In a real application with a full grid, this would parse sensitivity_matrix from backend
  // For now, we will construct a visual based on Bear, Base, and Bull cases
  
  const baseValue = dcfValuation.base_case || 1;
  
  const data = [
    { name: 'Bear Case', value: dcfValuation.bear_case, fill: '#ef4444' }, // red-500
    { name: 'Base Case', value: dcfValuation.base_case, fill: '#3b82f6' }, // blue-500
    { name: 'Bull Case', value: dcfValuation.bull_case, fill: '#10b981' }  // emerald-500
  ].filter(d => d.value);

  // Format currency
  const formatValue = (val) => {
    if (val >= 1e12) return `$${(val / 1e12).toFixed(2)}T`;
    if (val >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
    if (val >= 1e6) return `$${(val / 1e6).toFixed(2)}M`;
    return `$${val.toLocaleString()}`;
  };

  return (
    <div className="w-full bg-white dark:bg-finance-card p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <Target className="w-5 h-5 text-finance-accent" />
          Valuation Sensitivity Range
        </h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {data.map((item, idx) => {
          const premiumDiscount = ((item.value - baseValue) / baseValue) * 100;
          return (
            <div key={idx} className={`p-4 rounded-lg border ${
              item.name === 'Base Case' ? 'bg-sky-50 dark:bg-sky-900/10 border-sky-200 dark:border-sky-800' : 
              'bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700/50'
            }`}>
              <div className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">{item.name}</div>
              <div className="text-2xl font-bold text-slate-900 dark:text-white mb-2">{formatValue(item.value)}</div>
              {item.name !== 'Base Case' && (
                <div className={`text-xs font-semibold flex items-center gap-1 ${premiumDiscount > 0 ? 'text-emerald-500' : 'text-red-500'}`}>
                  {premiumDiscount > 0 ? '+' : ''}{premiumDiscount.toFixed(1)}% vs Base
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      <div className="text-xs text-slate-500 dark:text-slate-400 italic flex items-center gap-1.5 mt-2">
        <AlertCircle className="w-4 h-4" />
        Note: DCF Valuation is highly sensitive to WACC and terminal growth rate assumptions.
      </div>
    </div>
  );
}
