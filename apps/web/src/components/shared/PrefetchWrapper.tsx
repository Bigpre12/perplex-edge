"use client";

import { usePrefetchAllTabs } from "@/hooks/usePrefetchAllTabs";

/**
 * PrefetchWrapper - A client component that simply runs the prefetching hook.
 * This allows us to use hooks in a server component layout.
 */
export default function PrefetchWrapper() {
    usePrefetchAllTabs();
    return null;
}
