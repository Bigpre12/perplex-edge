"use client";

import { useEffect } from "react";

const RELOAD_FLAG = "lucrix_chunk_reload_v1";

/**
 * After a new Vercel deploy, old tabs keep a webpack runtime that references deleted
 * `/_next/static/chunks/*` hashes → ChunkLoadError / RSC fetch failures. One hard reload
 * pulls the new build manifest. Guarded so we only auto-reload once per tab session.
 */
export default function DeploymentChunkRecovery() {
  useEffect(() => {
    const match = (msg: string) =>
      /ChunkLoadError|Loading chunk \d+ failed|Failed to fetch dynamically imported module|Failed to fetch RSC payload/i.test(
        msg
      );

    const tryReload = () => {
      try {
        if (sessionStorage.getItem(RELOAD_FLAG)) return;
        sessionStorage.setItem(RELOAD_FLAG, "1");
      } catch {
        return;
      }
      window.location.reload();
    };

    const onError = (event: ErrorEvent) => {
      const msg = event.message || (event.error && String((event.error as Error).message)) || "";
      if (match(msg)) tryReload();
    };

    const onUnhandled = (event: PromiseRejectionEvent) => {
      const r = event.reason;
      const msg =
        typeof r === "object" && r !== null && "message" in r
          ? String((r as Error).message)
          : String(r);
      if (match(msg)) {
        event.preventDefault();
        tryReload();
      }
    };

    window.addEventListener("error", onError);
    window.addEventListener("unhandledrejection", onUnhandled);
    return () => {
      window.removeEventListener("error", onError);
      window.removeEventListener("unhandledrejection", onUnhandled);
    };
  }, []);

  return null;
}
