"use client";

import { useAuth } from "@clerk/nextjs";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import * as predictionService from "@/services/prediction.service";
import type { PredictionInput } from "@/types";

// ─── History Hooks ────────────────────────────────────────────────────────────

export function useHistory(params: { skip?: number; limit?: number } = {}) {
  const { getToken } = useAuth();

  return useQuery({
    queryKey: ["history", params],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return predictionService.getHistory(token, params);
    },
  });
}

export function useHistoryDetail(id: string | null) {
  const { getToken } = useAuth();

  return useQuery({
    queryKey: ["history", id],
    enabled: !!id,
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return predictionService.getHistoryDetail(token, id!);
    },
  });
}

export function useDeleteHistory() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return predictionService.deleteHistory(token, id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["history"] });
      toast.success("Prediction deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete prediction");
    },
  });
}

// ─── Prediction Hooks ─────────────────────────────────────────────────────────

export function usePredictMutation() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: PredictionInput) => {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");
      return predictionService.predict(token, input);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["history"] });
    },
    onError: (error: unknown) => {
      const message =
        (error as { response?: { data?: { error?: { message?: string } } } })
          ?.response?.data?.error?.message || "Prediction failed. Please try again.";
      toast.error(message);
    },
  });
}
