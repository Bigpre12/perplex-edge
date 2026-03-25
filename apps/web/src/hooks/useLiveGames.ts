import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface LiveGame {
  id: string;
  home_team: string;
  away_team: string;
  score_home?: number;
  score_away?: number;
  period?: string;
  clock?: string;
  sport: string;
}

export const useLiveGames = () => {
  return useQuery({
    queryKey: ['live-games'],
    queryFn: async () => {
      const { data } = await api.get('/api/live/games');
      return (data.games || []) as LiveGame[];
    },
    refetchInterval: 15000, // 15s
  });
};
