import { useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface OracleRequest {
  player: string;
  market: string;
  context: string;
}

export const useOracle = () => {
  return useMutation({
    mutationFn: async (req: OracleRequest) => {
      const { data } = await api.post('/api/oracle', req);
      return data;
    },
  });
};
