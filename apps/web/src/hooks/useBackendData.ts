"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { API_BASE } from "@/lib/api";

type QueryParams = Record<string, string | number | boolean | undefined | null>;

type UseBackendDataOptions = {
  params?: QueryParams;
  enabled?: boolean;
  requireAuth?: boolean;
  pollMs?: number;
  timeoutMs?: number;
  method?: "GET" | "POST";
  body?: unknown;
  headers?: Record<string, string>;
};

export type UseBackendDataResult<T> = {
  data: T | null;
  isLoading: boolean;
  isError: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  lastUpdated: string | null;
};

const RETRY_DELAYS_MS = [500, 1000, 2000];

function stableParamsKey(params?: QueryParams): string {
  if (!params) return "";
  const keys = Object.keys(params).sort();
  const normalized: Record<string, string | number | boolean | undefined | null> = {};
  for (const key of keys) normalized[key] = params[key];
  return JSON.stringify(normalized);
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function buildUrl(path: string, params?: QueryParams): string {
  const base = typeof window === "undefined" ? API_BASE : "/backend";
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${base}${normalizedPath}`, "http://local");
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value === undefined || value === null || value === "") return;
      url.searchParams.set(key, String(value));
    });
  }
  return `${url.pathname}${url.search}`;
}

async function fetchWithTimeout(input: RequestInfo, init: RequestInit, timeoutMs: number) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(input, { ...init, signal: controller.signal, cache: "no-store" });
    return response;
  } finally {
    clearTimeout(timeout);
  }
}

export function useBackendData<T = unknown>(
  path: string,
  options: UseBackendDataOptions = {},
): UseBackendDataResult<T> {
  const {
    params,
    enabled = true,
    requireAuth = false,
    pollMs,
    timeoutMs = 10000,
    method = "GET",
    body,
    headers,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(enabled);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const mountedRef = useRef(true);
  const hasLoadedRef = useRef(false);
  const paramsKey = useMemo(() => stableParamsKey(params), [params]);

  const requestUrl = useMemo(() => buildUrl(path, params), [path, paramsKey]);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const runFetch = useCallback(async () => {
    if (!enabled) return;
    setIsLoading(!hasLoadedRef.current);
    setIsError(false);
    setError(null);

    let lastErr: string | null = null;
    for (let attempt = 0; attempt < RETRY_DELAYS_MS.length + 1; attempt += 1) {
      try {
        const requestHeaders: Record<string, string> = {
          "Content-Type": "application/json",
          ...(headers || {}),
        };

        const token =
          typeof window !== "undefined"
            ? localStorage.getItem("access_token") || localStorage.getItem("accessToken")
            : null;
        if (token && !requestHeaders.Authorization) {
          requestHeaders.Authorization = `Bearer ${token}`;
        }

        const authRequiredPath = path.includes("/api/ev/top") || path.includes("/api/whale");
        const shouldRequireAuth = requireAuth || authRequiredPath;
        if (shouldRequireAuth && !token) {
          throw new Error("Authentication required for protected endpoint");
        }

        const response = await fetchWithTimeout(
          requestUrl,
          {
            method,
            headers: requestHeaders,
            body: body == null ? undefined : JSON.stringify(body),
          },
          timeoutMs,
        );

        if (!response.ok) {
          throw new Error(`Request failed (${response.status})`);
        }

        const json = (await response.json()) as T;
        if (!mountedRef.current) return;
        setData(json);
        setLastUpdated(new Date().toISOString());
        hasLoadedRef.current = true;
        setIsLoading(false);
        return;
      } catch (err) {
        lastErr = err instanceof Error ? err.message : "Unknown network error";
        if (attempt < RETRY_DELAYS_MS.length) {
          await sleep(RETRY_DELAYS_MS[attempt]);
          continue;
        }
      }
    }

    if (!mountedRef.current) return;
    setIsLoading(false);
    setIsError(true);
    setError(lastErr || "Failed to fetch data");
  }, [enabled, requestUrl, method, headers, body, timeoutMs, path, requireAuth]);

  useEffect(() => {
    if (!enabled) return;
    runFetch();
  }, [runFetch, enabled]);

  useEffect(() => {
    if (!enabled || !pollMs) return;
    const id = setInterval(() => {
      runFetch();
    }, pollMs);
    return () => clearInterval(id);
  }, [enabled, pollMs, runFetch]);

  return {
    data,
    isLoading,
    isError,
    error,
    refetch: runFetch,
    lastUpdated,
  };
}
