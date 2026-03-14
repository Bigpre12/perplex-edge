'use client';
import { useState } from 'react';
import { api, isApiError } from '@/lib/api';

interface Prop { id: string; player_name: string; stat_category: string; line: number; }

export default function AutoCopySlip({ props }: { props: Prop[] }) {
  const [copied, setCopied] = useState(false);
  const [platform, setPlatform] = useState<'prizepicks' | 'fliff'>('prizepicks');

  const handleCopy = async () => {
    const ids = props.map(p => p.id);
    const endpoint = platform === 'prizepicks' ? 'prizepicks-slip' : 'fliff-slip';
    const data = await api.autocopy(endpoint, ids);

    if (!isApiError(data) && data.slip_text) {
      await navigator.clipboard.writeText(data.slip_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
      <select value={platform} onChange={e => setPlatform(e.target.value as any)}
        style={{ background: '#1a1a1a', color: '#fff', border: '1px solid #333', borderRadius: 6, padding: '6px 10px' }}>
        <option value='prizepicks'>PrizePicks</option>
        <option value='fliff'>Fliff</option>
      </select>
      <button onClick={handleCopy}
        style={{
          background: copied ? '#16a34a' : '#3b82f6', color: '#fff', border: 'none',
          borderRadius: 6, padding: '8px 16px', cursor: 'pointer', fontWeight: 600
        }}>
        {copied ? '✓ Copied!' : `Copy ${platform === 'prizepicks' ? 'PrizePicks' : 'Fliff'} Slip`}
      </button>
    </div>
  );
}
