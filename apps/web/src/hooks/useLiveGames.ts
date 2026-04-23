import { useEffect, useState, useRef } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api, WS_BASE } from '@/lib/api';

export interface LiveGame {
  id: string;
  home_team: string;
  away_team: string;
  home_score?: number | null;
  away_score?: number | null;
  score_home?: number | null; // legacy
  score_away?: number | null; // legacy
  matchup?: string;
  period?: string | number;
  clock?: string;
  sport?: string;
  sport_key?: string;
  status?: string;
  commence_time?: string;
  home_logo?: string | null;
  away_logo?: string | null;
  home_team_abbr?: string | null;
  away_team_abbr?: string | null;
}

export const useLiveGames = () => {
  const queryClient = useQueryClient();
  const [socketStatus, setSocketStatus] = useState<'connecting' | 'open' | 'closed'>('connecting');
  const socketRef = useRef<WebSocket | null>(null);

  // Initial Fetch & Polling Fallback (15s)
  const query = useQuery({
    queryKey: ['live-games'],
    queryFn: async () => {
      const { data } = await api.get('/api/live/games');
      return (data.games || []) as LiveGame[];
    },
    refetchInterval: 15000, 
  });

  // WebSocket for Real-time pushing
  useEffect(() => {
    const connect = () => {
      try {
        const socket = new WebSocket(`${WS_BASE}/api/live/ws`);
        socketRef.current = socket;

        socket.onopen = () => {
          console.log('[LiveWS] Connected');
          setSocketStatus('open');
        };

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'game_update' && data.game) {
              // Update the cache immediately
              queryClient.setQueryData(['live-games'], (old: LiveGame[] | undefined) => {
                if (!old) return [data.game];
                return old.map(g => g.id === data.game.id ? data.game : g);
              });
            }
          } catch (e) {
            console.error('[LiveWS] Parse Error', e);
          }
        };

        socket.onclose = () => {
          console.log('[LiveWS] Closed');
          setSocketStatus('closed');
          // Reconnect after 5s
          setTimeout(connect, 5000);
        };

        socket.onerror = (err) => {
          console.error('[LiveWS] Socket Error', err);
          socket.close();
        };
      } catch (e) {
        setSocketStatus('closed');
      }
    };

    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [queryClient]);

  return {
    ...query,
    socketStatus
  };
};
