import { createAuthedApi } from "@/lib/api";
import type { PredictionInput, PredictionResponse, HistoryResponse, HistoryDetail } from "@/types";

// ─── Prediction Service ───────────────────────────────────────────────────────

export async function predict(
  token: string,
  input: PredictionInput
): Promise<PredictionResponse> {
  const api = createAuthedApi(token);
  const { data } = await api.post<PredictionResponse>("/api/v1/predict", input);
  return data;
}

export async function getHistory(
  token: string,
  params: { skip?: number; limit?: number } = {}
): Promise<HistoryResponse> {
  const api = createAuthedApi(token);
  const { data } = await api.get<HistoryResponse>("/api/v1/history", {
    params: { skip: params.skip ?? 0, limit: params.limit ?? 10 },
  });
  return data;
}

export async function getHistoryDetail(
  token: string,
  id: string
): Promise<HistoryDetail> {
  const api = createAuthedApi(token);
  const { data } = await api.get<HistoryDetail>(`/api/v1/history/${id}`);
  return data;
}

export async function deleteHistory(
  token: string,
  id: string
): Promise<{ success: boolean }> {
  const api = createAuthedApi(token);
  const { data } = await api.delete<{ success: boolean }>(`/api/v1/history/${id}`);
  return data;
}
