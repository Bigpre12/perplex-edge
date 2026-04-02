"use client";

import { useState } from "react";

export interface OracleRequest {
  player: string;
  market: string;
  context: string;
  sport: string;
}

export const useOracle = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [lastFullText, setLastFullText] = useState("");
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (req: OracleRequest) => {
    setIsStreaming(true);
    setStreamingText("");
    setError(null);
    
    try {
      const response = await fetch("/api/oracle/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          messages: [{ role: "user", content: req.context || `${req.player} - ${req.market}` }],
          sport: req.sport || "basketball_nba" 
        }),
      });

      if (!response.ok) throw new Error("Oracle is temporarily offline.");

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let fullText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split("\n\n").filter(Boolean);
        
        for (const line of lines) {
          const data = line.replace("data: ", "");
          if (data === "[DONE]") {
            setIsStreaming(false);
            setLastFullText(fullText);
            break;
          }
          fullText += data;
          setStreamingText(fullText);
        }
      }
    } catch (err: any) {
      setError(err.message || "Quantum synchronization failure.");
      setIsStreaming(false);
    }
  };

  return {
    sendMessage,
    isStreaming,
    streamingText,
    lastFullText,
    error,
    isPending: isStreaming, // backwards compatibility
  };
};
