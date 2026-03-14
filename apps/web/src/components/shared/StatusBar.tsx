'use client';
import { useLucrixStore } from '@/store';

export default function StatusBar() {
    const { backendOnline } = useLucrixStore();

    return (
        <div
            style={{
                height: 3,
                width: '100%',
                background: backendOnline ? '#00ff88' : '#ff4466',
                transition: 'background 0.5s ease',
            }}
            title={backendOnline ? 'API Operational' : 'API Degraded'}
        />
    );
}
