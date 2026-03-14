import { Tabs } from 'expo-router';
import { View, Text, StyleSheet } from 'react-native';
import { useLucrixStore } from '@/store/useLucrixStore';
import { Home, TrendingUp, Brain, ListChecks, Bell } from 'lucide-react-native';

export default function TabLayout() {
    const { unreadAlerts } = useLucrixStore();

    return (
        <Tabs
            screenOptions={{
                headerShown: false,
                tabBarStyle: styles.tabBar,
                tabBarActiveTintColor: '#7c3aed',
                tabBarInactiveTintColor: '#5a5a7a',
                tabBarLabelStyle: styles.tabLabel,
            }}
        >
            <Tabs.Screen
                name="index"
                options={{
                    title: 'Dashboard',
                    tabBarIcon: ({ color }) => <Home size={22} color={color} />,
                }}
            />
            <Tabs.Screen
                name="props"
                options={{
                    title: 'Props',
                    tabBarIcon: ({ color }) => <TrendingUp size={22} color={color} />,
                }}
            />
            <Tabs.Screen
                name="brain"
                options={{
                    title: 'Brain',
                    tabBarIcon: ({ color }) => <Brain size={22} color={color} />,
                }}
            />
            <Tabs.Screen
                name="parlays"
                options={{
                    title: 'Parlays',
                    tabBarIcon: ({ color }) => <ListChecks size={22} color={color} />,
                }}
            />
            <Tabs.Screen
                name="alerts"
                options={{
                    title: 'Alerts',
                    tabBarIcon: ({ color }) => (
                        <View>
                            <Bell size={22} color={color} />
                            {unreadAlerts > 0 && (
                                <View style={styles.badge}>
                                    <Text style={styles.badgeText}>{unreadAlerts}</Text>
                                </View>
                            )}
                        </View>
                    ),
                }}
            />
        </Tabs>
    );
}

const styles = StyleSheet.create({
    tabBar: {
        backgroundColor: '#111118',
        borderTopColor: '#2a2a3a',
        borderTopWidth: 1,
        height: 80,
        paddingBottom: 16,
    },
    tabLabel: { fontSize: 11, fontWeight: '600' },
    badge: {
        position: 'absolute', top: -4, right: -8,
        backgroundColor: '#ff4466',
        borderRadius: 8, minWidth: 16, height: 16,
        alignItems: 'center', justifyContent: 'center',
    },
    badgeText: { color: '#fff', fontSize: 9, fontWeight: '800' },
});
