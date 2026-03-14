'use client';
import { useEffect, useState } from 'react';
import { API, apiFetch, isApiError } from '@/lib/api';
import { SportKey } from '@/lib/sports.config';
import { useLucrixStore } from '@/store';

interface BrainDecision {
    id: string;
    pick: string;
    confidence: number;
    edge: number;
    reasoning: string;
    sport: string;
    timestamp: string;
    result?: 'win' | 'loss' | 'pending';
}

interface BrainMetrics {
    winRate: number;
    roi: number;
    totalPicks: number;
    streak: number;
    avgEdge: number;
}

export default function BrainPanel({ sport }: { sport: SportKey }) {
    const [decisions, setDecisions] = useState<BrainDecision[]>([]);
    const [metrics, setMetrics] = useState<BrainMetrics | null>(null);
    const [tab, setTab] = useState<'live' | 'metrics'>('live');
    const { backendOnline } = useLucrixStore();

    useEffect(() => {
        if (!backendOnline) return;
        const load = async () => {
            const [d, m] = await Promise.all([
                apiFetch<BrainDecision[]>(API.brainDecisions(sport, 5)),
                apiFetch<BrainMetrics>(API.brainMetrics(sport)),
            ]);

            if (!isApiError(d)) {
                setDecisions(Array.isArray(d) ? d : []);
            } else {
                setDecisions([]);
            }

            if (!isApiError(m)) {
                setMetrics(m);
            } else {
                setMetrics(null);
            }
        };
        load();
        const t = setInterval(load, 60000);
        return () => clearInterval(t);
    }, [sport, backendOnline]);

    return (
        <div className="brain-panel">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '1.2rem' }}>🧠</span>
                    <h3 style={{ fontWeight: 700, fontSize: '1rem', margin: 0 }}>Lucrix Brain</h3>
                </div>
                <div style={{ display: 'flex', gap: '4px' }}>
                    <button
                        onClick={() => setTab('live')}
                        style={{
                            padding: '5px 12px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer',
                            border: '1px solid #2a2a3a',
                            background: tab === 'live' ? '#7c3aed' : 'transparent',
                            color: tab === 'live' ? 'white' : '#9090aa',
                        }}
                    >
                        Live Picks
                    </button>
                    <button
                        onClick={() => setTab('metrics')}
                        style={{
                            padding: '5px 12px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer',
                            border: '1px solid #2a2a3a',
                            background: tab === 'metrics' ? '#7c3aed' : 'transparent',
                            color: tab === 'metrics' ? 'white' : '#9090aa',
                        }}
                    >
                        Metrics
                    </button>
                </div>
            </div>

            {tab === 'live' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {decisions.length === 0 && (
                        <p style={{ color: '#9090aa', fontSize: '0.85rem', textAlign: 'center', padding: '20px' }}>
                            No active decisions — brain is analyzing...
                        </p>
                    )}
                    {decisions.map(d => (
                        <div key={d.id} className="decision-card" style={{
                            borderLeft: `3px solid ${d.result === 'win' ? '#00ff88' : d.result === 'loss' ? '#ff4466' : '#7c3aed'}`,
                        }}>
                            <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '6px' }}>{d.pick}</div>
                            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '6px' }}>
                                <span style={{ fontSize: '0.75rem', color: '#9090aa' }}>
                                    <span style={{
                                        display: 'inline-block', height: '6px', width: `${d.confidence * 0.6}px`,
                                        background: 'linear-gradient(90deg, #7c3aed, #00ff88)',
                                        borderRadius: '3px', marginRight: '6px', verticalAlign: 'middle',
                                    }} />
                                    {d.confidence}% conf
                                </span>
                                <span style={{ fontSize: '0.75rem', color: '#00ff88', fontWeight: 600 }}>+{d.edge}% edge</span>
                            </div>
                            <div style={{ fontSize: '0.8rem', color: '#9090aa', lineHeight: 1.4 }}>{d.reasoning}</div>
                            <div style={{ fontSize: '0.7rem', color: '#666', marginTop: '6px' }}>
                                {new Date(d.timestamp).toLocaleTimeString()}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {tab === 'metrics' && metrics && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
                    <MetricCard label="Win Rate" value={`${metrics.winRate}%`} good={metrics.winRate > 55} />
                    <MetricCard label="ROI" value={`${metrics.roi}%`} good={metrics.roi > 0} />
                    <MetricCard label="Total Picks" value={metrics.totalPicks} />
                    <MetricCard label="Streak" value={`${metrics.streak > 0 ? '+' : ''}${metrics.streak}`} good={metrics.streak > 0} />
                    <MetricCard label="Avg Edge" value={`${metrics.avgEdge}%`} good={metrics.avgEdge > 3} />
                </div>
            )}

            {tab === 'metrics' && !metrics && (
                <p style={{ color: '#9090aa', fontSize: '0.85rem', textAlign: 'center', padding: '20px' }}>
                    No metrics data available
                </p>
            )}
        </div>
    );
}

function MetricCard({ label, value, good }: { label: string; value: any; good?: boolean }) {
    return (
        <div className="metric-card">
            <span style={{ fontSize: '0.75rem', color: '#9090aa', display: 'block', marginBottom: '4px' }}>{label}</span>
            <span style={{
                fontSize: '1.3rem', fontWeight: 800,
                color: good === true ? '#00ff88' : good === false ? '#ff4466' : '#f0f0ff',
            }}>
                {value}
            </span>
        </div>
    );
}
