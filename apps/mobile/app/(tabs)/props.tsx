import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { useLucrixStore } from '@/store/useLucrixStore';
import SportSelector from '@/components/shared/SportSelector';
import PropsFeed from '@/components/props/PropsFeed';

export default function PropsScreen() {
    const { activeSport } = useLucrixStore();

    return (
        <View style={styles.root}>
            <View style={styles.header}>
                <Text style={styles.title}>Player Props</Text>
            </View>
            <SportSelector />
            <ScrollView style={{ flex: 1 }} contentContainerStyle={{ paddingBottom: 100 }} showsVerticalScrollIndicator={false}>
                <PropsFeed sport={activeSport} limit={50} />
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    root: { flex: 1, backgroundColor: '#0a0a0f' },
    header: { paddingHorizontal: 20, paddingTop: 60, paddingBottom: 12 },
    title: { color: '#f0f0ff', fontSize: 22, fontWeight: '800' },
});
