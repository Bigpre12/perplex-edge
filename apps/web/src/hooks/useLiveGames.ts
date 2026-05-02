import { useEffect, useState, useRef } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api, WS_BASE } from '@/lib/api';
import { supabase } from '@/lib/supabase';
import { TOKEN_STORAGE_KEY } from '@/lib/authStorage';
import { useAuth } from './useAuth';

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
  const { token: authStateToken } = useAuth();
  const [socketStatus, setSocketStatus] = useState<'connecting' | 'open' | 'closed'>('connecting');
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Initial fetch + polling fallback (30s) against /api/live/scores
  const query = useQuery({
    queryKey: ['live-games'],
    queryFn: async () => {
      const { data } = await api.get('/api/live/scores?sport=basketball_nba');
      const rows = Array.isArray(data?.games)
        ? data.games
        : Array.isArray(data?.data)
          ? data.data
          : Array.isArray(data)
            ? data
            : [];
      return rows as LiveGame[];
    },
    refetchInterval: 30000,
  });

  // WebSocket for Real-time pushing
  useEffect(() => {
    const connect = async () => {
      try {
        // Try getting token from auth state first, fallback to storage
        const token = authStateToken || (typeof window !== 'undefined' ? localStorage.getItem(TOKEN_STORAGE_KEY) : null);
        
        if (!token) {
          console.log('[LiveWS] No token available yet. Waiting...');
          setSocketStatus('closed');
          return;
        }
        const socket = new WebSocket(
          `${WS_BASE}/api/live/ws?token=${encodeURIComponent(token)}&sport=basketball_nba`
        );
        socketRef.current = socket;

        socket.onopen = () => {
          console.log('[LiveWS] Connected');
          setSocketStatus('open');
          reconnectAttemptsRef.current = 0;
        };

        socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'game_update' && Array.isArray(data.games)) {
              queryClient.setQueryData(['live-games'], data.games as LiveGame[]);
            }
          } catch (e) {
            console.error('[LiveWS] Parse Error', e);
          }
        };

        socket.onclose = () => {
          console.log('[LiveWS] Closed');
          setSocketStatus('closed');
          const reconnectDelay = Math.min(1000 * 2 ** reconnectAttemptsRef.current, 30000);
          reconnectAttemptsRef.current += 1;
          reconnectTimerRef.current = setTimeout(connect, reconnectDelay);
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
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [queryClient, authStateToken]);

  return {
    ...query,
    socketStatus,
    lastUpdatedAt: query.dataUpdatedAt ? new Date(query.dataUpdatedAt).toISOString() : null,
  };
};
