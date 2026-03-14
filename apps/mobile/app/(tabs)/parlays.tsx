import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { useLucrixStore } from '@/store/useLucrixStore';
import { API, apiFetch } from '@/lib/api';
import * as Haptics from 'expo-haptics';

export default function ParlayScreen() {
    const { parlayLegs, removeLeg, clearParlay } = useLucrixStore();

    const calculatePayout = () => {
        if (parlayLegs.length === 0) return '0.00';
        const combined = parlayLegs.reduce((acc: number) => acc * 1.91, 1);
        return (100 * combined).toFixed(2);
    };

    const submitParlay = async () => {
        try {
            await apiFetch(API.parlayValidate(), { method: 'POST', body: JSON.stringify({ legs: parlayLegs }) });
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
            Alert.alert('✅ Parlay Validated', 'Your parlay looks good!');
        } catch {
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
            Alert.alert('❌ Validation Failed', 'Check your selections.');
        }
    };

    return (
        <View style={styles.root}>
            <View style={styles.header}>
                <Text style={styles.title}>⚡ Parlay Builder</Text>
                {parlayLegs.length > 0 && (
                    <TouchableOpacity onPress={clearParlay}>
                        <Text style={styles.clearBtn}>Clear All</Text>
                    </TouchableOpacity>
                )}
            </View>

            {parlayLegs.length === 0 ? (
                <View style={styles.empty}>
                    <Text style={styles.emptyIcon}>🎯</Text>
                    <Text style={styles.emptyText}>No legs added yet</Text>
                    <Text style={styles.emptySubtext}>Go to Props and tap "+ Add to Parlay"</Text>
                </View>
            ) : (
                <ScrollView style={styles.legs}>
                    {parlayLegs.map((leg: any) => (
                        <View key={leg.id} style={styles.legCard}>
                            <View style={styles.legInfo}>
                                <Text style={styles.legLabel}>{leg.label}</Text>
                                <Text style={styles.legMeta}>{leg.team} · {leg.hitRate}% hit rate</Text>
                            </View>
                            <TouchableOpacity onPress={() => removeLeg(leg.id)} style={styles.removeBtn}>
                                <Text style={styles.removeX}>✕</Text>
                            </TouchableOpacity>
                        </View>
                    ))}
                </ScrollView>
            )}

            {parlayLegs.length >= 2 && (
                <View style={styles.footer}>
                    <View style={styles.payoutRow}>
                        <Text style={styles.payoutLabel}>{parlayLegs.length}-Leg Parlay</Text>
                        <Text style={styles.payoutValue}>${calculatePayout()} per $100</Text>
                    </View>
                    <TouchableOpacity style={styles.submitBtn} onPress={submitParlay}>
                        <Text style={styles.submitBtnText}>Validate Parlay</Text>
                    </TouchableOpacity>
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    root: { flex: 1, backgroundColor: '#0a0a0f' },
    header: {
        flexDirection: 'row', justifyContent: 'space-between',
        alignItems: 'center', padding: 20, paddingTop: 60,
    },
    title: { color: '#f0f0ff', fontSize: 22, fontWeight: '800' },
    clearBtn: { color: '#ff4466', fontSize: 14, fontWeight: '600' },
    empty: { flex: 1, alignItems: 'center', justifyContent: 'center' },
    emptyIcon: { fontSize: 48, marginBottom: 12 },
    emptyText: { color: '#f0f0ff', fontSize: 18, fontWeight: '700' },
    emptySubtext: { color: '#9090aa', fontSize: 13, marginTop: 6 },
    legs: { flex: 1, paddingHorizontal: 16 },
    legCard: {
        backgroundColor: '#16161f', borderRadius: 12, padding: 16,
        flexDirection: 'row', justifyContent: 'space-between',
        alignItems: 'center', marginBottom: 8, borderWidth: 1, borderColor: '#2a2a3a',
    },
    legInfo: { flex: 1 },
    legLabel: { color: '#f0f0ff', fontWeight: '700', fontSize: 14 },
    legMeta: { color: '#9090aa', fontSize: 12, marginTop: 4 },
    removeBtn: { padding: 8 },
    removeX: { color: '#ff4466', fontSize: 16, fontWeight: '800' },
    footer: {
        backgroundColor: '#111118', borderTopWidth: 1, borderTopColor: '#2a2a3a',
        padding: 20, paddingBottom: 36,
    },
    payoutRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
    payoutLabel: { color: '#9090aa', fontSize: 14 },
    payoutValue: { color: '#00ff88', fontSize: 16, fontWeight: '800' },
    submitBtn: {
        backgroundColor: '#7c3aed', borderRadius: 12,
        paddingVertical: 16, alignItems: 'center',
    },
    submitBtnText: { color: '#fff', fontWeight: '800', fontSize: 16 },
});
