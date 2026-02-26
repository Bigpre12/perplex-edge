/* eslint-disable @typescript-eslint/no-unused-vars */
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts';

interface TrendData {
    game: string;
    value: number;
    hit: boolean;
}

interface TrendChartProps {
    data: TrendData[];
    line: number;
    statType: string;
}

export default function TrendChart({ data, line, statType }: TrendChartProps) {
    return (
        <div className="w-full h-32 mt-2">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                    <XAxis
                        dataKey="game"
                        hide
                    />
                    <YAxis
                        tick={{ fill: '#94a3b8', fontSize: 10 }}
                        width={25}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#0f1719',
                            border: '1px solid #1e293b',
                            borderRadius: '8px',
                            fontSize: '10px'
                        }}
                        itemStyle={{ color: '#f1f5f9' }}
                    />
                    <ReferenceLine y={line} stroke="#94a3b8" strokeDasharray="3 3" />
                    <Bar dataKey="value" radius={[2, 2, 0, 0]}>
                        {data.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={entry.value >= line ? '#0df233' : '#ff4d4d'}
                                fillOpacity={0.6}
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
            <div className="flex justify-between items-center mt-1 px-1">
                <p className="text-[9px] text-slate-500 font-bold uppercase tracking-tighter">
                    Last 5: {data.filter(d => d.value >= line).length}/5 HITS
                </p>
                <p className="text-[9px] text-slate-300 font-mono">Line: {line}</p>
            </div>
        </div>
    );
}
