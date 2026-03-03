"use client";

import React from 'react';

const testimonials = [
    { name: "SharpBettor88", text: "Lucrix's EV feed is the closest thing to professional steam tracking I've found. Up 40 units this month.", avatar: "🟢" },
    { name: "PropHunter", text: "The Hit Rate vs Odds tool saved me from dozens of 'trap' lines. Institutional grade stuff.", avatar: "⚡" },
    { name: "AlphaVegas", text: "Finally a platform that uses Sharp Book alignment correctly. Pinnacle parity is a game changer.", avatar: "💎" }
];

export const TrustSignals: React.FC = () => {
    return (
        <section style={{ padding: '60px 20px', background: '#0a0a0a', textAlign: 'center' }}>
            <div style={{ marginBottom: '40px' }}>
                <h2 style={{ fontSize: '2.5rem', color: '#fff', marginBottom: '10px' }}>
                    Trusted by <span style={{ color: '#00ff00' }}>5,000+</span> Sharp Bettors
                </h2>
                <p style={{ color: '#aaa' }}>Join the community of logic-driven gamblers dominating the books.</p>
            </div>

            <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', justifyContent: 'center' }}>
                {testimonials.map((t, i) => (
                    <div key={i} style={{
                        background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)',
                        padding: '25px', borderRadius: '15px', maxWidth: '300px', textAlign: 'left'
                    }}>
                        <div style={{ fontSize: '1.5rem', marginBottom: '15px' }}>{t.avatar}</div>
                        <p style={{ color: '#ddd', fontStyle: 'italic', marginBottom: '15px' }}>"{t.text}"</p>
                        <div style={{ color: '#00ff00', fontWeight: 'bold' }}>@{t.name}</div>
                    </div>
                ))}
            </div>

            <div style={{ marginTop: '50px', display: 'flex', justifyContent: 'center', gap: '40px' }}>
                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', color: '#fff', fontWeight: 'bold' }}>58.4%</div>
                    <div style={{ color: '#666', fontSize: '0.8rem' }}>MODEL HIT RATE</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', color: '#fff', fontWeight: 'bold' }}>+14.2%</div>
                    <div style={{ color: '#666', fontSize: '0.8rem' }}>AVERAGE ROI</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', color: '#fff', fontWeight: 'bold' }}>60k+</div>
                    <div style={{ color: '#666', fontSize: '0.8rem' }}>PROPS ANALYZED</div>
                </div>
            </div>
        </section>
    );
};
