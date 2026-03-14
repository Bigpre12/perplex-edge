import { ScrollView, View, Text, RefreshControl, StyleSheet } from 'react-native';
import { useState } from 'react';
import { useLucrixStore } from '@/store/useLucrixStore';
import SportSelector from '@/components/shared/SportSelector';
import StatusDot from '@/components/shared/StatusDot';
import BrainCard from '@/components/brain/BrainCard';
import PropsFeed from '@/components/props/PropsFeed';
import WhaleRow from '@/components/shared/WhaleRow';

export default function Dashboard() {
    const [refreshing, setRefreshing] = useState(false);
    const { activeSport, backendOnline } = useLucrixStore();

    const onRefresh = async () => {
        setRefreshing(true);
        await new Promise(r => setTimeout(r, 1000));
        setRefreshing(false);
    };

    return (
        <View style={styles.root}>
            <View style={styles.header}>
                <Text style={styles.logo}>⚡ LUCRIX</Text>
                <StatusDot online={backendOnline} />
            </View>
            <SportSelector />

            <ScrollView
                style={styles.scroll}
                contentContainerStyle={styles.content}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#7c3aed" />}
                showsVerticalScrollIndicator={false}
            >
                <WhaleRow sport={activeSport} />
                <View style={{ height: 12 }} />
                <BrainCard sport={activeSport} compact />
                <View style={{ height: 12 }} />
                <PropsFeed sport={activeSport} limit={10} />
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    root: { flex: 1, backgroundColor: '#0a0a0f' },
    header: {
        flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
        paddingHorizontal: 20, paddingTop: 60, paddingBottom: 12,
        backgroundColor: '#111118', borderBottomWidth: 1, borderBottomColor: '#2a2a3a',
    },
    logo: { color: '#7c3aed', fontSize: 20, fontWeight: '900', letterSpacing: -0.5 },
    scroll: { flex: 1 },
    content: { paddingBottom: 100 },
});
