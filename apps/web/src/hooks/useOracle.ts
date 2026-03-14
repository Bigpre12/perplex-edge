import { useState, useCallback } from "react";
import { api, isApiError } from "@/lib/api";

interface Message {
    role: "user" | "assistant";
    content: string;
}

export function useOracle() {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: "assistant",
            content: "Oracle online. Ask me about tonight's props, sharp money, or parlays. What are you looking at?",
        },
    ]);
    const [loading, setLoading] = useState(false);

    const ask = useCallback(async (input: string, propsContext?: any) => {
        const userMessage: Message = { role: "user", content: input };
        const updated = [...messages, userMessage];
        setMessages(updated);
        setLoading(true);

        try {
            const res = await api.oracle({
                messages: updated,
                propsContext,
            });

            if (!isApiError(res)) {
                setMessages((prev) => [
                    ...prev,
                    { role: "assistant", content: res.message },
                ]);
            } else {
                throw new Error(res.message);
            }
        } catch {
            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: "Connection lost. Try again." },
            ]);
        } finally {
            setLoading(false);
        }
    }, [messages]);

    const reset = () =>
        setMessages([
            {
                role: "assistant",
                content: "Oracle online. Ask me about tonight's props, sharp money, or parlays. What are you looking at?",
            },
        ]);

    return { messages, loading, ask, reset };
}
