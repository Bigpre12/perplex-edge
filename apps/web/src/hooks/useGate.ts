import { useLucrixStore } from "@/store";
import { getTierConfig } from "@/lib/tiers";

export function useGate() {
    const tier = useLucrixStore((state: any) => state.userTier);
    const isDev = typeof window !== 'undefined' && 
      (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

    const config = getTierConfig(isDev ? "elite" : tier);

    return {
        canAccess: (feature: keyof typeof config) => !!config[feature],
        propsLimit: config.props,
        sportsAllowed: config.sports,
        oracleLimit: config.oracle,
        config,
        tier: isDev ? "elite" : (tier?.toLowerCase() || "free"),
    };
}
