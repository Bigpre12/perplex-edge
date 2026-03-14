'use client';
import { useLucrixStore } from '@/store';

export default function APIHealth() {
    const { backendOnline } = useLucrixStore();

    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div
                style={{
                    width: 8, height: 8, borderRadius: '50%',
                    background: backendOnline ? '#00ff88' : '#ff4466',
                    boxShadow: backendOnline
                        ? '0 0 6px #00ff88'
                        : '0 0 6px #ff4466',
                    animation: 'pulse 2s infinite',
                }}
            />
            <span style={{ fontSize: 12, color: backendOnline ? '#00ff88' : '#ff4466', fontWeight: 600 }}>
                API Health: {backendOnline ? 'Operational' : 'Degraded'}
            </span>
            <style jsx>{`
                @keyframes pulse {
                    0% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.7; transform: scale(1.1); }
                    100% { opacity: 1; transform: scale(1); }
                }
            `}</style>
        </div>
    );
}
