import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

/**
 * Unified Intelligence Gateway
 * POST /api/compute?sport=basketball_nba
 * 
 * Triggers all backend scoring, arb detection, and sharp signals in parallel.
 * This is called on-demand when users navigate to intelligence pages.
 */
export async function POST(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const sport = searchParams.get("sport") || "basketball_nba";
    
    const backendBase = process.env.NEXT_PUBLIC_API_URL || "https://perplex-edge-backend-copy-production.up.railway.app";
    
    // Trigger all compute endpoints in parallel for maximum speed
    const endpoints = [
      `${backendBase}/api/ev/compute?sport=${sport}`,
      `${backendBase}/api/arbitrage/compute?sport=${sport}`,
      `${backendBase}/api/sharp/compute?sport=${sport}`,
      `${backendBase}/api/props/compute/props?sport=${sport}`
    ];

    console.log(`[COMPUTE GATEWAY] Triggering intelligence cycle for ${sport}...`);

    const results = await Promise.allSettled(
      endpoints.map(url => fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' } }))
    );

    const summary = {
      ev: results[0].status === 'fulfilled' && results[0].value.ok,
      arb: results[1].status === 'fulfilled' && results[1].value.ok,
      sharp: results[2].status === 'fulfilled' && results[2].value.ok,
      props: results[3].status === 'fulfilled' && results[3].value.ok,
      timestamp: new Date().toISOString()
    };

    return NextResponse.json({
      status: "ok",
      message: "Intelligence computation cycle triggered",
      summary
    });

  } catch (error) {
    console.error("[COMPUTE GATEWAY] Critical Failure:", error);
    return NextResponse.json({ 
        status: "error", 
        message: "Failed to trigger computation cycle" 
    }, { status: 500 });
  }
}
