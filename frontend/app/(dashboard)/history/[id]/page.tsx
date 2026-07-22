"use client";

import { useHistoryDetail } from "@/hooks/use-predictions";
import { PredictionResultView } from "@/features/prediction/prediction-result";
import { SkeletonCard } from "@/components/ui/skeleton";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function HistoryDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { data, isLoading, isError } = useHistoryDetail(params.id);

  if (isLoading) {
    return (
      <div className="space-y-6">
        {Array.from({ length: 3 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="h-16 w-16 rounded-2xl bg-red-500/10 flex items-center justify-center mb-4">
          <AlertTriangle className="h-8 w-8 text-red-500" />
        </div>
        <h2 className="text-xl font-bold mb-2">Prediction Not Found</h2>
        <p className="text-muted-foreground mb-6">
          This prediction may have been deleted or doesn&apos;t exist.
        </p>
        <Link href="/history">
          <Button>Back to History</Button>
        </Link>
      </div>
    );
  }

  return (
    <PredictionResultView
      result={{
        ...data,
        heart: data.heart_risk,
        diabetes: data.diabetes_risk,
        kidney: data.kidney_risk,
      }}
      backHref="/history"
    />
  );
}
