"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { useHealthMonitor } from "@/hooks/useHealthMonitor";

export function Providers({ children }: { children: React.ReactNode }) {
    const [queryClient] = useState(() => new QueryClient({
        defaultOptions: {
            queries: {
                staleTime: 60000, // 1 min
                gcTime: 300000, // 5 min
                refetchOnWindowFocus: false,
                refetchOnMount: false,
                retry: i => i < 2,
            },
        },
    }));
    useHealthMonitor();

    return (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    );
}
