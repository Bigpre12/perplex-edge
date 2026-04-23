import { NextRequest } from "next/server";
import { triggerIntelligenceCycle } from "@/lib/triggerIntelligenceCycle";

export const runtime = "nodejs";

/** POST /api/sync/odds?sport=basketball_nba — alias for the compute gateway (manual odds / pipeline refresh). */
export async function POST(req: NextRequest) {
  return triggerIntelligenceCycle(req);
}
