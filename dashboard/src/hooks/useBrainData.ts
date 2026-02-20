import { useState, useEffect } from 'react'

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

export const useBrainData = () => {
    const [decisions, setDecisions] = useState<BrainDecision[]>([])
    const [health, setHealth] = useState<SystemHealth | null>(null)
    const [loading, setLoading] = useState(true)

    const fetchData = async () => {
        try {
            const backendUrl = "http://localhost:8001"

            // Fetch decisions
            const decRes = await fetch(`${backendUrl}/immediate/brain-decisions?limit=5`)
            const decData = await decRes.json()
            setDecisions(decData.decisions || [])

            // Fetch health cycle
            const healthRes = await fetch(`${backendUrl}/immediate/brain-healing/run-cycle`, { method: 'POST' })
            const healthData = await healthRes.json()
            setHealth(healthData)

        } catch (err) {
            console.error("Failed to fetch brain data:", err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchData()
        const interval = setInterval(fetchData, 10000) // Poll every 10s
        return () => clearInterval(interval)
    }, [])

    return { decisions, health, loading, refetch: fetchData }
}
