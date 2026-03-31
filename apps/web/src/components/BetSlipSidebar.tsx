"use client";

import React, { useState } from 'react';

interface Leg {
    id: string;
    player: string;
    stat: string;
    line: number;
    odds: number;
}

export const BetSlipSidebar: React.FC = () => {
    const [legs, setLegs] = useState<Leg[]>([]);

    const calculateParlayOdds = (legs: Leg[]) => {
        // Standardized parlay multiplier logic
        let multiplier = 1;
        legs.forEach(leg => {
            const dec = leg.odds > 0 ? (leg.odds / 100) + 1 : (100 / Math.abs(leg.odds)) + 1;
            multiplier *= dec;
        });
        return Math.round((multiplier - 1) * 100);
    };

    const removeLeg = (id: string) => {
        setLegs(legs.filter(l => l.id !== id));
    };

    return (
        <div className="bet-slip-sidebar" style={{
            position: 'fixed', right: 0, top: 0, width: '320px', height: '100vh',
            background: '#121212', borderLeft: '1px solid #333', padding: '20px',
            color: '#fff', display: 'flex', flexDirection: 'column'
        }}>
            <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>Bet Slip</h3>

            <div style={{ flex: 1, overflowY: 'auto', margin: '15px 0' }}>
                {legs.length === 0 ? (
                    <p style={{ color: '#666', textAlign: 'center' }}>Your slip is empty.</p>
                ) : (
                    legs.map(leg => (
                        <div key={leg.id} style={{
                            background: '#1a1a1a', padding: '12px', borderRadius: '8px',
                            marginBottom: '10px', position: 'relative'
                        }}>
                            <button onClick={() => removeLeg(leg.id)} style={{
                                position: 'absolute', right: '5px', top: '5px', background: 'none',
                                border: 'none', color: '#ff4444', cursor: 'pointer'
                            }}>×</button>
                            <div style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>{leg.player}</div>
                            <div style={{ fontSize: '0.8rem', color: '#aaa' }}>{leg.stat} {leg.line}</div>
                            <div style={{ color: '#00ff00', fontSize: '0.9rem' }}>{leg.odds > 0 ? '+' : ''}{leg.odds}</div>
                        </div>
                    ))
                )}
            </div>

            {legs.length > 0 && (
                <div style={{ borderTop: '1px solid #333', paddingTop: '15px' }}>
                    <div style={{ display: 'flex', justifyItems: 'space-between', marginBottom: '10px' }}>
                        <span>Parlay Odds:</span>
                        <span style={{ marginLeft: 'auto', color: '#00ff00', fontWeight: 'bold' }}>
                            +{calculateParlayOdds(legs)}
                        </span>
                    </div>
                    <button style={{
                        width: '100%', padding: '15px', background: '#00ff00', color: '#000',
                        border: 'none', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer'
                    }}>
                        Place Bet on DraftKings
                    </button>
                    <p style={{ fontSize: '0.7rem', color: '#666', marginTop: '10px', textAlign: 'center' }}>
                        * Affiliate link triggers on click
                    </p>
                </div>
            )}
        </div>
    );
};
