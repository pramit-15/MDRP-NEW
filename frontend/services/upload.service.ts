import { createAuthedApi } from "@/lib/api";
import type { PdfParseResponse } from "@/types";

// ─── Upload Service ───────────────────────────────────────────────────────────

export async function parsePdf(
  token: string,
  file: File,
  onProgress?: (percent: number) => void
): Promise<PdfParseResponse> {
  const api = createAuthedApi(token);

  const formData = new FormData();
  formData.append("file", file);

  const { data } = await api.post<PdfParseResponse>(
    "/api/v1/parse-pdf",
    formData,
    {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (evt) => {
        if (evt.total && onProgress) {
          onProgress(Math.round((evt.loaded * 100) / evt.total));
        }
      },
    }
  );

  return data;
}

export const MAX_PDF_SIZE_MB = 10;
export const MAX_PDF_SIZE_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024;

export function validatePdfFile(file: File): string | null {
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    return "Only PDF files are accepted.";
  }
  if (file.size === 0) {
    return "File is empty.";
  }
  if (file.size > MAX_PDF_SIZE_BYTES) {
    return `File size must be less than ${MAX_PDF_SIZE_MB}MB.`;
  }
  return null;
}
