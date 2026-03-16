"use client";

import { useState, useEffect } from 'react'
import api, { isApiError, unwrap } from '@/lib/api'
import { useBackendStatus } from './useBackendStatus'
import { useLiveData } from './useLiveData'
import { SportKey } from '@/lib/sports.config'

export interface BrainDecision {
    action: string
    reasoning: string
    details: {
        player_name: string
        stat_type: string
        line_value: number
        side: string
        edge: number
        confidence: number
    }
    confidence_tier?: string
}

export interface SystemHealth {
    status: string
    ai_evaluation: {
        action: string
        target: string
        reason: string
        is_critical: boolean
    }
    system_metrics_evaluated: {
        cpu_usage: number
        error_rate: number
    }
}

export interface MarketIntelItem {
    title: string
    content: string
    type: 'news' | 'injury' | 'sharp'
    timestamp: string
}

export const useBrainData = (sportKey: SportKey = "basketball_nba") => {
    const [decisions, setDecisions] = useState<BrainDecision[]>([])
    const [health, setHealth] = useState<SystemHealth | null>(null)
    const [marketIntel, setMarketIntel] = useState<MarketIntelItem[]>([])
    const { isDown } = useBackendStatus()

    // 1. Fetch Decisions
    const { data: decData, loading: decLoading, refresh: decRefetch } = useLiveData(
        () => api.brain.decisions(sportKey),
        ['brain-decisions', sportKey],
        { enabled: !isDown, refreshInterval: 30000 }
    )

    // 2. Fetch Health/Metrics
    const { data: healthData, loading: healthLoading, refresh: healthRefetch } = useLiveData(
        () => api.brain.metrics(),
        ['brain-metrics', sportKey],
        { enabled: !isDown, refreshInterval: 30000 }
    )

    // 3. Fetch Intel
    const { data: intelData, loading: intelLoading, refresh: intelRefetch } = useLiveData(
        () => api.recentIntel(sportKey),
        ['recent-intel', sportKey],
        { enabled: !isDown, refreshInterval: 60000 }
    )

    useEffect(() => {
        if (intelData && !isApiError(intelData)) {
            setMarketIntel(unwrap(intelData))
        }
    }, [intelData])

    useEffect(() => {
        if (healthData && !isApiError(healthData)) {
            setHealth(healthData as SystemHealth)
        }
    }, [healthData])

    const loading = decLoading || healthLoading || intelLoading

    const refetch = () => {
        decRefetch();
        healthRefetch();
        intelRefetch();
    };

    return {
        decisions: unwrap(decData),
        health,
        marketIntel,
        loading,
        refetch
    }
}
