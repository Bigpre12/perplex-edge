import { View, Text, StyleSheet } from 'react-native';

export default function StatusDot({ online }: { online: boolean }) {
    return (
        <View style={styles.row}>
            <View style={[styles.dot, { backgroundColor: online ? '#00ff88' : '#ff4466' }]} />
            <Text style={[styles.text, { color: online ? '#00ff88' : '#ff4466' }]}>
                {online ? 'LIVE' : 'OFFLINE'}
            </Text>
        </View>
    );
}

const styles = StyleSheet.create({
    row: { flexDirection: 'row', alignItems: 'center', gap: 6 },
    dot: { width: 8, height: 8, borderRadius: 4 },
    text: { fontSize: 10, fontWeight: '800', letterSpacing: 1 },
});
