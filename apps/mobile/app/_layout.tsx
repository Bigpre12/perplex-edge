import { useEffect } from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import FlashMessage from 'react-native-flash-message';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useHealthMonitor } from '@/hooks/useHealthMonitor';
import { setupNotifications } from '@/lib/notifications';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 2,
            staleTime: 30_000,
            refetchInterval: 30_000,
        },
    },
});

function AppShell() {
    useHealthMonitor();

    useEffect(() => {
        setupNotifications();
    }, []);

    return (
        <Stack screenOptions={{ headerShown: false }}>
            <Stack.Screen name="(tabs)" />
            <Stack.Screen
                name="player/[id]"
                options={{ presentation: 'modal', animation: 'slide_from_bottom' }}
            />
        </Stack>
    );
}

export default function RootLayout() {
    return (
        <GestureHandlerRootView style={{ flex: 1 }}>
            <QueryClientProvider client={queryClient}>
                <StatusBar style="light" backgroundColor="#0a0a0f" />
                <AppShell />
                <FlashMessage position="top" />
            </QueryClientProvider>
        </GestureHandlerRootView>
    );
}
