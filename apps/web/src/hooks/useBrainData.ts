"use client";

import { useState, useEffect } from 'react'
import { API, apiFetch, isApiError, api } from '@/lib/api'
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
    const { data: decData, loading: decLoading } = useLiveData(
        () => api.brain.decisions(sportKey, 5),
        ['brain-decisions', sportKey],
        { enabled: !isDown, refreshInterval: 30000 }
    )

    // 2. Fetch Health/Metrics
    const { data: healthData, loading: healthLoading } = useLiveData(
        () => api.brain.metrics(sportKey),
        ['brain-metrics', sportKey],
        { enabled: !isDown, refreshInterval: 30000 }
    )

    // 3. Fetch Intel
    const { data: intelData, loading: intelLoading } = useLiveData(
        () => api.recentIntel(sportKey),
        ['recent-intel', sportKey],
        { enabled: !isDown, refreshInterval: 60000 }
    )

    useEffect(() => {
        if (intelData && !isApiError(intelData)) {
            const data = intelData as { items?: MarketIntelItem[] }
            setMarketIntel(data.items || [])
        }
    }, [intelData])

    const loading = decLoading || healthLoading || intelLoading

    return {
        decisions: decData?.decisions || [],
        health: healthData,
        marketIntel,
        loading,
        refetch: () => { }
    }
}
