"use client";

import React, { useState, useEffect } from "react";

const ONBOARDING_STEPS = [
    {
        title: "👋 Welcome to Lucrix Edge",
        body: "The institutional AI engine for sports bettors. You've started your 7-day full access trial.",
        icon: "🚀"
    },
    {
        title: "🔥 The +EV Power Feed",
        body: "This is your primary money-maker. Every prop here is mispriced by the books. Bet the green ones.",
        icon: "💰"
    },
    {
        title: "📊 Verify with Hit Rates",
        body: "Use the traffic-light system to see historical hit rates vs. book implied odds. Institutional trust, verified.",
        icon: "📈"
    }
];

export const OnboardingModal: React.FC = () => {
    const [step, setStep] = useState(0);
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        const hasOnboarded = localStorage.getItem("lucrix_onboarded");
        if (!hasOnboarded) {
            setIsOpen(true);
        }
    }, []);

    const handleNext = () => {
        if (step < ONBOARDING_STEPS.length - 1) {
            setStep(step + 1);
        } else {
            handleClose();
        }
    };

    const handleClose = () => {
        localStorage.setItem("lucrix_onboarded", "true");
        setIsOpen(false);
    };

    if (!isOpen) return null;

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
            background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center',
            justifyContent: 'center', zIndex: 9999, backdropFilter: 'blur(5px)'
        }}>
            <div style={{
                background: '#121212', border: '1px solid #333', padding: '40px',
                borderRadius: '20px', maxWidth: '450px', width: '90%', textAlign: 'center',
                boxShadow: '0 0 30px rgba(0,255,118,0.2)'
            }}>
                <div style={{ fontSize: '3rem', marginBottom: '20px' }}>
                    {ONBOARDING_STEPS[step].icon}
                </div>
                <h2 style={{ color: '#fff', fontSize: '1.8rem', marginBottom: '15px' }}>
                    {ONBOARDING_STEPS[step].title}
                </h2>
                <p style={{ color: '#aaa', lineHeight: '1.6', marginBottom: '30px' }}>
                    {ONBOARDING_STEPS[step].body}
                </p>

                <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginBottom: '30px' }}>
                    {ONBOARDING_STEPS.map((_, i) => (
                        <div key={i} style={{
                            width: '8px', height: '8px', borderRadius: '50%',
                            background: i === step ? '#00ff76' : '#333'
                        }} />
                    ))}
                </div>

                <button
                    onClick={handleNext}
                    style={{
                        width: '100%', padding: '15px', background: '#00ff76',
                        color: '#000', border: 'none', borderRadius: '10px',
                        fontWeight: 'bold', cursor: 'pointer', fontSize: '1rem'
                    }}
                >
                    {step === ONBOARDING_STEPS.length - 1 ? "Start Winning" : "Next Step"}
                </button>
            </div>
        </div>
    );
};
