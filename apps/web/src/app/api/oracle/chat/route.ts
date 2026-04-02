import { NextRequest } from "next/server";

export const runtime = "edge";

export async function POST(req: NextRequest) {
  try {
    const { messages, sport } = await req.json();
    const backendBase = process.env.NEXT_PUBLIC_API_URL || "https://perplex-edge-backend-copy-production.up.railway.app";

    // Proxy the stream from the backend
    const response = await fetch(`${backendBase}/api/oracle/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
      },
      body: JSON.stringify({ 
        messages, 
        sport: sport || "basketball_nba",
        stream: true 
      }),
    });

    if (!response.ok || !response.body) {
      return new Response(
        JSON.stringify({ error: "Oracle is temporarily offline. Try again shortly." }), 
        { status: response.status || 502, headers: { "Content-Type": "application/json" } }
      );
    }

    // Return the stream directly to the client
    return new Response(response.body, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Transfer-Encoding": "chunked",
      },
    });

  } catch (error) {
    console.error("[Oracle Stream Proxy] Error:", error);
    return new Response(
      JSON.stringify({ error: "Quantum synchronization failure." }), 
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
