import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

Notifications.setNotificationHandler({
    handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
        shouldShowBanner: true,
        shouldShowList: true,
    }),
});

export async function setupNotifications(): Promise<string | null> {
    if (!Device.isDevice) return null;

    const { status: existing } = await Notifications.getPermissionsAsync();
    let finalStatus = existing;

    if (existing !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
    }

    if (finalStatus !== 'granted') return null;

    if (Platform.OS === 'android') {
        await Notifications.setNotificationChannelAsync('lucrix-alerts', {
            name: 'Lucrix Alerts',
            importance: Notifications.AndroidImportance.MAX,
            vibrationPattern: [0, 250, 250, 250],
            lightColor: '#7c3aed',
            sound: 'default',
        });
    }

    const token = (await Notifications.getExpoPushTokenAsync()).data;
    return token;
}

export async function sendLocalAlert(title: string, body: string) {
    await Notifications.scheduleNotificationAsync({
        content: { title, body, sound: 'default', data: { type: 'alert' } },
        trigger: null,
    });
}
