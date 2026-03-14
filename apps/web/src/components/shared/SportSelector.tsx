'use client';
import { SPORTS_CONFIG, SportKey, ACTIVE_SPORTS } from '@/lib/sports.config';
import { useLucrixStore } from '@/store';

export default function SportSelector() {
    const { activeSport, setActiveSport } = useLucrixStore();

    return (
        <div style={{
            display: 'flex', gap: '4px', overflowX: 'auto',
            padding: '4px', borderRadius: '8px',
            scrollbarWidth: 'none',
        }}>
            {ACTIVE_SPORTS.map(key => {
                const sport = SPORTS_CONFIG[key];
                const isActive = key === activeSport;
                return (
                    <button
                        key={key}
                        onClick={() => setActiveSport(key)}
                        style={{
                            display: 'flex', alignItems: 'center', gap: '6px',
                            padding: '6px 14px', borderRadius: '6px',
                            border: `1px solid ${isActive ? '#7c3aed' : '#2a2a3a'}`,
                            background: isActive ? '#7c3aed' : 'transparent',
                            color: isActive ? 'white' : '#9090aa',
                            cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600,
                            whiteSpace: 'nowrap', transition: 'all 0.15s ease',
                        }}
                    >
                        <span>{sport.icon}</span>
                        <span>{sport.label}</span>
                    </button>
                );
            })}
        </div>
    );
}
