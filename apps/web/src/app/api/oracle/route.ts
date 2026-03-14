import { NextRequest, NextResponse } from "next/server";
import OpenAI from "openai";

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

export async function POST(req: NextRequest) {
    try {
        // ✅ Log key presence
        console.log("OPENAI KEY present:", !!process.env.OPENAI_API_KEY);

        const { messages, propsContext } = await req.json();
        console.log("Messages received:", messages?.length);

        const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

        // Build context from live props if available
        const contextMessage = propsContext
            ? `\n\nLIVE PROPS DATA:\n${JSON.stringify(propsContext, null, 2)}`
            : "";

        const response = await openai.chat.completions.create({
            model: "gpt-4o-mini",
            messages: [
                {
                    role: "system",
                    content: ORACLE_SYSTEM + contextMessage,
                },
                ...messages,
            ],
            max_tokens: 600,
            temperature: 0.7,
        });

        return NextResponse.json({
            message: response.choices[0].message.content,
            usage: response.usage,
        });
    } catch (err: any) {
        // ✅ Log actual error
        console.error("Oracle REAL error:", err.message, err.status);
        return NextResponse.json(
            {
                message: "Oracle is temporarily offline. Try again shortly.",
                error: err.message
            },
            { status: 200 }
        );
    }
}
