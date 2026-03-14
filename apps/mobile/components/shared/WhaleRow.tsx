import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { useLucrixStore } from '@/store/useLucrixStore';
import { API, apiFetch, isApiError } from '@/lib/api';
import { SportKey } from '@/lib/sports.config';
import { TrendingUp, Users, Activity } from 'lucide-react-native';

export default function WhaleRow({ sport }: { sport: SportKey }) {
    const { data: signals = [] } = useQuery({
        queryKey: ['sharp-money', sport],
        queryFn: async () => {
            const res = await apiFetch<any>(API.sharpMoney(sport));
            if (isApiError(res)) return [];
            return Array.isArray(res) ? res : (res?.items || []);
        },
        refetchInterval: 45_000,
    });

    if (signals.length === 0) return null;

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <TrendingUp size={14} color="#06b6d4" />
                <Text style={styles.title}>SHARP SIGNALS</Text>
            </View>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.scroll}>
                {signals.map((s: any) => (
                    <View key={s.id} style={styles.chip}>
                        <Text style={styles.chipText}>{s.player} {s.stat}</Text>
                        <View style={styles.badge}>
                            <Text style={styles.badgeText}>SHARP</Text>
                        </View>
                    </View>
                ))}
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { marginTop: 12, marginBottom: 4 },
    header: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 20, marginBottom: 8 },
    title: { color: '#06b6d4', fontSize: 10, fontWeight: '800', letterSpacing: 1 },
    scroll: { paddingHorizontal: 16, gap: 8 },
    chip: {
        backgroundColor: '#16161f', borderRadius: 12, paddingHorizontal: 12, paddingVertical: 10,
        borderWidth: 1, borderColor: '#06b6d433', flexDirection: 'row', alignItems: 'center', gap: 8,
    },
    chipText: { color: '#f0f0ff', fontSize: 13, fontWeight: '600' },
    badge: { backgroundColor: '#06b6d422', borderRadius: 4, paddingHorizontal: 4, paddingVertical: 2 },
    badgeText: { color: '#06b6d4', fontSize: 9, fontWeight: '900' },
});
