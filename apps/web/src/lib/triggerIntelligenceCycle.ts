import { NextRequest, NextResponse } from "next/server";

const PROD_FALLBACK =
  "https://perplex-edge-backend-copy-production.up.railway.app";

/**
 * Triggers EV, arbitrage, sharp, and props compute on the FastAPI backend (same as /api/compute).
 */
export async function triggerIntelligenceCycle(req: NextRequest): Promise<NextResponse> {
  try {
    const { searchParams } = new URL(req.url);
    const sport = searchParams.get("sport") || "basketball_nba";

    const backendBase =
      process.env.NEXT_PUBLIC_API_URL || PROD_FALLBACK;

    const endpoints = [
      `${backendBase}/api/ev/compute?sport=${sport}`,
      `${backendBase}/api/arbitrage/compute?sport=${sport}`,
      `${backendBase}/api/sharp/compute?sport=${sport}`,
      `${backendBase}/api/props/compute/props?sport=${sport}`,
    ];

    const results = await Promise.allSettled(
      endpoints.map((url) =>
        fetch(url, { method: "POST", headers: { "Content-Type": "application/json" } })
      )
    );

    const summary = {
      ev: results[0].status === "fulfilled" && results[0].value.ok,
      arb: results[1].status === "fulfilled" && results[1].value.ok,
      sharp: results[2].status === "fulfilled" && results[2].value.ok,
      props: results[3].status === "fulfilled" && results[3].value.ok,
      timestamp: new Date().toISOString(),
    };

    return NextResponse.json({
      status: "ok",
      message: "Intelligence computation cycle triggered",
      summary,
    });
  } catch (error) {
    console.error("[INTELLIGENCE SYNC] Critical failure:", error);
    return NextResponse.json(
      { status: "error", message: "Failed to trigger computation cycle" },
      { status: 500 }
    );
  }
}
