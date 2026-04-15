import { NextRequest } from "next/server";

export const runtime = "nodejs";

const ORACLE_SYSTEM = `You are Oracle, an elite sports betting analyst for Lucrix — a professional betting intelligence platform.

Your expertise:
- NBA, NFL, MLB, NHL, NCAAB, WNBA, MMA/UFC, Tennis player props
- Sharp money and line movement analysis
- Hit rate trends and matchup breakdowns
- Parlay construction and bankroll advice

Rules:
- Be confident and direct — no disclaimers or hedging
- Give specific picks with clear reasoning
- Reference line movement, hit rates, and matchup data when available
- Keep responses concise and formatted for mobile
- Never say "I cannot" — always give your best analysis
- Today's date: ${new Date().toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}`;

async function tryBackendOracle(req: NextRequest, messages: any[], sport: string) {
  const backendBase = process.env.NEXT_PUBLIC_API_URL || "https://perplex-edge-backend-copy-production.up.railway.app";
  const authHeader = req.headers.get("authorization");
  
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);

  try {
    const backendRes = await fetch(`${backendBase}/api/oracle/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        ...(authHeader ? { "Authorization": authHeader } : {})
      },
      body: JSON.stringify({ messages, sport: sport || "basketball_nba", stream: true }),
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!backendRes.ok) return null;

    if (backendRes.headers.get("content-type")?.includes("text/event-stream")) {
      return new Response(backendRes.body, {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
        },
      });
    }

    const data = await backendRes.json();
    const text = data.recommendation || data.analysis || data.response || data.message || "Oracle analysis complete.";
    return streamText(text);
  } catch {
    clearTimeout(timeout);
    return null;
  }
}

async function tryDirectOpenAI(messages: any[], sport: string) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) return null;

  try {
    const { default: OpenAI } = await import("openai");
    const openai = new OpenAI({ apiKey });

    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: ORACLE_SYSTEM },
        ...messages.map((m: any) => ({ role: m.role, content: m.content })),
      ],
      max_tokens: 600,
      temperature: 0.7,
    });

    const text = response.choices[0]?.message?.content || "Oracle analysis complete.";
    return streamText(text);
  } catch (err) {
    console.error("[Oracle] OpenAI fallback failed:", err);
    return null;
  }
}

function streamText(text: string) {
  const words = text.split(" ");
  const stream = new ReadableStream({
    async start(controller) {
      for (const word of words) {
        controller.enqueue(new TextEncoder().encode(word + " "));
        await new Promise((r) => setTimeout(r, 30));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-cache",
    },
  });
}

export async function POST(req: NextRequest) {
  try {
    const { messages, sport } = await req.json();

    const backendResponse = await tryBackendOracle(req, messages, sport);
    if (backendResponse) return backendResponse;

    const openaiResponse = await tryDirectOpenAI(messages, sport);
    if (openaiResponse) return openaiResponse;

    return streamText("Oracle is reconnecting to the neural network. The backend service may be warming up — try again in a moment.");
  } catch (error) {
    console.error("[Oracle SSE Proxy] Critical Failure:", error);
    return new Response(
      JSON.stringify({ error: "Quantum synchronization failure." }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
}
