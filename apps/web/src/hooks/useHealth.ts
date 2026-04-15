"use client";
import { useQuery } from "@tanstack/react-query";
import API from "@/lib/api";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: API.health,
    refetchInterval: 30000,
  });
}

export function useMetaHealth() {
  return useQuery({
    queryKey: ["metaHealth"],
    queryFn: API.metaHealth,
    refetchInterval: 30000,
  });
}
