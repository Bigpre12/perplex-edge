import { View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { API, apiFetch } from '@/lib/api';
import { useLucrixStore } from '@/store/useLucrixStore';
import { ChevronLeft, Share2, Star, TrendingUp, AlertTriangle } from 'lucide-react-native';
import * as Haptics from 'expo-haptics';

export default function PlayerDetail() {
    const { id } = useLocalSearchParams();
    const router = useRouter();
    const { activeSport, favoriteProps, toggleFavProp } = useLucrixStore();
    const isFav = favoriteProps.includes(id as string);

    const { data: stats, isLoading } = useQuery({
        queryKey: ['player-stats', id, activeSport],
        queryFn: () => apiFetch<any>(API.playerStats(activeSport, id as string)),
    });

    const handleToggleFav = () => {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        toggleFavProp(id as string);
    };

    if (isLoading) return (
        <View style={styles.loading}>
            <ActivityIndicator color="#7c3aed" />
        </View>
    );

    return (
        <View style={styles.root}>
            <View style={styles.header}>
                <TouchableOpacity onPress={() => router.back()} style={styles.iconBtn}>
                    <ChevronLeft color="#f0f0ff" />
                </TouchableOpacity>
                <Text style={styles.headerTitle}>Player Intel</Text>
                <View style={styles.headerRight}>
                    <TouchableOpacity onPress={handleToggleFav} style={styles.iconBtn}>
                        <Star color={isFav ? '#ffcc00' : '#9090aa'} fill={isFav ? '#ffcc00' : 'transparent'} />
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.iconBtn}>
                        <Share2 color="#9090aa" />
                    </TouchableOpacity>
                </View>
            </View>

            <ScrollView contentContainerStyle={styles.content}>
                <View style={styles.profileCard}>
                    <View style={styles.avatarPlaceholder} />
                    <View>
                        <Text style={styles.playerName}>{stats?.name || 'Unknown Player'}</Text>
                        <Text style={styles.playerMeta}>{stats?.team || 'Free Agent'} · {stats?.position || 'N/A'}</Text>
                    </View>
                </View>

                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Performance Metrics</Text>
                    <View style={styles.statsGrid}>
                        <StatBox label="L10 Avg" value={stats?.l10_avg || '--'} />
                        <StatBox label="Season Avg" value={stats?.season_avg || '--'} />
                        <StatBox label="Hit Rate" value={`${stats?.hit_rate || '0'}%`} highlight />
                        <StatBox label="Proj Value" value={stats?.projection || '--'} />
                    </View>
                </View>

                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Recent Game Log</Text>
                    {stats?.logs?.map((log: any, i: number) => (
                        <View key={i} style={styles.logRow}>
                            <Text style={styles.logDate}>{log.date}</Text>
                            <Text style={styles.logValue}>{log.value} {log.stat}</Text>
                            <Text style={log.hit ? styles.logHit : styles.logMiss}>{log.hit ? 'HIT' : 'MISS'}</Text>
                        </View>
                    )) || <Text style={styles.emptyText}>No recent data available.</Text>}
                </View>

                {stats?.injuries && (
                    <View style={styles.injuryCard}>
                        <AlertTriangle size={16} color="#ff8800" />
                        <Text style={styles.injuryText}>{stats.injuries}</Text>
                    </View>
                )}
            </ScrollView>
        </View>
    );
}

function StatBox({ label, value, highlight }: { label: string; value: any; highlight?: boolean }) {
    return (
        <View style={styles.statBox}>
            <Text style={styles.statLabel}>{label}</Text>
            <Text style={[styles.statValue, highlight && { color: '#00ff88' }]}>{value}</Text>
        </View>
    );
}

const styles = StyleSheet.create({
    root: { flex: 1, backgroundColor: '#0a0a0f' },
    loading: { flex: 1, backgroundColor: '#0a0a0f', justifyContent: 'center' },
    header: {
        flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
        paddingHorizontal: 16, paddingTop: 60, paddingBottom: 16, borderBottomWidth: 1, borderBottomColor: '#2a2a3a',
    },
    headerTitle: { color: '#f0f0ff', fontSize: 16, fontWeight: '700' },
    headerRight: { flexDirection: 'row', gap: 12 },
    iconBtn: { padding: 4 },
    content: { padding: 20 },
    profileCard: { flexDirection: 'row', alignItems: 'center', gap: 16, marginBottom: 24 },
    avatarPlaceholder: { width: 64, height: 64, borderRadius: 32, backgroundColor: '#1e1e2a' },
    playerName: { color: '#f0f0ff', fontSize: 22, fontWeight: '800' },
    playerMeta: { color: '#9090aa', fontSize: 14, marginTop: 4 },
    section: { marginBottom: 24 },
    sectionTitle: { color: '#9090aa', fontSize: 11, fontWeight: '800', letterSpacing: 1, marginBottom: 16 },
    statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
    statBox: { backgroundColor: '#16161f', borderRadius: 12, padding: 16, flex: 1, minWidth: '45%', borderWidth: 1, borderColor: '#2a2a3a' },
    statLabel: { color: '#9090aa', fontSize: 10, marginBottom: 4 },
    statValue: { color: '#f0f0ff', fontSize: 18, fontWeight: '800' },
    logRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#1e1e2a' },
    logDate: { color: '#9090aa', fontSize: 12 },
    logValue: { color: '#f0f0ff', fontSize: 13, fontWeight: '600' },
    logHit: { color: '#00ff88', fontSize: 11, fontWeight: '800' },
    logMiss: { color: '#ff4466', fontSize: 11, fontWeight: '800' },
    emptyText: { color: '#5a5a7a', fontSize: 13, fontStyle: 'italic' },
    injuryCard: { backgroundColor: '#ff880011', borderRadius: 8, padding: 12, flexDirection: 'row', gap: 10, alignItems: 'center', borderWidth: 1, borderColor: '#ff880033' },
    injuryText: { color: '#ff8800', fontSize: 12, fontWeight: '600', flex: 1 },
});
