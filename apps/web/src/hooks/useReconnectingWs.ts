// apps/web/src/hooks/useReconnectingWs.ts
import { useEffect, useRef, useState } from "react";

type Status = "CONNECTING" | "OPEN" | "RECONNECTING" | "CLOSED";

export function useReconnectingWs(url: string, onMessage: (data: any) => void) {
  const [status, setStatus] = useState<Status>("CONNECTING");
  const wsRef = useRef<WebSocket | null>(null);
  const retries = useRef(0);

  useEffect(() => {
    let cancelled = false;

    function connect() {
      // Handle protocol for local vs prod
      const wsUrl = url.startsWith('ws') ? url : `ws://${window.location.host}${url}`;
      
      setStatus(retries.current === 0 ? "CONNECTING" : "RECONNECTING");
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        if (cancelled) return;
        retries.current = 0;
        setStatus("OPEN");
        console.log("WS Connected:", wsUrl);
      };

      ws.onmessage = (evt) => {
        if (cancelled) return;
        try {
          onMessage(JSON.parse(evt.data));
        } catch (e) {
          console.error("WS Parse Error:", e);
        }
      };

      ws.onclose = () => {
        if (cancelled) return;
        retries.current += 1;
        if (retries.current > 10) {
          setStatus("CLOSED");
          return;
        }
        const delay = Math.min(30_000, 1000 * 2 ** retries.current);
        console.log(`WS Disconnected. Retrying in ${delay}ms...`);
        setTimeout(connect, delay);
      };

      ws.onerror = (err) => {
        console.error("WS Error:", err);
        ws.close();
      };
    }

    connect();
    return () => {
      cancelled = true;
      wsRef.current?.close();
    };
  }, [url, onMessage]);

  return status;
}
