import axios from "axios";
import type { HealthCheckResponse } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export async function checkHealth(): Promise<HealthCheckResponse> {
  const { data } = await axios.get<HealthCheckResponse>(`${API_URL}/api/v1/health`, {
    timeout: 5000,
  });
  return data;
}
