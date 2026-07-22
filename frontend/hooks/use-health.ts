"use client";

import { useQuery } from "@tanstack/react-query";
import { checkHealth } from "@/services/health.service";

export function useHealthCheck() {
  return useQuery({
    queryKey: ["health"],
    queryFn: checkHealth,
    refetchInterval: 30000, // check every 30 seconds
    retry: 1,
  });
}
