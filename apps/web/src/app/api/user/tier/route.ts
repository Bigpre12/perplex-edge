import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
    try {
        const backendUrl = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
        const res = await fetch(`${backendUrl}/api/user/tier`, {
            headers: {
                "Content-Type": "application/json",
                // forward auth header if present
                ...(req.headers.get("authorization") && {
                    Authorization: req.headers.get("authorization")!,
                }),
            },
        });
        if (!res.ok) throw new Error(`FastAPI error: ${res.status}`);
        const data = await res.json();
        return NextResponse.json(data);
    } catch (err) {
        console.error("[Proxy User Tier] Error:", err);
        // Return safe fallback — never let this 500
        return NextResponse.json({ tier: "free" }, { status: 200 });
    }
}
