// apps/web/src/lib/kelly.ts
export function calcKelly(
    odds: number,
    trueProbPct: number,
    bankroll: number,
    fraction = 0.25
): { dollars: number; units: number; kelloPct: number } {
    const p = trueProbPct / 100;
    const q = 1 - p;
    const b = odds > 0 ? odds / 100 : 100 / Math.abs(odds);
    if (b <= 0) return { dollars: 0, units: 0, kelloPct: 0 };
    const kelly = (b * p - q) / b;
    const kelloPct = Math.max(kelly * fraction * 100, 0);
    const dollars = parseFloat(((kelloPct / 100) * bankroll).toFixed(2));
    const units = parseFloat((kelloPct / 100).toFixed(3));
    return { dollars, units, kelloPct: parseFloat(kelloPct.toFixed(2)) };
}
