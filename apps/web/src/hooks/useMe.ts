"use client";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: api.me,
    staleTime: 5 * 60_000,
  });
}
