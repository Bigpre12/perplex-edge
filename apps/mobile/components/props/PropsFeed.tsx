import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { API, apiFetch, isApiError } from '@/lib/api';
import { SportKey } from '@/lib/sports.config';
import { SPORTSBOOKS } from '@/lib/sportsbooks.config';
import { useLucrixStore } from '@/store/useLucrixStore';
import * as Haptics from 'expo-haptics';

import { useRouter } from 'expo-router';

interface Prop {
    id: string; player: string; team: string;
    stat: string; line: number; hitRate: number;
    grade: 'S' | 'A' | 'B' | 'C'; sharp: boolean;
    books: Record<string, { over: number; under: number }>;
    trend: 'up' | 'down' | 'flat';
}

export default function PropsFeed({ sport, limit = 20 }: { sport: SportKey; limit?: number }) {
    const { addLeg } = useLucrixStore();
    const router = useRouter();

    const { data: props = [], isLoading } = useQuery({
        queryKey: ['props', sport],
        queryFn: async () => {
            const res = await apiFetch<any>(API.props(sport));
            if (isApiError(res)) return [];
            return Array.isArray(res) ? res : [];
        },
        refetchInterval: 30_000,
    });

    const handleAdd = (prop: Prop) => {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
        addLeg({ ...prop, id: prop.id, label: `${prop.player} ${prop.stat} ${prop.line}` });
    };

    if (isLoading) return <PropsSkeleton />;

    return (
        <FlatList
            data={(props as Prop[]).slice(0, limit)}
            keyExtractor={p => p.id}
            scrollEnabled={false}
            renderItem={({ item }) => (
                <PropCard
                    prop={item}
                    onAdd={() => handleAdd(item)}
                    onPress={() => router.push(`/player/${item.id}`)}
                />
            )}
            ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
            ListEmptyComponent={
                <View style={styles.empty}>
                    <Text style={styles.emptyText}>No props available</Text>
                    <Text style={styles.emptySub}>Check back when games are scheduled</Text>
                </View>
            }
        />
    );
}

function PropCard({ prop, onAdd, onPress }: { prop: Prop; onAdd: () => void; onPress: () => void }) {
    const gradeColor: Record<string, string> = { S: '#00ff88', A: '#88ff00', B: '#ffcc00', C: '#ff8800' };

    return (
        <TouchableOpacity
            style={[styles.card, prop.sharp && styles.sharpCard]}
            onPress={onPress}
            activeOpacity={0.8}
        >
            <View style={styles.cardTop}>
                <View>
                    <Text style={styles.playerName}>{prop.player}</Text>
                    <Text style={styles.teamName}>{prop.team}</Text>
                </View>
                <Text style={[styles.grade, { color: gradeColor[prop.grade] }]}>{prop.grade}</Text>
            </View>

            <View style={styles.statRow}>
                <Text style={styles.stat}>{prop.stat}</Text>
                <Text style={styles.line}>{prop.line}</Text>
                <Text style={[styles.trend, {
                    color: prop.trend === 'up' ? '#00ff88' : prop.trend === 'down' ? '#ff4466' : '#9090aa'
                }]}>
                    {prop.trend === 'up' ? '↑' : prop.trend === 'down' ? '↓' : '→'}
                </Text>
            </View>

            <View style={styles.hitRateBar}>
                <View style={[styles.hitRateFill, { width: `${prop.hitRate}%` as any }]} />
            </View>
            <Text style={styles.hitRateText}>{prop.hitRate}% hit rate</Text>

            {prop.books && Object.keys(prop.books).length > 0 && (
                <View style={styles.booksRow}>
                    {Object.entries(prop.books).slice(0, 3).map(([book, odds]: any) => (
                        <View key={book} style={styles.bookChip}>
                            <Text style={styles.bookName}>{SPORTSBOOKS[book as keyof typeof SPORTSBOOKS]?.label ?? book}</Text>
                            <Text style={styles.bookOdds}>{odds.over > 0 ? '+' : ''}{odds.over}</Text>
                        </View>
                    ))}
                </View>
            )}

            {prop.sharp && <Text style={styles.sharpBadge}>🐋 Sharp Action</Text>}

            <TouchableOpacity style={styles.addBtn} onPress={onAdd}>
                <Text style={styles.addBtnText}>+ Add to Parlay</Text>
            </TouchableOpacity>
        </TouchableOpacity>
    );
}

function PropsSkeleton() {
    return (
        <View style={{ paddingHorizontal: 16 }}>
            {[...Array(5)].map((_, i) => <View key={i} style={styles.skeleton} />)}
        </View>
    );
}

const styles = StyleSheet.create({
    card: {
        backgroundColor: '#16161f', borderRadius: 12, padding: 16,
        borderWidth: 1, borderColor: '#2a2a3a', marginHorizontal: 16,
    },
    sharpCard: { borderColor: '#06b6d4' },
    cardTop: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
    playerName: { color: '#f0f0ff', fontSize: 15, fontWeight: '700' },
    teamName: { color: '#9090aa', fontSize: 12, marginTop: 2 },
    grade: { fontSize: 24, fontWeight: '900' },
    statRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 8 },
    stat: { color: '#9090aa', fontSize: 13 },
    line: { color: '#f0f0ff', fontSize: 18, fontWeight: '800' },
    trend: { fontSize: 16 },
    hitRateBar: { height: 4, backgroundColor: '#2a2a3a', borderRadius: 2, marginBottom: 4 },
    hitRateFill: { height: 4, backgroundColor: '#7c3aed', borderRadius: 2 },
    hitRateText: { color: '#9090aa', fontSize: 11, marginBottom: 8 },
    booksRow: { flexDirection: 'row', gap: 6, flexWrap: 'wrap', marginBottom: 8 },
    bookChip: {
        backgroundColor: '#1e1e2a', borderRadius: 6, paddingHorizontal: 8, paddingVertical: 4,
        flexDirection: 'row', gap: 4,
    },
    bookName: { color: '#9090aa', fontSize: 10 },
    bookOdds: { color: '#00ff88', fontSize: 10, fontWeight: '700' },
    sharpBadge: { color: '#06b6d4', fontSize: 11, marginBottom: 8 },
    addBtn: { backgroundColor: '#7c3aed', borderRadius: 8, paddingVertical: 10, alignItems: 'center' },
    addBtnText: { color: '#fff', fontWeight: '700', fontSize: 13 },
    skeleton: { height: 160, backgroundColor: '#16161f', borderRadius: 12, marginBottom: 8 },
    empty: { alignItems: 'center', padding: 40 },
    emptyText: { color: '#f0f0ff', fontSize: 16, fontWeight: '700' },
    emptySub: { color: '#9090aa', fontSize: 13, marginTop: 4 },
});
