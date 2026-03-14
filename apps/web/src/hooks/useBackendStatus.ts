"use client";

import { useLucrixStore } from "@/store";

export function useBackendStatus() {
    const { backendOnline, setBackendOnline } = useLucrixStore();

    return {
        isDown: !backendOnline,
        recordFailure: () => setBackendOnline(false),
        recordSuccess: () => setBackendOnline(true)
    };
}
