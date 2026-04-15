"use client";
import { useQuery } from "@tanstack/react-query";
import API from "@/lib/api";

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: API.me,
    staleTime: 5 * 60_000,
  });
}
