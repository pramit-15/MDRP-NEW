"use client";

import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

// Client-side axios instance — unauthenticated, used for public endpoints
export const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// Helper: create an api instance with a pre-attached Bearer token
export function createAuthedApi(token: string) {
  const authed = axios.create({
    baseURL: API_URL,
    timeout: 30000,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  authed.interceptors.response.use(
    (response) => response,
    (error) => {
      // On 401, throw the error so the caller can handle it gracefully.
      // Do NOT force a redirect here — that causes infinite reload loops
      // when the auth service is temporarily unavailable.
      return Promise.reject(error);
    }
  );

  return authed;
}

export default api;
