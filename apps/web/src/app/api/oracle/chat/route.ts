import { NextRequest } from "next/server";

export const runtime = "edge";

export async function POST(req: NextRequest) {
  try {
    const { messages, sport } = await req.json();
    const backendBase = process.env.NEXT_PUBLIC_API_URL || "https://perplex-edge-backend-copy-production.up.railway.app";

    const authHeader = req.headers.get("authorization");

    const backendRes = await fetch(`${backendBase}/api/oracle/chat`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        ...(authHeader ? { "Authorization": authHeader } : {})
      },
      body: JSON.stringify({ 
        messages, 
        sport: sport || "basketball_nba",
        stream: true 
      }),
    });

    // If backend supports native streaming, pipe it through
    if (backendRes.headers.get("content-type")?.includes("text/event-stream")) {
      return new Response(backendRes.body, {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
        },
      });
    }

    // Fallback: If backend returns JSON, simulate streaming word by word
    const data = await backendRes.json();
    const text = data.recommendation || data.analysis || data.response || data.message || "Oracle analysis complete.";
    const words = text.split(" ");
    
    const stream = new ReadableStream({
      async start(controller) {
        for (const word of words) {
          controller.enqueue(new TextEncoder().encode(`data: ${word} \n\n`));
          await new Promise((r) => setTimeout(r, 40)); // 40ms per word for natural feel
        }
        controller.enqueue(new TextEncoder().encode("data: [DONE]\n\n"));
        controller.close();
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
      },
    });

  } catch (error) {
    console.error("[Oracle SSE Proxy] Critical Failure:", error);
    return new Response(
      JSON.stringify({ error: "Quantum synchronization failure." }), 
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
