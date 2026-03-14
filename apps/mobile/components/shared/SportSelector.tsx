import { ScrollView, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { SPORTS_CONFIG, ACTIVE_SPORTS } from '@/lib/sports.config';
import { useLucrixStore } from '@/store/useLucrixStore';
import * as Haptics from 'expo-haptics';

export default function SportSelector() {
    const { activeSport, setActiveSport } = useLucrixStore();

    return (
        <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.scroll}
            contentContainerStyle={styles.container}
        >
            {ACTIVE_SPORTS.map(key => {
                const s = SPORTS_CONFIG[key];
                const active = activeSport === key;
                return (
                    <TouchableOpacity
                        key={key}
                        style={[styles.chip, active && styles.chipActive]}
                        onPress={() => { Haptics.selectionAsync(); setActiveSport(key); }}
                    >
                        <Text style={styles.icon}>{s.icon}</Text>
                        <Text style={[styles.label, active && styles.labelActive]}>{s.label}</Text>
                    </TouchableOpacity>
                );
            })}
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    scroll: { maxHeight: 52 },
    container: { paddingHorizontal: 16, gap: 8, alignItems: 'center' },
    chip: {
        flexDirection: 'row', alignItems: 'center', gap: 4,
        paddingHorizontal: 12, paddingVertical: 6,
        backgroundColor: '#16161f', borderRadius: 20,
        borderWidth: 1, borderColor: '#2a2a3a',
    },
    chipActive: { backgroundColor: '#7c3aed', borderColor: '#7c3aed' },
    icon: { fontSize: 14 },
    label: { color: '#9090aa', fontSize: 12, fontWeight: '600' },
    labelActive: { color: '#fff' },
});
