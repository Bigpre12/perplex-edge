import { SportKey } from '@/lib/sports.config';

export interface Prop {
    id: string;
    player: string;
    team: string;
    stat: string;
    line: number;
    hitRate: number;
    grade: 'S' | 'A' | 'B' | 'C';
    sharp: boolean;
    books: Record<string, { over: number; under: number }>;
    trend: 'up' | 'down' | 'flat';
}

export interface Decision {
    id: string;
    pick: string;
    confidence: number;
    edge: number;
    reasoning: string;
    timestamp: string;
    result?: 'win' | 'loss' | 'pending';
}

export interface Metrics {
    winRate: number;
    roi: number;
    totalPicks: number;
    streak: number;
    avgEdge: number;
}

export interface Alert {
    id: string;
    type: string;
    message: string;
    timestamp: string;
}

export interface ParlayLeg extends Prop {
    label: string;
}
