"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { clsx } from 'clsx';

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
    await api.post('/api/user/preferences', { sports, bankroll, books });
    localStorage.setItem('lola-onboarded', 'true');
    router.push('/desk');
  };

  const btnClass = (active: boolean) => clsx(
    "px-4 py-2 rounded-lg cursor-pointer font-semibold transition-all",
    active 
      ? "border-2 border-brand-primary bg-brand-primary/20 text-white" 
      : "border border-white/10 bg-white/5 text-slate-400 hover:text-white hover:bg-white/10"
  );

  return (
    <div className="max-w-[480px] mx-auto my-20 p-8 bg-[#0c0c0c] border border-white/10 rounded-3xl text-white shadow-2xl">
      <div className="mb-6">
        <div className="flex gap-2 mb-4">
          {[1, 2, 3].map(i => (
            <div 
              key={i} 
              className={clsx(
                "h-1 flex-1 rounded-full transition-all",
                i <= step ? "bg-brand-primary shadow-[0_0_8px_rgba(34,211,238,0.5)]" : "bg-white/5"
              )} 
            />
          ))}
        </div>
        <h1 className="text-2xl font-black italic uppercase tracking-tight">Welcome to Lucrix ✦</h1>
        <p className="text-slate-500 text-sm font-medium mt-1">Quick setup — takes 30 seconds</p>
      </div>

      {step === 1 && (
        <div className="space-y-6">
          <div>
            <h2 className="text-sm font-black uppercase tracking-widest text-slate-400 mb-4">Which sports do you bet?</h2>
            <div className="flex flex-wrap gap-2">
              {SPORTS.map(s => (
                <button 
                  key={s} 
                  onClick={() => toggleSport(s)} 
                  className={btnClass(sports.includes(s))}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
          <button 
            onClick={() => setStep(2)} 
            className="w-full py-4 bg-brand-primary text-background-dark rounded-xl font-black uppercase tracking-widest hover:scale-[1.02] active:scale-95 transition-all shadow-lg shadow-brand-primary/20"
          >
            Next Step →
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-6">
          <div>
            <h2 className="text-sm font-black uppercase tracking-widest text-slate-400 mb-4">What's your bankroll?</h2>
            <label htmlFor="bankroll-input" className="sr-only">Bankroll Amount</label>
            <div className="relative group">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-brand-primary font-bold text-xl">$</span>
              <input 
                id="bankroll-input"
                type='number' 
                value={bankroll} 
                onChange={e => setBankroll(Number(e.target.value))}
                placeholder="500"
                title="Enter your total bankroll"
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-10 pr-6 text-2xl font-black text-white focus:outline-none focus:border-brand-primary/50 transition-all"
              />
            </div>
            <p className="text-slate-500 text-xs mt-3 leading-relaxed">
              Used for <span className="text-brand-primary font-bold">Kelly Criterion</span> stake sizing. You can change this anytime in settings.
            </p>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => setStep(1)} 
              className="flex-1 py-4 bg-white/5 border border-white/10 text-white rounded-xl font-black uppercase tracking-widest hover:bg-white/10 transition-all"
            >
              Back
            </button>
            <button 
              onClick={() => setStep(3)} 
              className="flex-[2] py-4 bg-brand-primary text-background-dark rounded-xl font-black uppercase tracking-widest hover:scale-[1.02] active:scale-95 transition-all shadow-lg shadow-brand-primary/20"
            >
              Next Step →
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-6">
          <div>
            <h2 className="text-sm font-black uppercase tracking-widest text-slate-400 mb-4">Where do you bet?</h2>
            <div className="flex flex-wrap gap-2">
              {BOOKS.map(b => (
                <button 
                  key={b} 
                  onClick={() => toggleBook(b)} 
                  className={btnClass(books.includes(b))}
                >
                  {b}
                </button>
              ))}
            </div>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => setStep(2)} 
              className="flex-1 py-4 bg-white/5 border border-white/10 text-white rounded-xl font-black uppercase tracking-widest hover:bg-white/10 transition-all"
            >
              Back
            </button>
            <button 
              onClick={finish} 
              className="flex-[2] py-4 bg-emerald-500 text-background-dark rounded-xl font-black uppercase tracking-widest hover:scale-[1.02] active:scale-95 transition-all shadow-lg shadow-emerald-500/20"
            >
              🚀 Launch Neural Engine
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
