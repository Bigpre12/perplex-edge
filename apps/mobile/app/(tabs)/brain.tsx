import { View, Text, StyleSheet } from 'react-native';
import { useLucrixStore } from '@/store/useLucrixStore';
import BrainCard from '@/components/brain/BrainCard';

export default function BrainScreen() {
    const { activeSport } = useLucrixStore();

    return (
        <View style={styles.root}>
            <View style={styles.header}>
                <Text style={styles.title}>🧠 Lucrix Brain</Text>
            </View>
            <BrainCard sport={activeSport} />
        </View>
    );
}

const styles = StyleSheet.create({
    root: { flex: 1, backgroundColor: '#0a0a0f' },
    header: { paddingHorizontal: 20, paddingTop: 60, paddingBottom: 12 },
    title: { color: '#f0f0ff', fontSize: 22, fontWeight: '800' },
});
