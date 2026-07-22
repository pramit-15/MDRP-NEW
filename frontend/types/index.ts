// ─── Prediction Types ────────────────────────────────────────────────────────

export interface PredictionInput {
  // Basic
  age?: number;
  sex?: number; // 0 = female, 1 = male
  preg?: number; // pregnancies
  height_cm?: number;
  weight_kg?: number;
  bmi?: number;

  // Vitals
  systolic_bp?: number;
  diastolic_bp?: number;
  thalach?: number; // max heart rate
  trestbps?: number; // resting BP (systolic)

  // Blood sugar
  glucose?: number; // fasting
  bgr?: number; // post-prandial / random
  hba1c?: number;
  insulin?: number;

  // Lipids
  chol?: number;
  ldl?: number;
  hdl?: number;
  triglycerides?: number;

  // Kidney markers
  sc?: number; // serum creatinine
  bu?: number; // blood urea
  sod?: number; // sodium
  pot?: number; // potassium
  egfr?: number;

  // Binary clinical flags
  htn?: number; // hypertension (0/1)
  dm?: number; // diabetes (0/1)
  cad?: number; // coronary artery disease (0/1)
  appet?: number; // appetite (0=poor, 1=good)
  pe?: number; // pedal edema (0/1)
  ane?: number; // anemia (0/1)

  // Heart-specific
  cp?: number; // chest pain type
  fbs?: number; // fasting blood sugar > 120
  restecg?: number;
  exang?: number;
  oldpeak?: number;
  slope?: number;
  ca?: number;
  thal?: number;

  // Patient info (non-model, for display)
  patient_id?: string;
  patient_name?: string;
}

export interface ScoreDetail {
  ml: number;
  clinical: number;
}

export interface PredictionResponse {
  success: boolean;
  heart: number;
  diabetes: number;
  kidney: number;
  bmi_used?: number;
  scores_detail: {
    heart: ScoreDetail;
    diabetes: ScoreDetail;
    kidney: ScoreDetail;
  };
  health_condition: Record<string, number>;
  used_defaults: string[];
  prediction_id?: string;
}

// ─── History Types ────────────────────────────────────────────────────────────

export interface HistoryItem {
  id: string;
  heart_risk: number;
  diabetes_risk: number;
  kidney_risk: number;
  health_condition: Record<string, number>;
  created_at: string;
}

export interface HistoryDetail extends HistoryItem {
  scores_detail: {
    heart: ScoreDetail;
    diabetes: ScoreDetail;
    kidney: ScoreDetail;
  };
  clinical_scores: {
    heart_clinical: number;
    diabetes_clinical: number;
    kidney_clinical: number;
  };
  inputs_used: PredictionInput;
  used_defaults: string[];
}

export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
  skip: number;
  limit: number;
}

// ─── PDF Upload Types ─────────────────────────────────────────────────────────

export interface ParsedPdfFields {
  age?: number | null;
  systolic_bp?: number | null;
  diastolic_bp?: number | null;
  glucose?: number | null;
  bgr?: number | null;
  hba1c?: number | null;
  insulin?: number | null;
  chol?: number | null;
  ldl?: number | null;
  hdl?: number | null;
  triglycerides?: number | null;
  sc?: number | null;
  bu?: number | null;
  sod?: number | null;
  pot?: number | null;
  egfr?: number | null;
  htn?: 0 | 1 | null;
  dm?: 0 | 1 | null;
  cad?: 0 | 1 | null;
  appet?: 0 | 1 | null;
  pe?: 0 | 1 | null;
  ane?: 0 | 1 | null;
}

export interface PdfParseResponse {
  success: boolean;
  extracted: ParsedPdfFields;
  count: number;
  all_fields: string[];
  method: "gemini_ai" | "regex";
}

// ─── Health Check ─────────────────────────────────────────────────────────────

export interface HealthCheckResponse {
  status: "healthy" | "unhealthy";
  models_loaded: boolean;
  version: string;
  uptime: number;
}

// ─── Risk Level Helpers ───────────────────────────────────────────────────────

export type RiskLevel = "low" | "moderate" | "high" | "critical";

export function getRiskLevel(score: number): RiskLevel {
  if (score < 20) return "low";
  if (score < 40) return "moderate";
  if (score < 65) return "high";
  return "critical";
}

export function getRiskColor(level: RiskLevel): string {
  switch (level) {
    case "low": return "text-emerald-500";
    case "moderate": return "text-amber-500";
    case "high": return "text-orange-500";
    case "critical": return "text-red-500";
  }
}

export function getRiskBgColor(level: RiskLevel): string {
  switch (level) {
    case "low": return "bg-emerald-500/10 text-emerald-600 border-emerald-200 dark:border-emerald-800 dark:text-emerald-400";
    case "moderate": return "bg-amber-500/10 text-amber-600 border-amber-200 dark:border-amber-800 dark:text-amber-400";
    case "high": return "bg-orange-500/10 text-orange-600 border-orange-200 dark:border-orange-800 dark:text-orange-400";
    case "critical": return "bg-red-500/10 text-red-600 border-red-200 dark:border-red-800 dark:text-red-400";
  }
}

export function getRiskLabel(level: RiskLevel): string {
  switch (level) {
    case "low": return "Low Risk";
    case "moderate": return "Moderate Risk";
    case "high": return "High Risk";
    case "critical": return "Critical Risk";
  }
}
