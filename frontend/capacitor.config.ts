import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
    appId: 'com.perplexedge.app',
    appName: 'Perplex Edge',
    webDir: 'out',
    bundledWebRuntime: false,
    server: {
        // In production, this should be removed to serve the bundled 'out' directory.
        // During local development, we point the native webview to the Next.js dev server:
        url: 'http://10.0.2.2:3000',
        cleartext: true
    },
    ios: {
        contentInset: 'always'
    },
    plugins: {
        PushNotifications: {
            presentationOptions: ["badge", "sound", "alert"]
        }
    }
};

export default config;
