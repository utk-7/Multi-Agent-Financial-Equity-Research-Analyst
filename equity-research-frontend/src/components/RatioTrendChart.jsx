import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell, ReferenceLine } from 'recharts';
import { Activity } from 'lucide-react';

export default function RatioTrendChart({ ratios }) {
  if (!ratios || Object.keys(ratios).length === 0) return null;
  
  // Convert flat object of ratios into an array suitable for Recharts
  // e.g. { gross_margin: 0.469, operating_margin: 0.32, ... }
  // to [{ name: 'Gross Margin', value: 0.469, type: 'margin' }, ...]
  
  const data = Object.entries(ratios)
    .filter(([_, val]) => typeof val === 'number')
    .map(([key, val]) => {
      const isPercent = key.includes('margin') || key.includes('conversion') || key.includes('roe');
      
      let fill = '#3b82f6'; // default blue
      if (key.includes('margin')) fill = '#10b981'; // emerald
      else if (key.includes('debt') || key.includes('leverage')) fill = '#f59e0b'; // amber
      else if (key.includes('liquidity') || key.includes('current')) fill = '#6366f1'; // indigo
      else if (key.includes('conversion')) fill = '#0ea5e9'; // sky
      
      return {
        name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        rawName: key,
        value: isPercent ? val * 100 : val,
        isPercent,
        fill
      };
    });

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-900/95 border border-slate-700/50 p-3 rounded-lg shadow-xl text-slate-200 text-sm">
          <p className="font-semibold text-white mb-1">{label}</p>
          <p className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: data.fill }}></span>
            {data.isPercent ? `${data.value.toFixed(2)}%` : data.value.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full bg-white dark:bg-finance-card p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm mt-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <Activity className="w-5 h-5 text-finance-accent" />
          Point-in-Time Ratio Analysis
        </h3>
      </div>
      
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.2} />
            <XAxis 
              dataKey="name" 
              tick={{ fill: '#64748b', fontSize: 12 }} 
              tickLine={false}
              axisLine={{ stroke: '#cbd5e1' }}
              angle={-45}
              textAnchor="end"
            />
            <YAxis 
              tick={{ fill: '#64748b', fontSize: 12 }} 
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(148, 163, 184, 0.1)' }} />
            <ReferenceLine y={0} stroke="#94a3b8" />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
