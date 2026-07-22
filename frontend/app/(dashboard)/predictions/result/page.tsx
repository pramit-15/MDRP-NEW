"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { PredictionResultView } from "@/features/prediction/prediction-result";
import type { PredictionResponse } from "@/types";
import { Loader2 } from "lucide-react";

export default function PredictionResultPage() {
  const router = useRouter();
  const [result, setResult] = useState<PredictionResponse | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("latest_prediction");
    if (stored) {
      try {
        setResult(JSON.parse(stored));
      } catch {
        router.push("/predictions/new");
      }
    } else {
      router.push("/predictions/new");
    }
  }, [router]);

  if (!result) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <PredictionResultView
      result={result}
      backHref="/predictions/new"
    />
  );
}
