import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    refetchInterval: 30000,
  });
}

export function useMetaHealth() {
  return useQuery({
    queryKey: ["metaHealth"],
    queryFn: api.metaHealth,
    refetchInterval: 30000,
  });
}
