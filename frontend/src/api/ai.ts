/**
 * AI Recommendations API — types, fetch functions, and React Query hooks.
 */

import { useQuery } from '@tanstack/react-query';
import { API_BASE_URL } from './client';

// =============================================================================
// Types
// =============================================================================

export type ConfidenceLabel = 'low' | 'medium' | 'high';
export type SignalSource = 'model' | 'ai_assisted';
export type RiskProfile = 'conservative' | 'moderate' | 'aggressive';

export interface AIRecommendation {
  player_name: string;
  stat_type: string;
  line: number;
  side: string;
  book: string | null;
  odds: number | null;
  model_projection: number | null;
  edge_pct: number | null;
  confidence_label: ConfidenceLabel;
  reasoning: string | null;
  signal_source: SignalSource;
  suggested_bet_size_pct: number | null;
}

export interface ParlayLegRecommendation {
  player_name: string;
  stat_type: string;
  line: number;
  side: string;
  odds: number | null;
  edge_pct: number | null;
  confidence_label: ConfidenceLabel;
}

export interface ParlayRecommendation {
  legs: ParlayLegRecommendation[];
  combined_odds: number | null;
  combined_ev: number | null;
  confidence_label: ConfidenceLabel;
  reasoning: string | null;
}

export interface AIRecommendationsResponse {
  sport: string;
  league: string;
  date: string;
  individual: AIRecommendation[];
  parlays: ParlayRecommendation[];
  warnings: string[];
  total_recommendations: number;
  ai_model: string | null;
  generated_at: string | null;
}

export interface AIRecommendationsRequest {
  sport_id: number;
  date?: string;
  risk_profile?: RiskProfile;
  min_ev?: number;
  books?: string[];
  markets?: string[];
  max_props?: number;
}

// =============================================================================
// Fetch Functions
// =============================================================================

export async function fetchAIRecommendations(
  request: AIRecommendationsRequest
): Promise<AIRecommendationsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/ai/recommendations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `AI request failed: ${response.status}`);
  }
  return response.json();
}

// =============================================================================
// React Query Hooks
// =============================================================================

export function useAIRecommendations(
  sportId: number | null,
  options: Omit<AIRecommendationsRequest, 'sport_id'> = {}
) {
  return useQuery({
    queryKey: ['ai-recommendations', sportId, options],
    queryFn: () =>
      fetchAIRecommendations({
        sport_id: sportId!,
        ...options,
      }),
    enabled: sportId !== null,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1,
  });
}
