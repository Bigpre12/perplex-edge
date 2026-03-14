import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { API, apiFetch, isApiError } from '@/lib/api';
import { SportKey } from '@/lib/sports.config';

interface Decision {
    id: string; pick: string; confidence: number; edge: number;
    reasoning: string; timestamp: string; result?: 'win' | 'loss' | 'pending';
}

interface Metrics {
    winRate: number; roi: number; totalPicks: number; streak: number; avgEdge: number;
}

export default function BrainCard({ sport, compact = false }: { sport: SportKey; compact?: boolean }) {
    const [tab, setTab] = useState<'live' | 'metrics'>('live');

    const { data: decisions = [] } = useQuery({
        queryKey: ['brain-decisions', sport],
        queryFn: async () => {
            const res = await apiFetch<any>(API.brainDecisions(sport, compact ? 3 : 5));
            if (isApiError(res)) return [];
            return Array.isArray(res) ? res : [];
        },
        refetchInterval: 60_000,
    });

    const { data: metrics } = useQuery({
        queryKey: ['brain-metrics', sport],
        queryFn: async () => {
            const res = await apiFetch<Metrics>(API.brainMetrics(sport));
            return isApiError(res) ? null : res;
        },
        refetchInterval: 60_000,
    });

    return (
        <View style={styles.panel}>
            <View style={styles.header}>
                <Text style={styles.headerText}>🧠 Lucrix Brain</Text>
                <View style={styles.tabs}>
                    <TouchableOpacity onPress={() => setTab('live')} style={[styles.tab, tab === 'live' && styles.tabActive]}>
                        <Text style={[styles.tabText, tab === 'live' && styles.tabTextActive]}>Live</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => setTab('metrics')} style={[styles.tab, tab === 'metrics' && styles.tabActive]}>
                        <Text style={[styles.tabText, tab === 'metrics' && styles.tabTextActive]}>Metrics</Text>
                    </TouchableOpacity>
                </View>
            </View>

            {tab === 'live' && (
                <ScrollView style={{ maxHeight: compact ? 200 : undefined }} scrollEnabled={!compact}>
                    {(decisions as Decision[]).length === 0 && (
                        <Text style={styles.emptyText}>No active decisions — brain is analyzing...</Text>
                    )}
                    {(decisions as Decision[]).map(d => (
                        <View key={d.id} style={[styles.decisionCard, {
                            borderLeftColor: d.result === 'win' ? '#00ff88' : d.result === 'loss' ? '#ff4466' : '#7c3aed'
                        }]}>
                            <Text style={styles.pick}>{d.pick}</Text>
                            <View style={styles.metaRow}>
                                <Text style={styles.conf}>{d.confidence}% conf</Text>
                                <Text style={styles.edge}>+{d.edge}% edge</Text>
                            </View>
                            {!compact && <Text style={styles.reasoning}>{d.reasoning}</Text>}
                        </View>
                    ))}
                </ScrollView>
            )}

            {tab === 'metrics' && metrics && (
                <View style={styles.metricsGrid}>
                    <MetricBox label="Win Rate" value={`${metrics.winRate}%`} good={metrics.winRate > 55} />
                    <MetricBox label="ROI" value={`${metrics.roi}%`} good={metrics.roi > 0} />
                    <MetricBox label="Picks" value={metrics.totalPicks} />
                    <MetricBox label="Streak" value={`${metrics.streak > 0 ? '+' : ''}${metrics.streak}`} good={metrics.streak > 0} />
                    <MetricBox label="Avg Edge" value={`${metrics.avgEdge}%`} good={metrics.avgEdge > 3} />
                </View>
            )}
        </View>
    );
}

function MetricBox({ label, value, good }: { label: string; value: any; good?: boolean }) {
    return (
        <View style={mStyles.box}>
            <Text style={mStyles.label}>{label}</Text>
            <Text style={[mStyles.value, {
                color: good === true ? '#00ff88' : good === false ? '#ff4466' : '#f0f0ff'
            }]}>{value}</Text>
        </View>
    );
}

const mStyles = StyleSheet.create({
    box: { backgroundColor: '#1e1e2a', borderRadius: 8, padding: 12, minWidth: '45%' },
    label: { color: '#9090aa', fontSize: 11, marginBottom: 4 },
    value: { fontSize: 20, fontWeight: '800' },
});

const styles = StyleSheet.create({
    panel: {
        backgroundColor: '#16161f', borderRadius: 12, padding: 16,
        marginHorizontal: 16, borderWidth: 1, borderColor: '#2a2a3a',
    },
    header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
    headerText: { color: '#f0f0ff', fontWeight: '700', fontSize: 15 },
    tabs: { flexDirection: 'row', gap: 4 },
    tab: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 6, borderWidth: 1, borderColor: '#2a2a3a' },
    tabActive: { backgroundColor: '#7c3aed', borderColor: '#7c3aed' },
    tabText: { color: '#9090aa', fontSize: 11, fontWeight: '600' },
    tabTextActive: { color: '#fff' },
    emptyText: { color: '#9090aa', fontSize: 13, textAlign: 'center', padding: 20 },
    decisionCard: {
        backgroundColor: '#1e1e2a', borderRadius: 8, padding: 12,
        borderLeftWidth: 3, marginBottom: 8,
    },
    pick: { color: '#f0f0ff', fontWeight: '700', fontSize: 13, marginBottom: 4 },
    metaRow: { flexDirection: 'row', gap: 12 },
    conf: { color: '#9090aa', fontSize: 11 },
    edge: { color: '#00ff88', fontSize: 11, fontWeight: '700' },
    reasoning: { color: '#9090aa', fontSize: 12, marginTop: 6, lineHeight: 18 },
    metricsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
});
