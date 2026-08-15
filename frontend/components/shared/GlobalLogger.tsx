"use client";

import { useEffect } from "react";
import { logger } from "@/lib/logger";

export function GlobalLogger() {
  useEffect(() => {
    const handleWindowError = (event: ErrorEvent) => {
      logger.error(event.error || event.message, {
        source: 'window.onerror',
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      });
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      logger.error(event.reason, {
        source: 'unhandledrejection',
      });
    };

    window.addEventListener("error", handleWindowError);
    window.addEventListener("unhandledrejection", handleUnhandledRejection);

    return () => {
      window.removeEventListener("error", handleWindowError);
      window.removeEventListener("unhandledrejection", handleUnhandledRejection);
    };
  }, []);

  return null; // This component doesn't render anything
}
