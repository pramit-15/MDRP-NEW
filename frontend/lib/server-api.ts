import axios from "axios";
import { auth } from "@clerk/nextjs/server";

// Server-side axios instance (for Server Components / Route Handlers)
export const serverApi = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});
