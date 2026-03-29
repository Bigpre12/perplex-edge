"use client";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from "framer-motion";

interface TrendPoint {
    date: string;
    win_rate: number;
}

interface PerformanceChartProps {
    data: TrendPoint[];
    loading?: boolean;
}

export function PerformanceChart({ data, loading }: PerformanceChartProps) {
    if (loading) {
        return (
            <div className="h-[300px] w-full bg-lucrix-surface border border-lucrix-border rounded-2xl flex items-center justify-center">
                <div className="animate-pulse flex flex-col items-center gap-3">
                    <div className="w-12 h-12 bg-lucrix-elevated rounded-full" />
                    <span className="text-[10px] text-textMuted uppercase font-black">Synthesizing Trend Data...</span>
                </div>
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="h-[300px] w-full bg-lucrix-surface border border-lucrix-border rounded-2xl flex items-center justify-center">
                <p className="text-xs text-textSecondary uppercase font-black opacity-50">Trend data will appear after 7 days of grading</p>
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-lucrix-surface border border-lucrix-border p-6 rounded-2xl shadow-card"
        >
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h3 className="text-sm font-black text-white uppercase tracking-widest font-display italic">Performance Trend</h3>
                    <p className="text-[10px] text-textMuted font-bold uppercase tracking-tight">Win Rate % over time (30D)</p>
                </div>
                <div className="flex gap-2">
                    <span className="text-[9px] bg-brand-success/10 text-brand-success border border-brand-success/20 px-2 py-0.5 rounded-sm font-black tracking-tighter uppercase">LIVE TRACE</span>
                </div>
            </div>

            <div className="h-[250px] w-full min-w-0" style={{ minWidth: 0 }}>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#2D2D3D" vertical={false} />
                        <XAxis 
                            dataKey="date" 
                            stroke="#52526D" 
                            fontSize={10} 
                            tickLine={false} 
                            axisLine={false} 
                            tickFormatter={(v) => v.split('-').slice(1).join('/')}
                        />
                        <YAxis 
                            stroke="#52526D" 
                            fontSize={10} 
                            tickLine={false} 
                            axisLine={false} 
                            domain={[0, 100]}
                            tickFormatter={(v) => `${v}%`}
                        />
                        <Tooltip 
                            contentStyle={{ 
                                backgroundColor: '#1A1B27', 
                                border: '1px solid #2D2D3D', 
                                borderRadius: '8px',
                                fontSize: '10px',
                                textTransform: 'uppercase',
                                fontStyle: 'italic',
                                fontWeight: '900'
                            }}
                            cursor={{ stroke: '#52526D', strokeWidth: 1 }}
                        />
                        <Line 
                            type="monotone" 
                            dataKey="win_rate" 
                            stroke="#7C3AED" 
                            strokeWidth={3} 
                            dot={{ fill: '#7C3AED', r: 4, strokeWidth: 2, stroke: '#1A1B27' }} 
                            activeDot={{ r: 6, fill: '#A78BFA' }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </motion.div>
    );
}
