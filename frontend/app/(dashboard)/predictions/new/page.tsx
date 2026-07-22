"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { PlusCircle, FileText, Loader2 } from "lucide-react";
import { PredictionForm } from "@/features/prediction/prediction-form";
import type { ParsedPdfFields } from "@/types";
import { Badge } from "@/components/ui/badge";

function PredictionPageContent() {
  const searchParams = useSearchParams();
  const source = searchParams.get("source");
  const [prefillData, setPrefillData] = useState<ParsedPdfFields | null>(null);

  useEffect(() => {
    if (source === "pdf") {
      const stored = sessionStorage.getItem("pdf_prefill");
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          setPrefillData(parsed);
          sessionStorage.removeItem("pdf_prefill");
        } catch {
          // Ignore
        }
      }
    }
  }, [source]);

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-1 flex-wrap">
          <PlusCircle className="h-5 w-5 text-blue-600" />
          <h1 className="text-2xl font-bold tracking-tight">New Risk Prediction</h1>
          {prefillData && (
            <Badge variant="success" className="flex items-center gap-1">
              <FileText className="h-3 w-3" />
              Pre-filled from PDF
            </Badge>
          )}
        </div>
        <p className="text-muted-foreground">
          {prefillData
            ? "Lab values have been pre-filled from your uploaded PDF. Review and adjust as needed."
            : "Enter your health data below. All fields are optional — more data means more accurate predictions."}
        </p>
      </div>
      <PredictionForm prefillData={prefillData ?? undefined} />
    </div>
  );
}

export default function NewPredictionPage() {
  return (
    <Suspense 
      fallback={
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      }
    >
      <PredictionPageContent />
    </Suspense>
  );
}
