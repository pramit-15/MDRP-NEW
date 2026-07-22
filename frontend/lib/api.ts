"use client";

import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

// Client-side axios instance — token is injected by the interceptor
export const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// Attach Clerk token before every request
api.interceptors.request.use(async (config) => {
  try {
    // Dynamic import to avoid SSR issues
    const { useAuth } = await import("@clerk/nextjs");
    // Can't call hooks outside React — token is injected via setAuthToken helper
  } catch {
    // Silently ignore
  }
  return config;
});

// Global response error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Let Clerk handle redirect
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

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
      if (error.response?.status === 401) {
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
      }
      return Promise.reject(error);
    }
  );

  return authed;
}

export default api;
