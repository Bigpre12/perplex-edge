"use client";
import { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';
import { API } from '../lib/api';

export function useReconnectingWs(endpoint: string, onMessage?: (data: any) => void) {
  const [data, setData] = useState<any>(null);
  const [status, setStatus] = useState<'connecting' | 'open' | 'closed'>('connecting');
  const ws = useRef<WebSocket | null>(null);
  const reconnectCount = useRef(0);

  const connect = () => {
    setStatus('connecting');
    const wsUrl = endpoint.startsWith('ws') ? endpoint : `${API.wsBaseUrl}${endpoint}`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log(`[WS] Connected to ${endpoint}`);
      setStatus('open');
      reconnectCount.current = 0;
    };

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        setData(payload);
        if (onMessage) onMessage(payload);
      } catch (e) {
        console.warn("[WS] Failed to parse message", event.data);
      }
    };

    socket.onclose = () => {
      setStatus('closed');
      const delay = Math.min(1000 * Math.pow(2, reconnectCount.current), 30000);
      reconnectCount.current += 1;
      console.log(`[WS] Connection closed. Retrying in ${delay / 1000}s...`);
      setTimeout(connect, delay);
    };

    socket.onerror = (err) => {
      console.error("[WS] Error", err);
      socket.close();
    };

    ws.current = socket;
  };

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [endpoint]);

  return { data, status };
}
