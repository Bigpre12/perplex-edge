import { View, Text, StyleSheet } from 'react-native';
import { Link } from 'expo-router';

export default function NotFoundScreen() {
    return (
        <View style={styles.root}>
            <Text style={styles.title}>Page not found</Text>
            <Link href="/" style={styles.link}>Go to Dashboard</Link>
        </View>
    );
}

const styles = StyleSheet.create({
    root: { flex: 1, backgroundColor: '#0a0a0f', alignItems: 'center', justifyContent: 'center' },
    title: { color: '#f0f0ff', fontSize: 20, fontWeight: '700', marginBottom: 16 },
    link: { color: '#7c3aed', fontSize: 14, fontWeight: '600' },
});
