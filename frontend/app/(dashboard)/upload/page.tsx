"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload, FileText, X, CheckCircle2, AlertCircle,
  Loader2, ArrowRight, RefreshCcw, Info, Sparkles,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { parsePdf, validatePdfFile } from "@/services/upload.service";
import { formatFieldName } from "@/lib/utils";
import type { PdfParseResponse } from "@/types";
import { toast } from "sonner";

type UploadState = "idle" | "uploading" | "success" | "error";

export default function UploadPage() {
  const { getToken } = useAuth();
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<PdfParseResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const selected = acceptedFiles[0];
      if (!selected) return;

      const validationError = validatePdfFile(selected);
      if (validationError) {
        toast.error(validationError);
        return;
      }

      setFile(selected);
      setUploadState("idle");
      setResult(null);
      setError(null);
      setProgress(0);
    },
    []
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  const handleUpload = async () => {
    if (!file) return;
    setUploadState("uploading");
    setProgress(0);
    setError(null);

    try {
      const token = await getToken();
      if (!token) throw new Error("Not authenticated");

      const data = await parsePdf(token, file, setProgress);
      setResult(data);
      setUploadState("success");
      toast.success(`Extracted ${data.count} fields using ${data.method === "gemini_ai" ? "AI" : "pattern matching"}`);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { error?: { message?: string } } } })
          ?.response?.data?.error?.message || "Failed to parse PDF";
      setError(message);
      setUploadState("error");
      toast.error(message);
    }
  };

  const handleReset = () => {
    setFile(null);
    setUploadState("idle");
    setResult(null);
    setError(null);
    setProgress(0);
  };

  const handleUsePdfData = () => {
    if (result?.extracted) {
      sessionStorage.setItem("pdf_prefill", JSON.stringify(result.extracted));
      router.push("/predictions/new?source=pdf");
    }
  };

  const extractedFields = result
    ? Object.entries(result.extracted).filter(([, v]) => v !== null && v !== undefined)
    : [];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Upload className="h-6 w-6 text-blue-600" />
          Upload Medical Report
        </h1>
        <p className="text-muted-foreground mt-1">
          Upload a PDF lab report to automatically extract health values for prediction.
        </p>
      </div>

      {/* Info Banner */}
      <div className="flex gap-3 p-4 rounded-xl bg-blue-600/5 border border-blue-200/50 dark:border-blue-800/30">
        <Info className="h-5 w-5 text-blue-600 shrink-0" />
        <div className="text-sm">
          <p className="font-medium text-blue-700 dark:text-blue-400">AI-Powered Extraction</p>
          <p className="text-muted-foreground mt-0.5">
            We use Google Gemini AI to intelligently extract lab values. Supports blood panels, metabolic reports, and more. Max 10MB PDF only.
          </p>
        </div>
      </div>

      {/* Drop Zone */}
      {uploadState !== "success" && (
        <div
          {...getRootProps()}
          className={`relative rounded-2xl border-2 border-dashed transition-all duration-200 cursor-pointer ${
            isDragActive
              ? "border-blue-500 bg-blue-500/5 scale-[1.01]"
              : file
              ? "border-emerald-400 bg-emerald-500/5"
              : "border-border hover:border-blue-400 hover:bg-muted/30"
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center justify-center py-16 text-center px-6">
            <AnimatePresence mode="wait">
              {file ? (
                <motion.div
                  key="file"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex flex-col items-center gap-3"
                >
                  <div className="h-16 w-16 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                    <FileText className="h-8 w-8 text-emerald-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-lg">{file.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {(file.size / 1024).toFixed(0)} KB · PDF
                    </p>
                  </div>
                  <Badge variant="success" className="mt-1">Ready to upload</Badge>
                </motion.div>
              ) : (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex flex-col items-center gap-3"
                >
                  <div className="h-16 w-16 rounded-2xl bg-muted flex items-center justify-center">
                    <Upload className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-lg font-semibold">
                      {isDragActive ? "Drop it here!" : "Drag & drop your PDF"}
                    </p>
                    <p className="text-muted-foreground text-sm mt-1">
                      or click to browse — PDF only, max 10MB
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Upload Progress */}
      {uploadState === "uploading" && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3 mb-4">
              <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
              <span className="font-medium">Extracting lab values...</span>
              <span className="ml-auto text-sm text-muted-foreground">{progress}%</span>
            </div>
            <Progress value={progress} className="h-2" />
            <p className="text-xs text-muted-foreground mt-3">
              {progress < 50 ? "Uploading PDF..." : "AI is parsing your report..."}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {uploadState === "error" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <Card className="border-red-200 dark:border-red-800">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-red-700 dark:text-red-400">Extraction Failed</p>
                  <p className="text-sm text-muted-foreground mt-1">{error}</p>
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-3"
                    onClick={handleUpload}
                  >
                    <RefreshCcw className="h-4 w-4 mr-1" />
                    Retry
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Success Results */}
      {uploadState === "success" && result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <Card className="border-emerald-200 dark:border-emerald-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                Extraction Complete
              </CardTitle>
              <CardDescription>
                {extractedFields.length} fields extracted via{" "}
                <Badge variant="outline" className="text-[10px]">
                  {result.method === "gemini_ai" ? (
                    <><Sparkles className="h-3 w-3 mr-1" />Gemini AI</>
                  ) : (
                    "Pattern Matching"
                  )}
                </Badge>
              </CardDescription>
            </CardHeader>
            <CardContent>
              {extractedFields.length === 0 ? (
                <p className="text-muted-foreground text-sm">No values could be extracted from this PDF.</p>
              ) : (
                <div className="grid sm:grid-cols-2 gap-2">
                  {extractedFields.map(([key, value]) => (
                    <div
                      key={key}
                      className="flex items-center justify-between p-3 rounded-lg bg-muted/30 border border-border/30"
                    >
                      <span className="text-sm text-muted-foreground">{formatFieldName(key)}</span>
                      <span className="text-sm font-semibold">
                        {typeof value === "number" ? (value % 1 === 0 ? value : value.toFixed(2)) : value}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={handleUsePdfData}
              className="flex-1 group"
              disabled={extractedFields.length === 0}
            >
              Use These Values for Prediction
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button variant="outline" onClick={handleReset}>
              Upload Another
            </Button>
          </div>
        </motion.div>
      )}

      {/* Action Buttons (pre-upload) */}
      {file && uploadState === "idle" && (
        <div className="flex gap-3">
          <Button onClick={handleUpload} className="flex-1">
            <Upload className="h-4 w-4 mr-2" />
            Extract Lab Values
          </Button>
          <Button variant="outline" onClick={handleReset}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
