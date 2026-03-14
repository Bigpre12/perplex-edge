import { View, Text, FlatList, StyleSheet } from 'react-native';
import { useQuery } from '@tanstack/react-query';
import { API, apiFetch } from '@/lib/api';
import { useLucrixStore } from '@/store/useLucrixStore';
import { useAlerts } from '@/hooks/useAlerts';

export default function AlertsScreen() {
    const { activeSport } = useLucrixStore();
    useAlerts(activeSport);

    const { data = [], isLoading } = useQuery({
        queryKey: ['alerts', activeSport],
        queryFn: async () => {
            const res = await apiFetch<any>(API.alerts(activeSport));
            return Array.isArray(res) ? res : (res?.items || []);
        },
        refetchInterval: 20_000,
    });

    return (
        <View style={styles.root}>
            <View style={styles.header}>
                <Text style={styles.title}>🔔 Live Alerts</Text>
            </View>

            {data.length === 0 ? (
                <View style={styles.empty}>
                    <Text style={styles.emptyIcon}>📡</Text>
                    <Text style={styles.emptyText}>No alerts right now</Text>
                    <Text style={styles.emptySubtext}>We'll notify you when something fires</Text>
                </View>
            ) : (
                <FlatList
                    data={data}
                    keyExtractor={(item: any) => item.id}
                    contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 100 }}
                    renderItem={({ item }) => (
                        <View style={styles.alertCard}>
                            <Text style={styles.alertType}>{item.type?.toUpperCase() ?? 'ALERT'}</Text>
                            <Text style={styles.alertMessage}>{item.message}</Text>
                            <Text style={styles.alertTime}>{new Date(item.timestamp).toLocaleTimeString()}</Text>
                        </View>
                    )}
                    ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
                />
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    root: { flex: 1, backgroundColor: '#0a0a0f' },
    header: { paddingHorizontal: 20, paddingTop: 60, paddingBottom: 12 },
    title: { color: '#f0f0ff', fontSize: 22, fontWeight: '800' },
    empty: { flex: 1, alignItems: 'center', justifyContent: 'center' },
    emptyIcon: { fontSize: 48, marginBottom: 12 },
    emptyText: { color: '#f0f0ff', fontSize: 18, fontWeight: '700' },
    emptySubtext: { color: '#9090aa', fontSize: 13, marginTop: 6 },
    alertCard: {
        backgroundColor: '#16161f', borderRadius: 12, padding: 16,
        borderWidth: 1, borderColor: '#2a2a3a',
    },
    alertType: { color: '#7c3aed', fontSize: 10, fontWeight: '800', letterSpacing: 1, marginBottom: 4 },
    alertMessage: { color: '#f0f0ff', fontSize: 14, fontWeight: '600', lineHeight: 20 },
    alertTime: { color: '#9090aa', fontSize: 11, marginTop: 6 },
});
