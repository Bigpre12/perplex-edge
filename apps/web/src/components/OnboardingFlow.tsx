'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, API } from '@/lib/api';

const SPORTS = ['NBA', 'NFL', 'MLB', 'NHL', 'NCAAF', 'WNBA'];
const BOOKS = ['PrizePicks', 'DraftKings', 'FanDuel', 'BetMGM', 'Caesars', 'Fliff'];

export default function OnboardingFlow() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [sports, setSports] = useState<string[]>(['NBA']);
  const [bankroll, setBankroll] = useState(500);
  const [books, setBooks] = useState<string[]>(['PrizePicks']);

  const toggleSport = (s: string) => setSports(p => p.includes(s) ? p.filter(x => x !== s) : [...p, s]);
  const toggleBook = (b: string) => setBooks(p => p.includes(b) ? p.filter(x => x !== b) : [...p, b]);

  const finish = async () => {
    await api.post('/user/preferences', { sports, bankroll, books });
    localStorage.setItem('lola-onboarded', 'true');
    router.push('/dashboard');
  };

  const btnStyle = (active: boolean) => ({
    padding: '8px 16px', borderRadius: 8, cursor: 'pointer', fontWeight: 600,
    border: active ? '2px solid #3b82f6' : '1px solid #333',
    background: active ? '#1d4ed8' : '#1a1a1a', color: '#fff'
  });

  return (
    <div style={{ maxWidth: 480, margin: '80px auto', padding: 32, background: '#111', borderRadius: 16, color: '#fff' }}>
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
          {[1, 2, 3].map(i => <div key={i} style={{ height: 4, flex: 1, borderRadius: 4, background: i <= step ? '#3b82f6' : '#333' }} />)}
        </div>
        <h1 style={{ fontSize: 24, fontWeight: 700 }}>Welcome to LOLA ✦</h1>
        <p style={{ color: '#888' }}>Quick setup — takes 30 seconds</p>
      </div>

      {step === 1 && (
        <div>
          <h2 style={{ marginBottom: 12 }}>Which sports do you bet?</h2>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {SPORTS.map(s => <button key={s} onClick={() => toggleSport(s)} style={btnStyle(sports.includes(s))}>{s}</button>)}
          </div>
          <button onClick={() => setStep(2)} style={{ marginTop: 24, width: '100%', padding: '12px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 700 }}>Next →</button>
        </div>
      )}

      {step === 2 && (
        <div>
          <h2 style={{ marginBottom: 12 }}>What's your bankroll?</h2>
          <input type='number' value={bankroll} onChange={e => setBankroll(Number(e.target.value))}
            style={{ width: '100%', padding: 12, background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, color: '#fff', fontSize: 18 }} />
          <p style={{ color: '#888', marginTop: 8, fontSize: 13 }}>Used for Kelly Criterion stake sizing. You can change this anytime.</p>
          <div style={{ display: 'flex', gap: 8, marginTop: 24 }}>
            <button onClick={() => setStep(1)} style={{ flex: 1, padding: 12, background: '#1a1a1a', color: '#fff', border: '1px solid #333', borderRadius: 8, cursor: 'pointer' }}>← Back</button>
            <button onClick={() => setStep(3)} style={{ flex: 2, padding: 12, background: '#3b82f6', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 700 }}>Next →</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div>
          <h2 style={{ marginBottom: 12 }}>Where do you bet?</h2>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {BOOKS.map(b => <button key={b} onClick={() => toggleBook(b)} style={btnStyle(books.includes(b))}>{b}</button>)}
          </div>
          <div style={{ display: 'flex', gap: 8, marginTop: 24 }}>
            <button onClick={() => setStep(2)} style={{ flex: 1, padding: 12, background: '#1a1a1a', color: '#fff', border: '1px solid #333', borderRadius: 8, cursor: 'pointer' }}>← Back</button>
            <button onClick={finish} style={{ flex: 2, padding: 12, background: '#16a34a', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 700 }}>🚀 Launch LOLA</button>
          </div>
        </div>
      )}
    </div>
  );
}
// Usage: In middleware.ts, check if localStorage lola-onboarded is set.
// If not, redirect new users to /onboarding route.
// Add page: app/onboarding/page.tsx -> <OnboardingFlow />
